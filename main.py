import discord
import asyncio
from aiohttp import web
import random

# Set your Discord account token here
TOKEN = "Nzg0Nzg5NTI5NjYzODk3NjMx.GhshlE.Ad756I2U32iaPpYKN1l-lmAPaUeSLaFvfBcDM8"  # Replace with your account's token
VOICE_CHANNEL_ID = 1338058808899145758  # Replace with the ID of your desired voice channel
QUOTES_FILE = "quotes.txt"


class SelfBot(discord.Client):
    async def setup_hook(self):
        # Start the web server and voice channel task
        self.loop.create_task(self.start_web_server())
        self.loop.create_task(self.stay_in_voice_channel())
        self.loop.create_task(self.send_message_loop())  # Start sending messages every 30 min
    
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
                    await channel.send(f"{message}")
                    print(f"Sent message: {message}")
                else:
                    print("No available text channel found.")

                # if isinstance(channel, discord.VoiceChannel):
                #     text_channel = channel.guild.system_channel or discord.utils.get(channel.guild.text_channels)
                #     if text_channel:
                #         message = self.get_random_quote()
                #         await text_channel.send(message)
                #         print(f"Sent message: {message}")
                #     else:
                #         print("No available text channel found.")
                # else:
                #     print(f"Voice channel {VOICE_CHANNEL_ID} not found.")
            except Exception as e:
                print(f"Error sending message: {e}")

            await asyncio.sleep(1800)  # 30 minutes

    def get_random_quote(self):
        """Reads quotes from a file and returns a random one."""
        try:
            with open(QUOTES_FILE, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file if line.strip()]
            return random.choice(lines) if lines else "No quotes available."
        except Exception as e:
            return f"Error reading quotes: {e}"
    
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print("Keeping the account in the voice channel...")



client = SelfBot()
client.run(TOKEN)
