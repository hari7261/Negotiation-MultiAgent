import google.generativeai as genai
import random
import json
import re

class BuyerAgent:
    def __init__(self, model, max_price):
        self.model = model
        self.max_price = max_price
        self.target_price = max_price * 0.8  # Initial target is 20% below max
        self.rounds_count = 0
        self.negotiation_strategy = "conservative"  # Start conservative, get more aggressive
    
    def make_initial_offer(self, item):
        # Start at around 70-80% of max price
        initial_offer_price = self.max_price * random.uniform(0.70, 0.80)
        
        prompt = f"""You are a buyer interested in purchasing a {item}. Your maximum budget is ${self.max_price:.2f}, but you want to negotiate a good deal.

Generate a realistic opening offer message for ${initial_offer_price:.2f}. Make it:
- Polite and professional
- Show genuine interest
- Include research/comparison references to justify the price
- Mention specific details about the item if relevant
- Sound natural and conversational

Example style: "Hello! I'm interested in your {item}. Based on my research and similar items I've seen, would you consider $X as a starting point?"

Return ONLY a valid JSON response with 'message' and 'price' keys.
Example: {{"message": "Hello! I'm interested in your {item}...", "price": {initial_offer_price:.2f}}}"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                offer = json.loads(json_match.group())
                offer['price'] = initial_offer_price
                return offer
        except Exception as e:
            print(f"Error generating initial offer: {e}")
        
        # Fallback response
        return {
            'message': f"Hello! I'm interested in your {item}. Based on my research and similar items I've seen in the area, would you consider ${initial_offer_price:.2f} as a starting point?",
            'price': initial_offer_price
        }
    
    def respond_to_offer(self, item, last_price, last_message):
        self.rounds_count += 1
        
        # NEVER accept prices above maximum budget
        if last_price > self.max_price:
            # If seller's price is above budget, make a firm counter or walk away
            if self.rounds_count >= 3:
                return {
                    'message': f"I appreciate your time, but ${last_price:.2f} exceeds my maximum budget of ${self.max_price:.2f}. I'll have to look elsewhere unless you can work within my budget.",
                    'price': self.max_price * 0.95
                }
        
        # Check if price is acceptable (within budget and reasonable)
        if last_price <= self.max_price and last_price <= self.max_price * 0.95:
            # Accept if it's a good deal (within 95% of max)
            prompt = f"""You are a buyer who has been negotiating for a {item}. The seller's offer of ${last_price:.2f} is within your budget of ${self.max_price:.2f}.

Generate an acceptance message that:
- Expresses satisfaction with the deal
- Shows eagerness to finalize
- Maintains professional tone
- Mentions moving forward with paperwork/next steps

Return ONLY a valid JSON response with 'message' and 'price' keys.
Example: {{"message": "That works for me! I'm happy to proceed...", "price": {last_price}}}"""
            
            try:
                response = self.model.generate_content(prompt)
                text = response.text
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    acceptance = json.loads(json_match.group())
                    acceptance['price'] = last_price
                    return acceptance
            except Exception as e:
                print(f"Error generating acceptance: {e}")
            
            return {
                'message': f"${last_price:.2f} works for me! I'm happy to proceed today. Shall we move forward with the paperwork?",
                'price': last_price
            }
        
        # Calculate strategic counter-offer (NEVER exceed max budget)
        if self.rounds_count == 1:
            # First counter - modest increase but stay under budget
            new_price = min(last_price * 1.1, self.max_price * 0.9)
        elif self.rounds_count == 2:
            # Second counter - bigger move but respect budget
            new_price = min((last_price + self.max_price * 0.9) / 2, self.max_price * 0.95)
        else:
            # Later rounds - smaller increments, approach max budget carefully
            new_price = min(last_price * 1.03, self.max_price * 0.98)
        
        # Absolute safety check - NEVER exceed budget
        new_price = min(new_price, self.max_price * 0.99)
        
        prompt = f"""You are a buyer negotiating for a {item}. Your maximum budget is ${self.max_price:.2f}.
        
The seller's last offer was ${last_price:.2f} with message: "{last_message}"
You want to counter with ${new_price:.2f}.

Generate a realistic counter-offer message that:
- Acknowledges their offer respectfully
- Explains your position (budget constraints, market research, etc.)
- Proposes your counter-offer with justification
- Keeps negotiation moving forward
- Sounds natural and conversational

Return ONLY a valid JSON response with 'message' and 'price' keys.
Example: {{"message": "I appreciate the information. While I understand...", "price": {new_price:.2f}}}"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                counter = json.loads(json_match.group())
                counter['price'] = new_price
                return counter
        except Exception as e:
            print(f"Error generating buyer response: {e}")
        
        # Fallback response
        return {
            'message': f"I appreciate the information. While I understand the value, ${last_price:.2f} is above my budget. Could we meet at ${new_price:.2f}? This reflects similar items I've seen in the area.",
            'price': new_price
        }

