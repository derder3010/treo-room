import discord
import asyncio

# Set your Discord account token here
TOKEN = "Nzg4ODE4MjU1NDgwNDg3OTM2.G3tOur.b4uhyN0dtVATXOWFpYWvtwO391QeAqgZqqWjh8"  # Replace with your account's token
VOICE_CHANNEL_ID = (
    1273285776905338922  # Replace with the ID of your desired voice channel
)


class SelfBot(discord.Client):
    async def setup_hook(self):
        # Start the task to keep the bot in the voice channel
        self.loop.create_task(self.stay_in_voice_channel())

    async def stay_in_voice_channel(self):
        """Keep the self-bot connected to the specified voice channel."""
        await self.wait_until_ready()

        while not self.is_closed():
            try:
                # Get the voice channel by ID
                channel = self.get_channel(VOICE_CHANNEL_ID)
                if isinstance(channel, discord.VoiceChannel):
                    # Connect to the channel if not already connected
                    if (
                        not self.voice_clients
                        or not self.voice_clients[0].is_connected()
                    ):
                        print(f"Connecting to voice channel: {channel.name}")
                        await channel.connect()
                    else:
                        print(f"Already connected to {channel.name}")
                else:
                    print(
                        f"The provided ID ({VOICE_CHANNEL_ID}) is not a voice channel."
                    )
                    break
            except Exception as e:
                print(f"Error occurred: {e}")

            # Check every 60 seconds
            await asyncio.sleep(60)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print("Keeping the account in the voice channel...")


# Create and run the bot
client = SelfBot()
client.run(TOKEN)
