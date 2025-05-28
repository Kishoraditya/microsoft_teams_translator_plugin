# Teams Translation Bot

## Key Features

- **Auto-detection**: Automatically detects if text is English or Sinhala and translates accordingly
- **Simple usage**: Just type any text - no commands needed
- **Azure integration**: Uses Azure Translator service for accurate translations
- **Teams native**: Works directly in Teams chats, groups, and channels

## Architecture

- **Flask web app** as the bot backend
- **Azure Bot Service** for Teams integration
- **Azure Translator** for translation services
- **Azure App Service** for hosting

## How it works

1. User types text in Teams
2. Bot detects language (English or Sinhala)
3. Translates to the other language using Azure Translator
4. Returns formatted translation

## Cost

Completely **FREE** using Azure's free tiers:

- Azure Translator F0: 2M characters/month free
- Azure App Service F1: Free tier
- Bot Service: Free for standard channels

## Simple Setup Process

1. Create Azure Translator service
2. Deploy the Python bot to Azure App Service
3. Register bot in Azure Bot Service
4. Enable Teams channel
5. Install in Teams using the manifest

The bot automatically handles language detection using Unicode character ranges for Sinhala text, making it incredibly simple to use - just type and get instant translations!

## Teams Translation Bot Setup Guide

## Prerequisites

- Azure subscription
- Python 3.8+
- Microsoft Teams account with admin access

## Step 1: Create Azure Resources

### 1.1 Create Azure Translator Service

```bash
# Login to Azure CLI
az login

# Create resource group
az group create --name translation-bot-rg --location eastus

# Create Translator service
az cognitiveservices account create --name translation-service --resource-group translation-bot-rg --kind TextTranslation --sku F0 --location eastus

# Get the key
az cognitiveservices account keys list --name translation-service --resource-group translation-bot-rg
```

### 1.2 Create App Service

```bash
# Create App Service Plan
az appservice plan create --name translation-bot-plan --resource-group translation-bot-rg --sku F1 --is-linux

# Create Web App
az webapp create --name your-translation-bot --resource-group translation-bot-rg --plan translation-bot-plan --runtime "PYTHON|3.9"
```

## Step 2: Register Bot in Azure

### 2.1 Create Bot Registration

1. Go to Azure Portal → "Bot Services" → "Create"
2. Fill in:
   - Bot handle: `translation-bot`
   - Subscription: Your subscription
   - Resource group: `translation-bot-rg`
   - Pricing tier: F0 (Free)
   - App ID: Create new
   - Messaging endpoint: `https://your-translation-bot.azurewebsites.net/api/messages`

### 2.2 Get Bot Credentials

1. In your Bot Service → "Configuration"
2. Copy "App ID" and "App Password"

## Step 3: Deploy the Bot

### 3.1 Local Development Setup

```bash
# Clone or create project directory
mkdir teams-translation-bot
cd teams-translation-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your actual values
```

### 3.2 Deploy to Azure

```bash
# Configure deployment
az webapp config appsettings set --resource-group translation-bot-rg --name your-translation-bot --settings AZURE_TRANSLATOR_KEY="your_translator_key" BOT_APP_ID="your_bot_app_id" BOT_APP_PASSWORD="your_bot_password"

# Deploy code
az webapp up --resource-group translation-bot-rg --name your-translation-bot --runtime "PYTHON:3.9"
```

## Step 4: Configure Teams Integration

### 4.1 Enable Teams Channel

1. In Azure Portal → Your Bot Service → "Channels"
2. Click "Microsoft Teams" icon
3. Click "Save" to enable

### 4.2 Create Teams App Package

1. Update `manifest.json` with your bot ID
2. Create two PNG icons:
   - `color.png` (192x192px)
   - `outline.png` (32x32px, transparent background)
3. Zip these 3 files: `manifest.json`, `color.png`, `outline.png`

### 4.3 Install in

1. Open Microsoft Teams
2. Go to "Apps" → "Manage your apps" → "Upload an app"
3. Upload your ZIP file
4. Click "Add" to install the bot

## Step 5: Test the Bot

### 5.1 Basic Testing

1. Start a chat with your bot in Teams
2. Type: "Hello, how are you?"
3. Should get Sinhala translation
4. Type: "ඔබට කොහොමද?"
5. Should get English translation

### 5.2 Commands to Test

- `/help` - Shows help message
- Any English text - Translates to Sinhala
- Any Sinhala text - Translates to English

## Usage Examples

### User Types

```bash
Hello, how are you?
```

### Bot Responds

```bash
**Translated** (en → si):
ඔබට කොහොමද?
```

### User Types 2

```bash
ඔයා කොහෙද ඉන්නේ?
```

### Bot Responds 2

```bash
**Translated** (si → en):
Where are you?
```

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if messaging endpoint is correct
   - Verify App ID and Password are set correctly
   - Check Azure App Service logs

2. **Translation not working**
   - Verify Azure Translator key is valid
   - Check if Translator service is active
   - Ensure proper API permissions

3. **Teams installation fails**
   - Verify manifest.json format
   - Check if bot ID matches in manifest
   - Ensure ZIP file contains all required files

### Logs and Debugging

```bash
# View App Service logs
az webapp log tail --resource-group translation-bot-rg --name your-translation-bot

# Check bot health
curl https://your-translation-bot.azurewebsites.net/health
```

## Architecture Overview

```bash
Teams User → Teams Service → Azure Bot Service → Your App Service → Azure Translator → Response Back
```

## Cost Estimation

- Azure Translator (F0): Free tier - 2M characters/month
- Azure App Service (F1): Free tier
- Azure Bot Service: Free for standard channels
- **Total monthly cost: $0** for basic usage

## Security Notes

- Bot credentials are stored as environment variables
- HTTPS is enforced for all communications
- No user data is stored permanently
- Translation requests are processed through Azure's secure APIs

## Customization Options

- Add more language pairs by modifying language detection logic
- Implement user preferences for default languages
- Add conversation context for better translations
- Include translation confidence scores
- Add support for document translation

This setup provides a fully functional, production-ready Teams translation bot with minimal complexity while using Azure's robust infrastructure.
