import discord
import asyncio
from aiohttp import web
import random
import sys
import os
import time
from hugchat import hugchat
from hugchat.login import Login

# Set your Discord account token here
TOKEN = "Nzg0Nzg5NTI5NjYzODk3NjMx.GhshlE.Ad756I2U32iaPpYKN1l-lmAPaUeSLaFvfBcDM8"  # Replace with your account's token
VOICE_CHANNEL_ID = 678955120301572096  # Replace with the ID of your desired voice channel
QUOTES_FILE = "quotes.txt"


# HuggingChat credentials
HUGGING_EMAIL = "nguoiaoden111@gmail.com" # Replace with your HuggingFace email
HUGGING_PASSWORD = "Tranducduy2@"  # Replace with your HuggingFace password

class SelfBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.chatbot = None
        self.chat_id = None
        
    async def setup_hook(self):
        # Start the web server and voice channel task
        self.loop.create_task(self.start_web_server())
        self.loop.create_task(self.stay_in_voice_channel())
        # self.loop.create_task(self.send_message_loop())
        self.loop.create_task(self.setup_huggingchat())
    
    async def setup_huggingchat(self):
        """Initialize HuggingChat connection"""
        try:
            print("Setting up HuggingChat connection...")
            sign = Login(HUGGING_EMAIL, HUGGING_PASSWORD)
            cookie_path_dir = "./cookies/" # NOTE: trailing slash (/) is required to avoid errors
            cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

            self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
            # Create a new conversation
            self.chat_id = self.chatbot.new_conversation()
            self.chatbot.change_conversation(self.chat_id)
            
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
    
    # async def send_message_loop(self):
    #     """Sends a random message every 30 minutes to the text chat of the voice channel."""
    #     await self.wait_until_ready()
    #     while not self.is_closed():
    #         try:
    #             channel = self.get_channel(VOICE_CHANNEL_ID)
    #             if channel:
    #                 message = self.get_random_quote()
    #                 await channel.send(f"{message}")
    #                 print(f"Sent message: {message}")
    #             else:
    #                 print("No available text channel found.")
    #         except Exception as e:
    #             print(f"Error sending message: {e}")
    #         await asyncio.sleep(1800)  # 30 minutes
    
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
        if not self.chatbot:
            return self.get_random_quote()
        
        try:
            # Get response from HuggingChat
            response = await asyncio.to_thread(
                self.chatbot.chat, 
                prompt,
                temperature=0.7,
                max_new_tokens=150  # Limit response length
            )
            
            # Clean up the response
            cleaned_response = response.strip()
            # Limit response length for Discord
            if len(cleaned_response) > 1500:
                cleaned_response = cleaned_response[:1500] + "..."
                
            return cleaned_response
        except Exception as e:
            print(f"Error getting AI response: {e}")
            # Fallback to quotes
            return self.get_random_quote()
    
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
                if not content:
                    content = "Hello"
                
                # Create a prompt for the AI
                prompt = f"{message.author.display_name} said: {content}\nRespond in a friendly way as if you're having a casual conversation."
                
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
                await message.channel.send(self.get_random_quote())

client = SelfBot()
client.run(TOKEN)
