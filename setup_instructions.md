# Setup Instructions

## 1. Get your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

## 2. Set the Environment Variable

### Option A: Set for current PowerShell session (temporary)
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

### Option B: Set permanently (recommended)
1. Open System Properties (Win + R, type `sysdm.cpl`)
2. Click "Environment Variables"
3. Under "User variables", click "New"
4. Variable name: `GEMINI_API_KEY`
5. Variable value: your API key
6. Click OK and restart VS Code

### Option C: Create a .env file
1. Create a `.env` file in the negotiation_platform folder
2. Add: `GEMINI_API_KEY=your-api-key-here`
3. Install python-dotenv: `pip install python-dotenv`
4. Add to app.py: `from dotenv import load_dotenv; load_dotenv()`

## 3. Restart your Flask app
After setting the API key, restart your Flask application.

## 4. Test the Application
1. Fill in the negotiation form
2. Click "Start Negotiation"
3. You should see the buyer's initial offer appear
4. Click "Continue Negotiation" to proceed
