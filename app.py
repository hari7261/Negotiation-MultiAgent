from flask import Flask, render_template, request, jsonify, make_response
from agents import BuyerAgent, SellerAgent, MediatorAgent
from database import init_db, save_negotiation, get_negotiation_history
import os
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['DATABASE'] = 'negotiations.db'

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable not set!")
    print("Please set your Gemini API key:")
    print("Set GEMINI_API_KEY=your_api_key_here")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("✅ Gemini API configured successfully")
except Exception as e:
    print(f"❌ Failed to configure Gemini API: {e}")
    exit(1)

# Initialize database
init_db(app.config['DATABASE'])

@app.route('/')
def index():
    history = get_negotiation_history(app.config['DATABASE'])
    return render_template('index.html', history=history)

@app.route('/start_auto_negotiation', methods=['POST'])
def start_auto_negotiation():
    try:
        print("Starting auto negotiation...")
        data = request.json
        print(f"Request data: {data}")
        
        item = data['item']
        buyer_max = float(data['buyer_max'])
        seller_min = float(data['seller_min'])
        
        print(f"Item: {item}, Buyer Max: {buyer_max}, Seller Min: {seller_min}")
        
        # Validate that negotiation is possible
        if seller_min > buyer_max:
            return jsonify({
                'error': f'Negotiation impossible: Seller minimum (${seller_min:.2f}) exceeds buyer maximum (${buyer_max:.2f})'
            }), 400
        
        # Run automatic negotiation
        print("Running negotiation...")
        negotiation_result = run_automatic_negotiation(item, buyer_max, seller_min)
        print("Negotiation completed successfully")
        
        return jsonify(negotiation_result)
    except Exception as e:
        print(f"Error starting auto negotiation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def run_automatic_negotiation(item, buyer_max, seller_min):
    """Run a complete automatic negotiation with minimum 6 rounds"""
    print("Initializing agents...")
    buyer = BuyerAgent(model, max_price=buyer_max)
    seller = SellerAgent(model, min_price=seller_min)
    mediator = MediatorAgent(model)
    
    negotiation = {
        'item': item,
        'buyer_max': buyer_max,
        'seller_min': seller_min,
        'rounds': [],
        'status': 'ongoing'
    }
    
    print("Starting negotiation rounds...")
    # Round 1: Buyer's initial offer
    buyer_offer = buyer.make_initial_offer(item)
    print(f"Buyer initial offer: {buyer_offer}")
    negotiation['rounds'].append({
        'round': 1,
        'agent': 'buyer',
        'message': buyer_offer['message'],
        'price': buyer_offer['price']
    })
    
    # Continue negotiation for at least 6 rounds
    round_count = 1
    while round_count < 6 or negotiation['status'] == 'ongoing':
        round_count += 1
        last_round = negotiation['rounds'][-1]
        
        # Determine whose turn it is
        if last_round['agent'] == 'buyer':
            response = seller.respond_to_offer(item, last_round['price'], last_round['message'])
            agent = 'seller'
        elif last_round['agent'] == 'seller':
            response = buyer.respond_to_offer(item, last_round['price'], last_round['message'])
            agent = 'buyer'
        else:  # mediator just spoke
            # Continue with whoever didn't speak last before mediator
            prev_agent = None
            for i in range(len(negotiation['rounds']) - 2, -1, -1):
                if negotiation['rounds'][i]['agent'] != 'mediator':
                    prev_agent = negotiation['rounds'][i]['agent']
                    break
            
            if prev_agent == 'buyer':
                response = seller.respond_to_offer(item, last_round['price'], last_round['message'])
                agent = 'seller'
            else:
                response = buyer.respond_to_offer(item, last_round['price'], last_round['message'])
                agent = 'buyer'
        
        print(f"Round {round_count} - {agent}: {response}")
        
        # Add mediator intervention periodically
        if round_count == 4 or (round_count > 6 and round_count % 3 == 0):
            mediation = mediator.intervene(
                item,
                [r['price'] for r in negotiation['rounds'] if r.get('price')],
                [r['message'] for r in negotiation['rounds']]
            )
            if mediation:
                negotiation['rounds'].append({
                    'round': round_count,
                    'agent': 'mediator',
                    'message': mediation['message'],
                    'price': mediation.get('price')
                })
                round_count += 1
        
        # Add the main response
        negotiation['rounds'].append({
            'round': round_count,
            'agent': agent,
            'message': response['message'],
            'price': response['price']
        })
        
        # Check for agreement after minimum rounds
        if round_count >= 6:
            # Check for explicit acceptance
            acceptance_keywords = ['accept', 'deal', 'agreed', 'proceed', 'paperwork', 'finalize']
            if any(keyword in response['message'].lower() for keyword in acceptance_keywords):
                if seller_min <= response['price'] <= buyer_max:
                    negotiation['status'] = 'agreed'
                    negotiation['final_price'] = response['price']
                    break
            
            # Check if prices are converging
            if len(negotiation['rounds']) >= 2:
                last_two_prices = [negotiation['rounds'][-1]['price'], negotiation['rounds'][-2]['price']]
                if abs(last_two_prices[0] - last_two_prices[1]) < 10:  # Within $10
                    avg_price = sum(last_two_prices) / 2
                    if seller_min <= avg_price <= buyer_max:
                        negotiation['status'] = 'agreed'
                        negotiation['final_price'] = avg_price
                        break
        
        # Prevent infinite loops
        if round_count >= 12:
            negotiation['status'] = 'failed'
            negotiation['reason'] = 'Maximum rounds reached without agreement'
            break
    
    # Generate AI summary and analysis
    negotiation['summary'] = generate_negotiation_summary(negotiation)
    negotiation['analysis'] = generate_negotiation_analysis(negotiation)
    
    # Save to database if successful
    if negotiation['status'] == 'agreed':
        save_negotiation(
            app.config['DATABASE'],
            negotiation['item'],
            negotiation['buyer_max'],
            negotiation['seller_min'],
            negotiation['final_price'],
            "\n".join([f"Round {r['round']} - {r['agent'].title()}: {r['message']}" for r in negotiation['rounds']])
        )
        print("Negotiation saved to database")
    
    return negotiation

def generate_negotiation_summary(negotiation):
    """Generate AI-powered negotiation summary"""
    try:
        rounds_text = "\n".join([f"Round {r['round']} - {r['agent'].title()}: {r['message']} (${r['price']:.2f})" for r in negotiation['rounds']])
        
        prompt = f"""Generate a professional negotiation summary for the following negotiation:

Item: {negotiation['item']}
Buyer Maximum: ${negotiation['buyer_max']:.2f}
Seller Minimum: ${negotiation['seller_min']:.2f}
Status: {negotiation['status']}
Final Price: ${negotiation.get('final_price', 0):.2f}

Negotiation Rounds:
{rounds_text}

Create a concise summary (150-200 words) that includes:
- Overview of the negotiation
- Key turning points
- Final outcome
- Professional tone suitable for a business report"""

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Summary generation failed: {str(e)}"

def generate_negotiation_analysis(negotiation):
    """Generate AI-powered negotiation analysis"""
    try:
        prices = [r['price'] for r in negotiation['rounds'] if r['price']]
        
        prompt = f"""Analyze this negotiation and provide strategic insights:

Item: {negotiation['item']}
Buyer Maximum: ${negotiation['buyer_max']:.2f}
Seller Minimum: ${negotiation['seller_min']:.2f}
Price Range: ${min(prices):.2f} - ${max(prices):.2f}
Total Rounds: {len(negotiation['rounds'])}
Outcome: {negotiation['status']}

Provide analysis covering:
1. Negotiation strategy effectiveness
2. Price movement patterns
3. Agent behavior assessment
4. Key success/failure factors
5. Recommendations for future negotiations

Keep it professional and analytical (200-250 words)."""

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Analysis generation failed: {str(e)}"

@app.route('/continue_negotiation', methods=['POST'])
def continue_negotiation():
    data = request.json
    negotiation = data['negotiation']
    last_round = negotiation['rounds'][-1]
    
    buyer = BuyerAgent(model, max_price=negotiation['buyer_max'])
    seller = SellerAgent(model, min_price=negotiation['seller_min'])
    mediator = MediatorAgent(model)
    
    if last_round['agent'] == 'buyer':
        # Seller's turn to respond
        response = seller.respond_to_offer(
            negotiation['item'],
            last_round['price'],
            last_round['message']
        )
        agent = 'seller'
    else:
        # Buyer's turn to respond
        response = buyer.respond_to_offer(
            negotiation['item'],
            last_round['price'],
            last_round['message']
        )
        agent = 'buyer'
    
    # Check if mediator should intervene
    if len(negotiation['rounds']) >= 4 and len(negotiation['rounds']) % 2 == 0:  # After every 2 rounds starting from round 4
        mediation = mediator.intervene(
            negotiation['item'],
            [r['price'] for r in negotiation['rounds']],
            [r['message'] for r in negotiation['rounds']]
        )
        if mediation:
            negotiation['rounds'].append({
                'agent': 'mediator',
                'message': mediation['message'],
                'price': mediation.get('price')
            })
    
    negotiation['rounds'].append({
        'agent': agent,
        'message': response['message'],
        'price': response['price']
    })
    
    # Check for agreement - look for acceptance keywords or very close prices
    if len(negotiation['rounds']) >= 2:
        last_round = negotiation['rounds'][-1]
        prev_round = negotiation['rounds'][-2]
        
        # Check if someone accepted explicitly
        acceptance_keywords = ['accept', 'deal', 'agreed', 'proceed', 'paperwork', 'finalize']
        if any(keyword in last_round['message'].lower() for keyword in acceptance_keywords):
            final_price = last_round['price']
            # Validate final price is within acceptable range
            if negotiation['seller_min'] <= final_price <= negotiation['buyer_max']:
                negotiation['status'] = 'agreed'
                negotiation['final_price'] = final_price
                save_negotiation(
                    app.config['DATABASE'],
                    negotiation['item'],
                    negotiation['buyer_max'],
                    negotiation['seller_min'],
                    negotiation['final_price'],
                    "\n".join([f"{r['agent'].title()}: {r['message']}" for r in negotiation['rounds']])
                )
            else:
                negotiation['status'] = 'failed'
                negotiation['reason'] = f'Final price ${final_price:.2f} outside acceptable range'
        # Check if prices are very close (within 2% of average) AND within valid range
        elif (prev_round['agent'] != last_round['agent'] and 
              abs(prev_round['price'] - last_round['price']) < ((prev_round['price'] + last_round['price']) / 2 * 0.02)):
            final_price = (prev_round['price'] + last_round['price']) / 2
            # Validate final price is within acceptable range
            if negotiation['seller_min'] <= final_price <= negotiation['buyer_max']:
                negotiation['status'] = 'agreed'
                negotiation['final_price'] = final_price
                save_negotiation(
                    app.config['DATABASE'],
                    negotiation['item'],
                    negotiation['buyer_max'],
                    negotiation['seller_min'],
                    negotiation['final_price'],
                    "\n".join([f"{r['agent'].title()}: {r['message']}" for r in negotiation['rounds']])
                )
            else:
                negotiation['status'] = 'failed'
                negotiation['reason'] = f'Final price ${final_price:.2f} outside acceptable range'
        # Check for negotiation failure (too many rounds without progress)
        elif len(negotiation['rounds']) >= 10:
            negotiation['status'] = 'failed'
    
    return jsonify(negotiation)

@app.route('/download_report/<int:negotiation_id>')
def download_report(negotiation_id):
    """Generate and download PDF report for a negotiation"""
    try:
        # Get negotiation data from database (simplified - you'd implement this)
        # For now, we'll generate a sample report
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Negotiation Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Sample content - in real implementation, you'd fetch from database
        content = Paragraph("This is a sample negotiation report. Full implementation would include actual negotiation data.", styles['Normal'])
        story.append(content)
        
        doc.build(story)
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=negotiation_report_{negotiation_id}.pdf'
        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_pdf_report', methods=['POST'])
def generate_pdf_report():
    """Generate PDF report from negotiation data"""
    try:
        data = request.json
        negotiation = data['negotiation']
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("NEGOTIATION ANALYSIS REPORT", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Executive Summary
        summary_title = Paragraph("Executive Summary", styles['Heading1'])
        story.append(summary_title)
        summary_text = Paragraph(negotiation.get('summary', 'No summary available'), styles['Normal'])
        story.append(summary_text)
        story.append(Spacer(1, 15))
        
        # Negotiation Details Table
        details_title = Paragraph("Negotiation Details", styles['Heading1'])
        story.append(details_title)
        
        details_data = [
            ['Item', negotiation['item']],
            ['Buyer Maximum Price', f"${negotiation['buyer_max']:.2f}"],
            ['Seller Minimum Price', f"${negotiation['seller_min']:.2f}"],
            ['Final Status', negotiation['status'].title()],
            ['Final Price', f"${negotiation.get('final_price', 0):.2f}"],
            ['Total Rounds', str(len(negotiation['rounds']))]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        # Round by Round Analysis
        rounds_title = Paragraph("Round-by-Round Breakdown", styles['Heading1'])
        story.append(rounds_title)
        
        for round_data in negotiation['rounds']:
            round_text = f"<b>Round {round_data.get('round', 'N/A')} - {round_data['agent'].title()}:</b><br/>"
            round_text += f"Price: ${round_data['price']:.2f}<br/>"
            round_text += f"Message: {round_data['message']}"
            
            round_para = Paragraph(round_text, styles['Normal'])
            story.append(round_para)
            story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 20))
        
        # Strategic Analysis
        analysis_title = Paragraph("Strategic Analysis", styles['Heading1'])
        story.append(analysis_title)
        analysis_text = Paragraph(negotiation.get('analysis', 'No analysis available'), styles['Normal'])
        story.append(analysis_text)
        
        doc.build(story)
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=negotiation_report_{negotiation["item"].replace(" ", "_")}.pdf'
        
        return response
    except Exception as e:
        print(f"PDF generation error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)