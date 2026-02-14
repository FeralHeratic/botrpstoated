import revolt
import json
import os
import asyncio

# --- CONFIGURATION ---
# We load the token from the environment instead of hardcoding it.
# On FPS.ms, go to the "Variables" tab and add a variable named: BOT_TOKEN
TOKEN = os.getenv("BOT_TOKEN")
FILE_NAME = "characters.json"

class StoatBot(revolt.Client):
    def load_data(self):
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r") as f:
                return json.load(f)
        return {"templates": []}

    def save_data(self, data):
        with open(FILE_NAME, "w") as f:
            json.dump(data, f, indent=4)

    async def on_ready(self):
        print(f"✅ SUCCESS: Bot is online as {self.user.name} on Stoat!")

    async def on_message(self, message: revolt.Message):
        if message.author.bot or not message.content:
            return

        # 1. THE PROXY SYSTEM
        data = self.load_data()
        for char in data.get("templates", []):
            prefix = char.get("prefix", "")
            if prefix and message.content.startswith(prefix):
                # Clean the trigger out of the text
                clean_content = message.content.replace(prefix, "", 1).strip()
                
                # Delete the original user message
                await message.delete()
                
                # Send the "proxied" message
                return await message.channel.send(
                    clean_content, 
                    masquerade=revolt.Masquerade(
                        name=char['name'], 
                        avatar=char['avatar_url']
                    )
                )

        # 2. COMMANDS
        if message.content.startswith("!register"):
            try:
                parts = message.content.split(" ")
                name = parts[1].strip('"')
                prefix = parts[2]
                avatar = parts[3]
                data = self.load_data()
                data["templates"].append({
                    "name": name, 
                    "prefix": prefix, 
                    "avatar_url": avatar, 
                    "owner_id": str(message.author.id)
                })
                self.save_data(data)
                await message.channel.send(f"✅ **{name}** registered!")
            except:
                await message.channel.send("❌ Use: `!register \"Name\" [Prefix] URL`")

        if message.content == "!list":
            data = self.load_data()
            names = [c['name'] for c in data.get("templates", [])]
            await message.channel.send(f"👥 Characters: {', '.join(names) if names else 'None'}")

async def main():
    if not TOKEN:
        print("❌ ERROR: No BOT_TOKEN found in environment variables!")
        return

    async with revolt.utils.client_session() as session:
        # Points to Stoat API (change to api.revolt.chat for main Revolt)
        client = StoatBot(session, TOKEN, api_url="https://api.stoat.chat")
        await client.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Connection Error: {e}")
