import os
import logging
from flask import Flask, request, jsonify
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.core.conversation_state import ConversationState
from botbuilder.core.memory_storage import MemoryStorage
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from botbuilder.adapter.teams import TeamsAdapter
from azure.cognitiveservices.language.translator import TranslatorClient
from azure.core.credentials import AzureKeyCredential
import asyncio
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Translator configuration
TRANSLATOR_KEY = os.environ.get("AZURE_TRANSLATOR_KEY")
TRANSLATOR_ENDPOINT = os.environ.get("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
TRANSLATOR_REGION = os.environ.get("AZURE_TRANSLATOR_REGION", "eastus")

# Bot configuration
BOT_APP_ID = os.environ.get("BOT_APP_ID", "")
BOT_APP_PASSWORD = os.environ.get("BOT_APP_PASSWORD", "")

class TranslationBot(ActivityHandler):
    def __init__(self):
        super().__init__()
        self.translator_client = self._create_translator_client()

    def _create_translator_client(self):
        """Create Azure Translator client"""
        try:
            import requests
            return requests.Session()
        except Exception as e:
            logger.error(f"Failed to create translator client: {e}")
            return None

    async def translate_text(self, text: str, target_language: str) -> str:
        """Translate text using Azure Translator API"""
        if not self.translator_client or not TRANSLATOR_KEY:
            return "Translation service not configured"

        try:
            # Azure Translator REST API endpoint
            url = f"{TRANSLATOR_ENDPOINT}/translate"
            
            headers = {
                'Ocp-Apim-Subscription-Key': TRANSLATOR_KEY,
                'Ocp-Apim-Subscription-Region': TRANSLATOR_REGION,
                'Content-Type': 'application/json'
            }
            
            # Detect source language and translate
            params = {
                'api-version': '3.0',
                'to': target_language
            }
            
            body = [{'text': text}]
            
            response = self.translator_client.post(url, params=params, headers=headers, json=body)
            response.raise_for_status()
            
            result = response.json()
            translated_text = result[0]['translations'][0]['text']
            detected_language = result[0].get('detectedLanguage', {}).get('language', 'unknown')
            
            return f"**Translated** ({detected_language} → {target_language}):\n{translated_text}"
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return f"Sorry, translation failed: {str(e)}"

    def _detect_language_and_get_target(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        # Check for Sinhala Unicode range
        sinhala_chars = any('\u0d80' <= char <= '\u0dff' for char in text)
        
        if sinhala_chars:
            return 'en'  # If Sinhala detected, translate to English
        else:
            return 'si'  # Otherwise, translate to Sinhala

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages"""
        user_message = turn_context.activity.text.strip()
        
        if not user_message:
            await turn_context.send_activity(MessageFactory.text("Please send some text to translate!"))
            return

        # Handle help command
        if user_message.lower() in ['/help', 'help', '/translate help']:
            help_text = """
**Translation Bot Help**

Simply type any text in English or Sinhala, and I'll translate it for you!

**Examples:**
- Type: "Hello, how are you?" → Gets translated to Sinhala
- Type: "ඔබට කොහොමද?" → Gets translated to English

**Commands:**
- `/help` or `help` - Show this help message
- Just type any text - Auto-detects language and translates

**Supported Languages:**
- English ↔ Sinhala
            """
            await turn_context.send_activity(MessageFactory.text(help_text))
            return

        # Auto-detect language and translate
        target_language = self._detect_language_and_get_target(user_message)
        
        # Show typing indicator
        typing_activity = Activity(type=ActivityTypes.typing)
        await turn_context.send_activity(typing_activity)
        
        # Perform translation
        translated_text = await self.translate_text(user_message, target_language)
        
        # Send translated result
        await turn_context.send_activity(MessageFactory.text(translated_text))

    async def on_members_added_activity(self, members_added: list, turn_context: TurnContext):
        """Welcome new members"""
        welcome_text = """
👋 **Welcome to Translation Bot!**

I can translate between English and Sinhala instantly!

Just type any text and I'll automatically detect the language and translate it for you.

Type `/help` for more information.
        """
        
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(MessageFactory.text(welcome_text))

# Flask app setup
app = Flask(__name__)

# Create bot adapter
adapter = TeamsAdapter(BOT_APP_ID, BOT_APP_PASSWORD)

# Create bot instance
bot = TranslationBot()

@app.route("/api/messages", methods=["POST"])
def messages():
    """Main bot endpoint"""
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return jsonify({"error": "Invalid content type"}), 415

    activity = Activity().deserialize(body)
    auth_header = request.headers["Authorization"] if "Authorization" in request.headers else ""

    async def aux_func(turn_context):
        await bot.on_message_activity(turn_context)

    try:
        response = asyncio.run(adapter.process_activity(activity, auth_header, aux_func))
        if response:
            return jsonify(response.body), response.status
        return "", 200
    except Exception as e:
        logger.error(f"Error processing activity: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "translation-bot"}), 200

@app.route("/", methods=["GET"])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Translation Bot is running!",
        "endpoints": {
            "messages": "/api/messages",
            "health": "/health"
        },
        "supported_languages": ["English", "Sinhala"]
    })

if __name__ == "__main__":
    # Validate required environment variables
    required_vars = ["AZURE_TRANSLATOR_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.info("Please set the following environment variables:")
        logger.info("- AZURE_TRANSLATOR_KEY: Your Azure Translator API key")
        logger.info("- BOT_APP_ID: Your bot's application ID (optional for local testing)")
        logger.info("- BOT_APP_PASSWORD: Your bot's application password (optional for local testing)")
    else:
        logger.info("Starting Translation Bot...")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3978)), debug=False)