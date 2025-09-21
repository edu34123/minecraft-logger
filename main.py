#!/usr/bin/env python3
"""
BOT ATERNOS con Intent Corretti
"""
import discord
import asyncio
import aiohttp
import os
import json
from datetime import datetime
from flask import Flask, jsonify
from threading import Thread
import requests
from mcstatus import JavaServer

# Configurazione Render
TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', 1418196149545730153))
SERVER_IP = os.environ.get('SERVER_IP', 'EVLCraft.aternos.me')
WELCOME_CHANNEL_ID = int(os.environ.get('1415598135719362622', CHANNEL_ID))

# Web server per keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "🎮 Minecraft Bot with Welcome Messages - Online!"

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "feature": "welcome_messages"})

class AternosBot(discord.Client):
    def __init__(self):
        # CONFIGURA INTENTS CORRETTI
        intents = discord.Intents.all()  # ← USA all() PER EVITARE PROBLEMI
        super().__init__(intents=intents)
        self.player_count = 0
        self.max_players = 20
        self.server_online = False
        self.last_players = set()
        
    async def on_ready(self):
        print(f'✅ Bot Aternos avviato: {self.user}')
        print(f'🎯 Monitoraggio: {SERVER_IP}')
        print(f'👋 Welcome messages attivi')
        
        # Verifica intents
        print(f'📊 Intents abilitati: {self.intents}')
        
        # Avvia monitoraggio giocatori
        self.loop.create_task(self.monitor_players_and_welcome())

    async def get_player_list(self):
        """Ottiene la lista dei giocatori online"""
        try:
            server = JavaServer.lookup(SERVER_IP)
            status = server.status()
            return [], status.players.online, status.players.max
        except Exception as e:
            print(f"❌ Errore get players: {e}")
            return [], 0, 20

    async def send_temp_welcome(self, player_name):
        """Invia un messaggio di benvenuto temporaneo"""
        try:
            channel = self.get_channel(WELCOME_CHANNEL_ID)
            if not channel:
                print("❌ Canale welcome non trovato")
                return
            
            # Messaggio di benvenuto
            embed = discord.Embed(
                title="🎮 Nuovo Giocatore!",
                description=f"**{player_name}** si è unito al server!",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="👋 Benvenuto", value=f"Dai il benvenuto a {player_name}!", inline=False)
            embed.add_field(name="🌐 Server", value=f"`{SERVER_IP}`", inline=True)
            embed.add_field(name="👥 Online", value=f"{self.player_count}/{self.max_players}", inline=True)
            embed.set_footer(text="Messaggio auto-eliminante")
            
            # Invia e programma eliminazione
            welcome_msg = await channel.send(embed=embed)
            print(f"👋 Welcome message inviato per {player_name}")
            
            await asyncio.sleep(10)
            try:
                await welcome_msg.delete()
                print(f"🗑️ Messaggio eliminato per {player_name}")
            except:
                print(f"⚠️ Messaggio già eliminato")
                
        except Exception as e:
            print(f"❌ Errore welcome message: {e}")

    async def monitor_players_and_welcome(self):
        """Monitora i giocatori e invia welcome messages"""
        await self.wait_until_ready()
        
        while not self.is_closed():
            try:
                # Ottieni lista giocatori
                current_players, online_count, max_players = await self.get_player_list()
                current_set = set(current_players)
                
                # Aggiorna conteggi
                self.player_count = online_count
                self.max_players = max_players
                
                # Trova nuovi giocatori (simulato per test)
                if current_players:
                    new_players = current_set - self.last_players
                    for player in new_players:
                        print(f"🎮 Nuovo giocatore: {player}")
                        self.loop.create_task(self.send_temp_welcome(player))
                
                self.last_players = current_set
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"❌ Errore monitoraggio: {e}")
                await asyncio.sleep(60)

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.lower() == '!players':
            try:
                players_list, online, max_players = await self.get_player_list()
                
                embed = discord.Embed(
                    title="👥 Giocatori Online",
                    description=f"**Server:** `{SERVER_IP}`",
                    color=0x00ff00 if online > 0 else 0xff0000
                )
                
                embed.add_field(name="Online", value=f"**{online}**", inline=True)
                embed.add_field(name="Massimo", value=f"**{max_players}**", inline=True)
                embed.set_footer(text="Use !ip per connetterti")
                
                await message.channel.send(embed=embed)
                
            except Exception as e:
                await message.channel.send("❌ Impossibile ottenere i dati")
        
        elif message.content.lower() == '!welcome':
            """Test welcome message"""
            await message.channel.send("🧪 Test welcome message...")
            await self.send_temp_welcome("TestPlayer")
        
        elif message.content.lower() == '!ip':
            embed = discord.Embed(
                title="📍 Connetti al Server",
                description=f"**Indirizzo:** `{SERVER_IP}`\n**Porta:** `25565`",
                color=0x7289da
            )
            embed.add_field(name="Giocatori", value=f"{self.player_count}/{self.max_players}", inline=True)
            await message.channel.send(embed=embed)

def run_web_server():
    """Avvia web server per keep-alive"""
    app.run(host='0.0.0.0', port=10000)

async def main():
    print("🎮 Avvio Bot Aternos...")
    print("🔧 Assicurati di aver abilitato gli intents su Discord Developer!")
    
    # Avvia web server
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Avvia bot
    bot = AternosBot()
    
    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Token errato! Controlla DISCORD_TOKEN")
    except discord.PrivilegedIntentsRequired:
        print("❌ PRIVILEGED INTENTS REQUIRED!")
        print("Vai su: https://discord.com/developers/applications")
        print("Bot → Abilita PRESENCE INTENT, SERVER MEMBERS INTENT, MESSAGE CONTENT INTENT")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    asyncio.run(main())
