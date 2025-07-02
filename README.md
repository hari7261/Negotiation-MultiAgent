# 🤖 AI-Powered Multi-Agent Negotiation Platform

![AI Negotiation Platform](https://img.shields.io/badge/AI-Negotiation-6366f1?style=for-the-badge&logo=ai&logoColor=white)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini-AI-orange?style=for-the-badge&logo=google&logoColor=white)

A sophisticated AI-powered negotiation platform that simulates real-world negotiations using multiple intelligent agents. Built with Google's Gemini AI, this platform demonstrates advanced negotiation strategies, autonomous decision-making, and dynamic price optimization.

## 🌟 Features

### 🎯 Core Capabilities

- **Multi-Agent System**
  - 🤝 Buyer Agent: Strategic price negotiation with learning capabilities
  - 💼 Seller Agent: Adaptive pricing based on market conditions
  - ⚖️ Mediator Agent: Facilitates negotiations and suggests compromises

- **Real-Time Negotiation**
  - 📊 Live negotiation progress tracking
  - 💬 Dynamic message exchange between agents
  - 🎯 Automatic price convergence detection

- **Advanced Analytics**
  - 📈 Negotiation efficiency metrics
  - 🎯 Fair value index calculation
  - 🧮 Complexity score assessment
  - 📋 Detailed transaction history

### 💫 User Experience

- **Modern UI/UX**
  - 🎨 Clean, intuitive interface
  - 📱 Fully responsive design
  - ✨ Smooth animations and transitions
  - 🌓 Light/Dark mode support

- **Real-Time Updates**
  - ⚡ Live negotiation progress
  - 🔄 Automatic status updates
  - 📊 Dynamic price tracking

## 🛠️ Technology Stack

- **Backend**
  - 🐍 Python 3.9+
  - 🌶️ Flask Web Framework
  - 🤖 Google Gemini AI API
  - 🗄️ SQLite Database

- **Frontend**
  - 🎨 Modern CSS with Custom Properties
  - 📱 Responsive Design
  - 🎭 Custom Animations
  - ⚡ Vanilla JavaScript

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key
- Modern web browser

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/negotiation-multiagent.git
   cd negotiation-multiagent
   ```

2. Run the setup script:
   - Windows: `setup.bat`
   - Unix/Mac: `./setup.sh`

3. Configure your environment:
   ```bash
   copy .env.example .env
   # Edit .env and add your Gemini API key
   ```

4. Start the application:
   - Windows: `run.bat`
   - Unix/Mac: `./run.sh`

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## 🎯 How It Works

### Negotiation Process

1. **Initialization**
   - User inputs item details and price ranges
   - System initializes three AI agents: buyer, seller, and mediator

2. **Negotiation Rounds**
   - Buyer makes initial offer
   - Seller responds with counter-offer
   - Mediator intervenes periodically to facilitate agreement
   - Process continues until agreement or maximum rounds reached

3. **Agreement Detection**
   - System automatically detects when agents reach agreement
   - Validates final price against initial constraints
   - Records successful negotiations in database

### AI Agent Behaviors

#### 🤝 Buyer Agent
- Analyzes item value and market conditions
- Implements strategic bidding patterns
- Adapts offers based on seller responses
- Learns from negotiation history

#### 💼 Seller Agent
- Evaluates market position and item worth
- Employs dynamic pricing strategies
- Considers buyer's negotiation pattern
- Maintains profit margins while being flexible

#### ⚖️ Mediator Agent
- Monitors negotiation progress
- Identifies deadlock situations
- Suggests compromises based on both positions
- Helps optimize for mutual benefit

## 📊 Analytics & Metrics

### Efficiency Metrics
- **Negotiation Speed**: Rounds to agreement
- **Price Convergence**: Rate of offer adjustments
- **Success Rate**: Percentage of successful negotiations

### Fair Value Index
- Market value analysis
- Price trend correlation
- Historical transaction comparison

### Complexity Score
- Number of rounds required
- Price movement patterns
- Intervention frequency

## 🎨 UI/UX Features

### Real-Time Updates
- Animated progress indicators
- Live message updates
- Dynamic price tracking

### Interactive Elements
- Negotiation timeline
- Price history graphs
- Status indicators

### Responsive Design
- Mobile-first approach
- Adaptive layouts
- Touch-friendly interfaces

## 📈 Future Enhancements

- 🌐 Multi-language support
- 📊 Advanced analytics dashboard
- 🤝 Multi-party negotiations
- 🔄 Integration with real market data
- 🎯 Custom negotiation strategies

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- Google Gemini AI for providing the advanced language model
- Flask community for the excellent web framework
- All contributors who have helped shape this project

---

<p align="center">
Made with ❤️ by [Your Name]
</p>
