from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import decimal
import os
import random
import time
import json

# Bot credentials
api_id = 11683442  # Replace with your Telegram API ID
api_hash = "5125412d657f5d2da179799a5bc7cb6d"  # Replace with your Telegram API Hash
bot_token = "8004715331:AAFHEF-LfrnJZLy2YavpcIHATtSRG81hlGc"  # Replace with your BotFather token

# Initialize the bot
app = Client("fenyx_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Global variable to track user states
user_states = {}

# Function: Fetch token details using CoinGecko API
def get_token_details(contract_address, chain_id="ethereum"):
    """
    Fetches token details by contract address from CoinGecko API.
    Args:
        contract_address (str): The contract address of the token.
        chain_id (str): The blockchain to query ('ethereum' or 'solana').
    Returns:
        str: Details of the token in a formatted string or an error message.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{chain_id}/contract/{contract_address}"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-BNqmBE6QoBKHrXLSYe3wmsmm"  # Your API key
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            name = data.get("name", "N/A")
            symbol = data.get("symbol", "N/A")
            price = data.get("market_data", {}).get("current_price", {}).get("usd", "N/A")
            
            # Convert price to a proper format without scientific notation
            if isinstance(price, (float, int)):
                price = f"{decimal.Decimal(price):f}"  # Format to avoid scientific notation
            
            return f"📄 Token Details:\n" \
                   f"🔹 Name: {name}\n" \
                   f"🔸 Symbol: {symbol}\n" \
                   f"💹 Price (USD): ${price}\n" \
                   f"📜 Contract Address: {contract_address}"
        elif response.status_code == 404:
            return "⚠️ Token not found. Please check the contract address or chain."
        else:
            return "🚨 Error fetching token details. Try again later."
    except Exception as e:
        return f"❌ API Error: {e}"

# Command: /start
@app.on_message(filters.command("start"))
def start(client, message):
    buttons = [
        [InlineKeyboardButton("🔍 Check CA", callback_data="check_ca")],
        [InlineKeyboardButton("🆕 New Ethereum Tokens", callback_data="new_eth_tokens")],
        [InlineKeyboardButton("🤖 AI Trader", callback_data="ai_trader")],
        [InlineKeyboardButton("👛 Your Wallet", callback_data="your_wallet")],
        [InlineKeyboardButton("🎯 Sniper AI", callback_data="sniper_ai")],
        [InlineKeyboardButton("📦 Bundler AI", callback_data="bundler_ai")],
        [InlineKeyboardButton("📜 T&C", callback_data="terms_conditions")],
        [InlineKeyboardButton("🖼️ AI Image Gen", callback_data="ai_image_gen")],  # New button added
    ]
    message.reply_text(
        "👋 Welcome to Fenyx AI Protocol BOT!\nChoose an option below:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Callback Handler: Handle button clicks
@app.on_callback_query()
def handle_callback(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "check_ca":
        user_states[user_id] = "waiting_for_ca"  # Set state to expect contract address input
        callback_query.message.reply_text("🔍 Please enter the contract address you want to check.")
    
    elif data == "ai_image_gen":
        user_states[user_id] = "waiting_for_image_prompt"  # Set state to expect image prompt input
        callback_query.message.reply_text("🖼️ Please enter a prompt description for the image you want to generate.")
    
    elif data in [
        "new_eth_tokens", "ai_trader", "your_wallet",
        "sniper_ai", "bundler_ai", "terms_conditions"
    ]:
        buttons = [[InlineKeyboardButton("🔙 Return to Menu", callback_data="return_to_menu")]]
        callback_query.message.reply_text(
            "🚧 Coming soon! Stay tuned for updates. 🚀",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "return_to_menu":
        start(client, callback_query.message)  # Return to main menu
    else:
        callback_query.message.reply_text("Invalid option. Please try again.")

# Handle user input for contract address
@app.on_message()
def handle_user_input(client, message):
    user_id = message.from_user.id
    if user_states.get(user_id) == "waiting_for_ca":
        contract_address = message.text.strip()
        if len(contract_address) < 5:  # Basic validation
            message.reply_text("⚠️ Invalid contract address. Please try again.")
            return

        message.reply_text("⏳ Fetching token details, please wait...")
        result = get_token_details(contract_address)
        
        # Show token details and return options
        buttons = [
            [InlineKeyboardButton("🔍 Check Another Token CA", callback_data="check_ca")],
            [InlineKeyboardButton("🔙 Return to Home Menu", callback_data="return_to_menu")]
        ]
        message.reply_text(result, reply_markup=InlineKeyboardMarkup(buttons))
        
        user_states[user_id] = None  # Reset state

    elif user_states.get(user_id) == "waiting_for_image_prompt":
        prompt = message.text.strip()
        message.reply_text("⏳ Generating image, please wait...")
        
        # Call the Midjourney API with the prompt
        midjourney_api = MidjourneyApi(
            prompt=prompt,
            application_id="YOUR_APPLICATION_ID",  # Replace with your application ID
            guild_id="YOUR_GUILD_ID",              # Replace with your guild ID
            channel_id="YOUR_CHANNEL_ID",          # Replace with your channel ID
            version="YOUR_VERSION",                 # Replace with your version
            id="YOUR_ID",                           # Replace with your ID
            authorization="YOUR_AUTHORIZATION"     # Replace with your authorization token
        )
        
        image_path = midjourney_api.image_path()
        
        # Send the generated image back to the user
        with open(image_path, "rb") as image_file:
            message.reply_photo(photo=image_file, caption="Here is your generated image:")
        
        user_states[user_id] = None  # Reset state

# Midjourney API class (add this class to your code)
class MidjourneyApi:
    def __init__(self, prompt, application_id, guild_id, channel_id, version, id, authorization):
        self.application_id = application_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.version = version
        self.id = id
        self.authorization = authorization
        self.prompt = prompt
        self.message_id = ""
        self.custom_id = ""
        self.image_path_str = ""
        self.send_message()
        self.get_message()
        self.choose_images()
        self.download_image()

    def send_message(self):
        url = "https://discord.com/api/v9/interactions"
        data = {
            "type": 2,
            "application_id": self.application_id,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "session_id": "cannot be empty",
            "data": {
                "version": self.version,
                "id": self.id,
                "name": "imagine",
                "type": 1,
                "options": [
                    {
                        "type": 3,
                        "name": "prompt",
                        "value": self.prompt
                    }
                ],
                "attachments": []
            },
        }
        headers = {
            'Authorization': self.authorization,
            'Content-Type': 'application/json',
        }
        requests.post(url, headers=headers, json=data)

    def get_message(self):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        for i in range(3):
            time.sleep(30)
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages', headers=headers)
                messages = response.json()
                most_recent_message_id = messages[0]['id']
                self.message_id = most_recent_message_id
                components = messages[0]['components'][0]['components']
                buttons = [comp for comp in components if comp.get('label') in ['U1', 'U2', 'U3', 'U4']]
                custom_ids = [button['custom_id'] for button in buttons]
                random_custom_id = random.choice(custom_ids)
                self.custom_id = random_custom_id
                break
            except:
                ValueError("Timeout")

    def choose_images(self):
        url = "https://discord.com/api/v9/interactions"
        headers = {
            "Authorization": self.authorization,
            "Content-Type": "application/json",
        }
        data = {
            "type": 3,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "message_flags": 0,
            "message_id": self.message_id,
            "application_id": self.application_id,
            "session_id": "cannot be empty",
            "data": {
                "component_type": 2,
                "custom_id": self.custom_id,
            }
        }
        requests.post(url, headers=headers, json=data)

    def download_image(self):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        for i in range(3):
            time.sleep(30)
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages', headers=headers)
                messages = response.json()
                most_recent_message_id = messages[0]['id']
                self.message_id = most_recent_message_id
                image_url = messages[0]['attachments'][0]['url']
                image_response = requests.get(image_url)
                a = urlparse(image_url)
                image_name = os.path.basename(a.path)
                self.image_path_str = f"images/{image_name}"
                with open(f"images/{image_name}", "wb") as file:
                    file.write(image_response.content)
                break
            except:
                raise ValueError("Timeout")

    def image_path(self):
        return self.image_path_str

# Run the bot
app.run()