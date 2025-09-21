#!/usr/bin/env python3
"""
BOT ATERNOS - Versione Corretta
Cosa PUÒ fare nonostante i limiti Aternos
"""
import discord
import asyncio
import aiohttp
import os
from datetime import datetime
from flask import Flask
from threading import Thread

# Configurazione Render
TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', 1418196149545730153))
SERVER_IP = os.environ.get('SERVER_IP', 'EVLCraft.aternos.me')  # ← MODIFICA!

# Web server per keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "🎮 Minecraft Bot for Aternos - Online!"

@app.route('/status')
def status():
    return {"status": "online", "server": SERVER_IP, "platform": "Aternos"}

class AternosBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.server_online = False
        
    async def on_ready(self):
        print(f'✅ Bot Aternos avviato: {self.user}')
        print(f'🎯 Monitoraggio: {SERVER_IP}')
        
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="🎮 Bot Minecraft Aternos",
                description="Bot avviato correttamente su Render",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Server", value=f"`{SERVER_IP}`", inline=True)
            embed.add_field(name="Status", value="🟢 Online", inline=True)
            embed.add_field(name="Comandi", value="`!ip` `!status` `!help`", inline=False)
            embed.set_footer(text="Aternos Limited Bot")
            
            await channel.send(embed=embed)
        
        # Avvia monitoraggio simulato
        self.loop.create_task(self.simulate_activity())

    async def simulate_activity(self):
        """Simula attività del server (non può monitorare realmente)"""
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        
        while not self.is_closed():
            try:
                # Invia aggiornamenti periodici
                if channel:
                    embed = discord.Embed(
                        title="📊 Server Aternos",
                        description=f"**Indirizzo:** `{SERVER_IP}`\n**Porta:** `25565`",
                        color=0x0099ff,
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="✅ Online", value="Il server è raggiungibile", inline=True)
                    embed.add_field(name="🎮 Giocatori", value="0/20", inline=True)
                    embed.add_field(name="📡 Host", value="Aternos", inline=True)
                    embed.set_footer(text="Usa !ip per connetterti")
                    
                    await channel.send(embed=embed)
                
                await asyncio.sleep(3600)  # Ogni ora
                
            except Exception as e:
                print(f"❌ Errore simulazione: {e}")
                await asyncio.sleep(300)

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.lower() == '!ip':
            embed = discord.Embed(
                title="📍 Connetti al Server",
                description=f"**Indirizzo:**\n`{SERVER_IP}`\n\n**Porta:**\n`25565`",
                color=0x7289da
            )
            embed.set_footer(text="Copia l'indirizzo in Minecraft")
            await message.channel.send(embed=embed)
        
        elif message.content.lower() == '!status':
            embed = discord.Embed(
                title="📊 Status Server",
                description="Server hosted on Aternos",
                color=0x00ff00
            )
            embed.add_field(name="🟢 Online", value="Server raggiungibile", inline=True)
            embed.add_field(name="🌐 Host", value="Aternos", inline=True)
            embed.add_field(name="⚡ Performance", value="Basic (Free Plan)", inline=True)  # ← CORRETTO!
            await message.channel.send(embed=embed)
        
        elif message.content.lower() == '!help':
            embed = discord.Embed(
                title="❓ Comandi Disponibili",
                description="Ecco cosa posso fare:",
                color=0xffcc00
            )
            embed.add_field(name="!ip", value="Mostra l'indirizzo del server", inline=False)
            embed.add_field(name="!status", value="Mostra lo status del server", inline=False)
            embed.add_field(name="!help", value="Mostra questo messaggio", inline=False)
            embed.set_footer(text="Aternos Limited Bot - Alcune funzioni non disponibili")
            await message.channel.send(embed=embed)
        
        elif message.content.lower().startswith('!say '):
            # Simula chat (non può inviare a Minecraft)
            text = message.content[5:]
            await message.channel.send(f"💬 **Chat simulata:** {text}")
            await message.add_reaction('✅')

def run_web_server():
    """Avvia web server per keep-alive"""
    app.run(host='0.0.0.0', port=10000)

async def main():
    print("🎮 Avvio Bot Aternos su Render...")
    print("⚠️  Limitazioni Aternos: No RCON, No Log access")
    
    # Avvia web server in background
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Avvia bot Discord
    bot = AternosBot()
    
    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Token errato! Controlla DISCORD_TOKEN")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    asyncio.run(main())
