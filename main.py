#!/usr/bin/env python3
"""
BOT ATERNOS con Welcome Message Temporaneo
"""
import discord
import asyncio
import aiohttp
import os
import json
from datetime import datetime
from flask import Flask, jsonify
from threading import Thread
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
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # Necessario per vedere i membri
        super().__init__(intents=intents)
        self.player_count = 0
        self.max_players = 20
        self.server_online = False
        self.last_players = set()
        self.welcome_messages = {}
        
    async def on_ready(self):
        print(f'✅ Bot Aternos avviato: {self.user}')
        print(f'🎯 Monitoraggio: {SERVER_IP}')
        print(f'👋 Welcome messages attivi sul canale: {WELCOME_CHANNEL_ID}')
        
        # Avvia monitoraggio giocatori e welcome messages
        self.loop.create_task(self.monitor_players_and_welcome())

    async def get_player_list(self):
        """Ottiene la lista dei giocatori online"""
        try:
            server = JavaServer.lookup(SERVER_IP)
            status = server.status()
            
            # Prova a ottenere la lista giocatori (se supportato)
            try:
                query = server.query()
                return query.players.names, status.players.online, status.players.max
            except:
                # Fallback a solo conteggio
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
            
            # Crea messaggio di benvenuto con tag
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
            
            # Invia il messaggio
            welcome_msg = await channel.send(embed=embed)
            print(f"👋 Welcome message inviato per {player_name}")
            
            # Programma l'eliminazione dopo 10 secondi
            await asyncio.sleep(10)
            try:
                await welcome_msg.delete()
                print(f"🗑️ Messaggio eliminato per {player_name}")
            except discord.NotFound:
                print(f"⚠️ Messaggio già eliminato per {player_name}")
            except Exception as e:
                print(f"❌ Errore eliminazione messaggio: {e}")
                
        except Exception as e:
            print(f"❌ Errore invio welcome: {e}")

    async def monitor_players_and_welcome(self):
        """Monitora i giocatori e invia welcome messages"""
        await self.wait_until_ready()
        
        while not self.is_closed():
            try:
                # Ottieni lista giocatori attuali
                current_players, online_count, max_players = await self.get_player_list()
                current_set = set(current_players)
                
                # Aggiorna conteggi
                self.player_count = online_count
                self.max_players = max_players
                
                # Trova nuovi giocatori
                new_players = current_set - self.last_players
                
                # Invia welcome messages per nuovi giocatori
                for player in new_players:
                    print(f"🎮 Nuovo giocatore rilevato: {player}")
                    self.loop.create_task(self.send_temp_welcome(player))
                
                # Aggiorna ultima lista
                self.last_players = current_set
                
                await asyncio.sleep(30)  # Controlla ogni 30 secondi
                
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
                    color=0x00ff00 if online > 0 else 0xff0000,
                    timestamp=datetime.now()
                )
                
                if players_list:
                    players_text = "\n".join([f"• {player}" for player in players_list])
                    embed.add_field(name="Giocatori Connessi", value=players_text, inline=False)
                else:
                    embed.add_field(name="Giocatori", value="Nessun giocatore online", inline=False)
                
                embed.add_field(name="Online", value=f"**{online}**", inline=True)
                embed.add_field(name="Massimo", value=f"**{max_players}**", inline=True)
                embed.set_footer(text="Aggiornato in tempo reale")
                
                await message.channel.send(embed=embed)
                
            except Exception as e:
                await message.channel.send("❌ Impossibile ottenere la lista giocatori")
        
        elif message.content.lower() == '!welcome':
            """Comando per testare il welcome message"""
            try:
                test_player = "TestPlayer"
                await message.channel.send(f"🧪 Test welcome message per {test_player}...")
                await self.send_temp_welcome(test_player)
            except Exception as e:
                await message.channel.send(f"❌ Errore test: {e}")
        
        elif message.content.lower() == '!ip':
            embed = discord.Embed(
                title="📍 Connetti al Server",
                description=f"**Indirizzo:**\n`{SERVER_IP}`\n\n**Porta:**\n`25565`",
                color=0x7289da
            )
            embed.add_field(name="Giocatori Online", value=f"{self.player_count}/{self.max_players}", inline=True)
            embed.set_footer(text="Copia l'indirizzo in Minecraft")
            await message.channel.send(embed=embed)

def run_web_server():
    """Avvia web server per keep-alive"""
    app.run(host='0.0.0.0', port=10000)

async def main():
    print("🎮 Avvio Bot Aternos con Welcome Messages...")
    print("👋 Messaggi temporanei attivi per nuovi giocatori")
    
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
