#!/usr/bin/env python3
"""
BOT MINECRAFT per Render.com
"""
import discord
import os
import asyncio
from flask import Flask
from threading import Thread

# Configurazione da variabili d'ambiente (SICUREZZA!)
TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', 1418196149545730153))

# Web server per keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Minecraft Bot is Online!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

class MinecraftBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
    
    async def on_ready(self):
        print(f'✅ Bot avviato su Render: {self.user}')
        print(f'🏠 Web server: https://{os.environ.get("RENDER_SERVICE_NAME")}.onrender.com')
        
        try:
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                await channel.send('🎮 **Bot Minecraft avviato su Render!**\n`✅ Server sempre attivo`')
            else:
                print(f'❌ Canale {CHANNEL_ID} non trovato')
        except Exception as e:
            print(f'❌ Errore invio messaggio: {e}')
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.lower() in ['!ciao', '!hello']:
            await message.channel.send('Ciao! Sono il bot del server Minecraft! 🎮')
        
        if message.content.lower() == '!status':
            await message.channel.send('🟢 **Server Online**\n`Hosted on Render.com`')
        
        if message.content.lower() == '!info':
            await message.channel.send(
                '**🤖 Minecraft Bot Info**\n'
                '• Host: Render.com\n'
                '• Status: Always Online\n'
                '• Commands: !ciao, !status, !info'
            )

async def run_bot():
    if not TOKEN:
        print("❌ Token non configurato! Imposta DISCORD_TOKEN")
        return
    
    bot = MinecraftBot()
    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Token errato! Controlla DISCORD_TOKEN")
    except Exception as e:
        print(f"❌ Errore: {e}")

def main():
    print("🎮 Avvio Minecraft Bot su Render...")
    
    # Avvia web server in background
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # Avvia bot Discord
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
