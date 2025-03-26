import discord
import asyncio
from aiohttp import web
import random
import sys
import os
import json
import time
from hugchat import hugchat
from hugchat.login import Login

# Set your Discord account token here
TOKEN = "Nzg0Nzg5NTI5NjYzODk3NjMx.GhshlE.Ad756I2U32iaPpYKN1l-lmAPaUeSLaFvfBcDM8"  # Replace with your account's token
VOICE_CHANNEL_ID = 1273285776905338922  # Replace with the ID of your desired voice channel
QUOTES_FILE = "quotes.txt"


# HuggingChat credentials
HUGGING_EMAIL = "nguoiaoden111@gmail.com" # Replace with your HuggingFace email
HUGGING_PASSWORD = "Tranducduy2@"  # Replace with your HuggingFace password
COOKIE_DIR = "./cookies/" # NOTE: trailing slash (/) is required to avoid errors
ASSISTANT_ID = "65ddfa3539b31e70f8b55dfb"  # Name of the assistant to use in prompts




class SelfBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.chatbot = None
        self.chat_id = None
        
    async def setup_hook(self):
        # Start the web server and voice channel task
        self.loop.create_task(self.start_web_server())
        self.loop.create_task(self.stay_in_voice_channel())
        self.loop.create_task(self.send_message_loop())
        self.loop.create_task(self.setup_huggingchat())
        self.loop.create_task(self.reset_chat_loop())
    
    async def load_cookies(self):
        """Load cookies if available, else raise an exception."""
        cookie_files = os.listdir(COOKIE_DIR)
        if not cookie_files:
            raise Exception("No cookies found. Please log in.")
        
        cookie_path = os.path.join(COOKIE_DIR, cookie_files[0])
        with open(cookie_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        return cookies

    
    async def setup_huggingchat(self):
        """Initialize HuggingChat connection"""
        try:
            print("Setting up HuggingChat connection...")
            if os.listdir(COOKIE_DIR):
                print("Loading cookies...")
                cookies = await self.load_cookies()  
            else:
                print("Logging in...")
                sign = Login(HUGGING_EMAIL, HUGGING_PASSWORD)
                cookies = sign.login(cookie_dir_path=COOKIE_DIR, save_cookies=True).get_dict()

            self.chatbot = hugchat.ChatBot(cookies=cookies)
            # Create a new conversation
            self.chat_id = self.chatbot.new_conversation(assistant=ASSISTANT_ID, switch_to = True)
            # self.chatbot.change_conversation(self.chat_id)
            
            print("HuggingChat setup complete!")
        except Exception as e:
            print(f"Error setting up HuggingChat: {e}")
            print("Falling back to quotes for responses")
    
    async def start_web_server(self):
        """Start a simple web server to satisfy Render's port requirement"""
        app = web.Application()
        app.router.add_get('/', self.handle_request)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 10000)
        await site.start()
        print("Web server started on port 10000")
    
    async def handle_request(self, request):
        """Handle health check requests"""
        return web.Response(text="OK")
    
    async def stay_in_voice_channel(self):
        """Keep the self-bot connected to the specified voice channel."""
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                channel = self.get_channel(VOICE_CHANNEL_ID)
                if isinstance(channel, discord.VoiceChannel):
                    if not self.voice_clients or not self.voice_clients[0].is_connected():
                        print(f"Connecting to voice channel: {channel.name}")
                        await channel.connect()
                    else:
                        print(f"Already connected to {channel.name}")
                else:
                    print(f"The provided ID ({VOICE_CHANNEL_ID}) is not a voice channel.")
                    break
            except Exception as e:
                print(f"Error occurred: {e}")
            await asyncio.sleep(60)
    
    async def send_message_loop(self):
        """Sends a random message every 30 minutes to the text chat of the voice channel."""
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                channel = self.get_channel(VOICE_CHANNEL_ID)
                if channel:
                    message = self.get_random_quote()
                    await channel.send(f"24p {message}")
                    print(f"Sent message: {message}")
                else:
                    print("No available text channel found.")
            except Exception as e:
                print(f"Error sending message: {e}")
            await asyncio.sleep(300)  # 30 minutes
    
    async def reset_chat_loop(self):
        """Creates a new HuggingChat conversation every 30 minutes."""
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                print("Creating new HuggingChat conversation...")
                if self.chatbot:
                    # Create a new conversation
                    self.chat_id = self.chatbot.new_conversation(assistant=ASSISTANT_ID, switch_to = True)
                    # self.chatbot.change_conversation(self.chat_id)
                    print(f"New conversation created with ID: {self.chat_id}")
                    
                    # Optionally announce this in a channel
                    # channel = self.get_channel(VOICE_CHANNEL_ID)
                    # if channel:
                    #     await channel.send("Mình vừa tạo lại trí nhớ nè, hãy trò chuyện với mình! 😊")
                else:
                    print("Chatbot not initialized, cannot create new conversation")
            except Exception as e:
                print(f"Error creating new conversation: {e}")
            await asyncio.sleep(1800)  # 30 minutes
    
    def get_random_quote(self):
        """Reads quotes from a file and returns a random one."""
        try:
            with open(QUOTES_FILE, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file if line.strip()]
            return random.choice(lines) if lines else "No quotes available."
        except Exception as e:
            return f"Error reading quotes: {e}"
        
        
    
    async def get_ai_response(self, prompt):
        """Get a response from HuggingChat"""
        # if not self.chatbot:
        #     return self.get_random_quote()
        
        try:
            # Get response from HuggingChat
            response = await asyncio.to_thread(
                self.chatbot.chat, 
                prompt,
                temperature=0.7,
                webweb_search=True
            )
            print(response)
            return response
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return "hình như sai sai ở đâu í, @heyim_der-onichan ơi cứu em :("
    
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print("Keeping the account in the voice channel...")
    
    async def on_message(self, message):
        """Respond when mentioned in a message"""
        # Skip messages sent by this bot
        if message.author == self.user:
            return
        
        # Check if bot was mentioned
        if self.user.mentioned_in(message):
            try:
                # Get user's message content without the mention
                content = message.content.replace(f'<@{self.user.id}>', '').strip()
                print(content)
                if not content:
                    content = "Hello"
                
                # Create a prompt for the AI
                prompt = f"{message.author.display_name} said: {content}\nRespond in Vietnamese in a lovely and affectionate way, as if you're having a casual conversation with a lover. Always use 'em' to refer to yourself, and 'anh' refer me. Your profile: Your name is Meow. Your are a peretty girl. You have a boyfriend named Dersieudeptrai. You're a second-year university student studying art. You love cats, enjoy playing video games, watching movies, reading books, listening to music, and traveling. Your favorite color is black. Keep your responses short and natural as possible, within 1000 characters. You can use emojis, gifs, and stickers to make your responses more engaging but jsut a litle, only 1 each respone."
                
                # Typing indicator to show the bot is "thinking"
                async with message.channel.typing():
                    # Get AI response
                    response = await self.get_ai_response(prompt)
                
                # Send the response
                await message.channel.send(response)
                print(f"Responded to mention from {message.author.display_name}")
            except Exception as e:
                print(f"Error responding to mention: {e}")
                # Fallback to a random quote if AI fails
                await message.channel.send("hình như sai sai ở đâu í, @heyim_der-onichan ơi cứu em :(")

client = SelfBot()
client.run(TOKEN)
