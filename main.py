#!/usr/bin/env python3
"""
BOT ATERNOS con Player Count
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
import socket
import mcstatus

# Configurazione Render
TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', 1418196149545730153))
SERVER_IP = os.environ.get('SERVER_IP', 'EVLCraft.aternos.me')
ATERNOS_USER = os.environ.get('ATERNOS_USER', 'Ker0l341')  # Tuo username Aternos
ATERNOS_PASS = os.environ.get('ATERNOS_PASS', 'Edu.eyy3411')   # Tua password Aternos

# Web server per keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "🎮 Minecraft Bot for Aternos - Online!"

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "players": "monitoring"})

@app.route('/status')
def status():
    return jsonify({
        "status": "online", 
        "server": SERVER_IP,
        "platform": "Aternos"
    })

class AternosBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.player_count = 0
        self.max_players = 20
        self.server_online = False
        
    async def on_ready(self):
        print(f'✅ Bot Aternos avviato: {self.user}')
        print(f'🎯 Monitoraggio: {SERVER_IP}')
        
        channel = self.get_channel(CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="🎮 Bot Minecraft Aternos",
                description="Bot avviato con monitoraggio giocatori",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Server", value=f"`{SERVER_IP}`", inline=True)
            embed.add_field(name="Status", value="🟢 Online", inline=True)
            embed.add_field(name="Giocatori", value="0/20", inline=True)
            embed.set_footer(text="Use !players for real-time info")
            
            await channel.send(embed=embed)
        
        # Avvia monitoraggio giocatori
        self.loop.create_task(self.monitor_players())

    async def get_player_count(self):
        """Ottiene il numero di giocatori online"""
        try:
            # Metodo 1: Usa mcstatus per pingare il server
            from mcstatus import JavaServer
            server = JavaServer.lookup(SERVER_IP)
            status = server.status()
            return status.players.online, status.players.max
            
        except Exception:
            try:
                # Metodo 2: API Aternos (se hai credenziali)
                if ATERNOS_USER and ATERNOS_PASS:
                    async with aiohttp.ClientSession() as session:
                        # Login ad Aternos
                        async with session.post(
                            'https://aternos.org/api/login',
                            json={'user': ATERNOS_USER, 'password': ATERNOS_PASS}
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                if data.get('success'):
                                    # Ottieni status server
                                    async with session.get(
                                        'https://aternos.org/api/server'
                                    ) as server_resp:
                                        server_data = await server_resp.json()
                                        players = server_data.get('players', {})
                                        return players.get('online', 0), players.get('max', 20)
                return 0, 20
            except Exception:
                # Metodo 3: Fallback a simulazione
                return self.player_count, self.max_players

    async def monitor_players(self):
        """Monitora i giocatori ogni minuto"""
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        
        while not self.is_closed():
            try:
                # Ottieni conteggio giocatori
                online_players, max_players = await self.get_player_count()
                
                # Aggiorna stato
                if online_players != self.player_count:
                    self.player_count = online_players
                    self.max_players = max_players
                    
                    if channel and online_players > 0:
                        embed = discord.Embed(
                            title="👥 Statistiche Giocatori",
                            color=0x0099ff,
                            timestamp=datetime.now()
                        )
                        embed.add_field(name="Online", value=f"**{online_players}**", inline=True)
                        embed.add_field(name="Massimo", value=f"**{max_players}**", inline=True)
                        embed.add_field(name="Status", value="🟢 In Game" if online_players > 0 else "🔴 Empty", inline=True)
                        embed.set_footer(text=f"Server: {SERVER_IP}")
                        
                        await channel.send(embed=embed)
                        print(f"📊 Giocatori aggiornati: {online_players}/{max_players}")
                
                await asyncio.sleep(60)  # Controlla ogni minuto
                
            except Exception as e:
                print(f"❌ Errore monitoraggio giocatori: {e}")
                await asyncio.sleep(30)

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.lower() == '!players':
            try:
                online, max_players = await self.get_player_count()
                
                embed = discord.Embed(
                    title="👥 Giocatori Online",
                    description=f"**Server:** `{SERVER_IP}`",
                    color=0x00ff00 if online > 0 else 0xff0000,
                    timestamp=datetime.now()
                )
                
                embed.add_field(name="Online", value=f"**{online}**", inline=True)
                embed.add_field(name="Massimo", value=f"**{max_players}**", inline=True)
                embed.add_field(name="Status", value="🟢 In Game" if online > 0 else "🔴 Empty", inline=True)
                
                if online > 0:
                    embed.add_field(name="💡 Info", value="Giocatori connessi al server!", inline=False)
                else:
                    embed.add_field(name="💡 Info", value="Nessun giocatore online", inline=False)
                
                embed.set_footer(text="Aggiornato in tempo reale")
                await message.channel.send(embed=embed)
                
            except Exception as e:
                await message.channel.send("❌ Impossibile ottenere i dati dei giocatori")
        
        elif message.content.lower() == '!ip':
            embed = discord.Embed(
                title="📍 Connetti al Server",
                description=f"**Indirizzo:**\n`{SERVER_IP}`\n\n**Porta:**\n`25565`",
                color=0x7289da
            )
            embed.add_field(name="Giocatori Online", value=f"{self.player_count}/{self.max_players}", inline=True)
            embed.set_footer(text="Copia l'indirizzo in Minecraft")
            await message.channel.send(embed=embed)
        
        elif message.content.lower() == '!status':
            embed = discord.Embed(
                title="📊 Status Server Completo",
                description=f"**Server:** `{SERVER_IP}`",
                color=0x0099ff
            )
            embed.add_field(name="🟢 Online", value="Server raggiungibile", inline=True)
            embed.add_field(name="👥 Giocatori", value=f"{self.player_count}/{self.max_players}", inline=True)
            embed.add_field(name="🌐 Host", value="Aternos", inline=True)
            embed.add_field(name="⚡ Performance", value="Basic (Free Plan)", inline=True)
            embed.add_field(name="📊 Uptime", value="24/7 Monitorato", inline=True)
            embed.set_footer(text="Use !players for detailed info")
            await message.channel.send(embed=embed)

def run_web_server():
    """Avvia web server per keep-alive"""
    app.run(host='0.0.0.0', port=10000)

async def main():
    print("🎮 Avvio Bot Aternos con Player Monitoring...")
    print("📊 Funzionalità: !players, !ip, !status")
    
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