class SellerAgent:
    def __init__(self, model, min_price):
        self.model = model
        self.min_price = min_price
        self.target_price = min_price * 1.2  # Initial target is 20% above min
        self.rounds_count = 0
        self.negotiation_strategy = "firm"  # Start firm, become more flexible
    
    def respond_to_offer(self, item, last_price, last_message):
        self.rounds_count += 1
        
        # NEVER accept prices below minimum
        if last_price < self.min_price:
            if self.rounds_count >= 3:
                return {
                    'message': f"I understand you're working within a budget, but ${last_price:.2f} is below my minimum of ${self.min_price:.2f}. I'm afraid I can't go any lower than that.",
                    'price': self.min_price
                }
        
        # Check if offer is acceptable (at or above minimum)
        if last_price >= self.min_price:
            # Accept if it meets minimum requirement
            prompt = f"""You are a seller who has been negotiating for a {item}. The buyer's offer of ${last_price:.2f} meets your minimum price requirement of ${self.min_price:.2f}.

Generate an acceptance message that:
- Shows satisfaction with reaching a deal
- Thanks the buyer
- Expresses readiness to finalize
- Maintains professional tone

Return ONLY a valid JSON response with 'message' and 'price' keys.
Example: {{"message": "I accept your offer! It's a deal...", "price": {last_price}}}"""
            
            try:
                response = self.model.generate_content(prompt)
                text = response.text
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    acceptance = json.loads(json_match.group())
                    acceptance['price'] = last_price
                    return acceptance
            except Exception as e:
                print(f"Error generating seller acceptance: {e}")
            
            return {
                'message': f"I accept your offer of ${last_price:.2f} for the {item}. It's a deal! Let's proceed with the paperwork.",
                'price': last_price
            }
        
        # Calculate strategic counter-offer (NEVER go below minimum)
        if self.rounds_count == 1:
            # First response - start high but reasonable (105-110% of min)
            new_price = self.min_price * random.uniform(1.05, 1.10)
        elif self.rounds_count == 2:
            # Second response - make a meaningful concession but stay above min
            new_price = max(self.min_price * 1.02, (last_price + self.min_price * 1.05) / 2)
        else:
            # Later rounds - smaller concessions, approach minimum carefully
            new_price = max(self.min_price * 1.01, last_price * 0.98)
        
        # Absolute safety check - NEVER go below minimum
        new_price = max(new_price, self.min_price * 1.001)
        
        prompt = f"""You are a seller negotiating for a {item}. Your minimum acceptable price is ${self.min_price:.2f}.
        
The buyer's last offer was ${last_price:.2f} with message: "{last_message}"
You want to counter with ${new_price:.2f}.

Generate a realistic counter-offer message that:
- Thanks them for their interest
- Explains why their offer is too low (condition, features, market value)
- Proposes your counter-offer with justification
- Shows willingness to negotiate but firmness on value
- Sounds natural and professional

Return ONLY a valid JSON response with 'message' and 'price' keys.
Example: {{"message": "Thank you for your interest. While I appreciate the offer...", "price": {new_price:.2f}}}"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                counter = json.loads(json_match.group())
                counter['price'] = new_price
                return counter
        except Exception as e:
            print(f"Error generating seller response: {e}")
        
        # Fallback response
        reason = "excellent condition and low mileage" if self.rounds_count == 1 else "its quality and market value"
        return {
            'message': f"Thank you for your interest. ${last_price:.2f} is quite low for this {item} given its {reason}. The lowest I could go would be ${new_price:.2f}.",
            'price': new_price
        }

class MediatorAgent:
    def __init__(self, model):
        self.model = model
    
    def intervene(self, item, prices, messages):
        if len(prices) < 3:
            return None  # Don't intervene too early
            
        # Analyze the negotiation pattern
        last_two_prices = prices[-2:]
        price_gap = abs(last_two_prices[0] - last_two_prices[1])
        avg_price = sum(last_two_prices) / 2
        
        # Only intervene if there's still a significant gap and negotiation seems stalled
        if price_gap < (avg_price * 0.05):  # If gap is less than 5%, no need to intervene
            return None
            
        prompt = f"""You are a professional mediator facilitating a negotiation for a {item}.

Current situation:
- Recent offers: ${last_two_prices[0]:.2f} and ${last_two_prices[1]:.2f}
- Price gap: ${price_gap:.2f}
- Conversation context: {' | '.join(messages[-2:])}

Generate a helpful mediation message that:
- Acknowledges the progress made so far
- Points out how close they are to a deal
- Suggests a fair compromise price around ${avg_price:.2f}
- Encourages both parties to make a final push
- Maintains neutral, professional tone
- Helps bridge the remaining gap

Return ONLY a valid JSON response with 'message' and 'price' keys.
Example: {{"message": "I've been following your negotiation. You've made good progress...", "price": {avg_price:.2f}}}"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                mediation = json.loads(json_match.group())
                mediation['price'] = avg_price
                return mediation
        except Exception as e:
            print(f"Error generating mediator response: {e}")
        
        # Fallback response
        progress_msg = f"the buyer started at ${prices[0]:.2f} and the seller came down from their initial position"
        return {
            'message': f"I've been following your negotiation. You've made good progress - {progress_msg}. Perhaps we can find middle ground around ${avg_price:.2f}? You're very close to a deal.",
            'price': avg_price
        }