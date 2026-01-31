import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import json
import discord
from discord.ext import commands
import config
import re
import asyncio
import random
import aiohttp 

# Moel Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#webhook
if config.webhook:
    LOG_WEBHOOK_URL = config.webhook


async def log_catch(pokemon_name, level, percentage):
    async with aiohttp.ClientSession() as session:
        payload = {
            "embeds": [{
                "title": "✅ Pokémon Caught!",
                "description": f"Successfully caught **{pokemon_name}**",
                "fields": [
                    {"name": "Level", "value": str(level), "inline": True},
                    {"name": "IV", "value": f"{percentage}%", "inline": True}
                ],
                "color": 3066993 # Green color
            }]
        }
        await session.post(LOG_WEBHOOK_URL, json=payload)


async def log_catch_rare(pokemon_name, level, percentage):
    async with aiohttp.ClientSession() as session:
        payload = {
            "embeds": [{
                "title": "✅ Rare Pokémon Caught!",
                "description": f"Successfully caught **{pokemon_name}**",
                "fields": [
                    {"name": "Level", "value": str(level), "inline": True},
                    {"name": "IV", "value": f"{percentage}%", "inline": True}
                ],
                "color": 3066993 # Green color
            }]
        }
        await session.post(LOG_WEBHOOK_URL, json=payload)


# Load names and model
with open('bot/class_names.json', 'r') as f:
    class_names = json.load(f)

model = models.mobilenet_v3_small()
num_ftrs = model.classifier[3].in_features
model.classifier[3] = nn.Linear(num_ftrs, len(class_names))
model.load_state_dict(torch.load(r'bot\pokemon_model_lite.pth', map_location=device))
model.to(device)
model.eval()

# Transform
bot_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

bot = commands.Bot(command_prefix="!", self_bot=True)
sleeping = config.sleep

async def spam():
    global sleeping
    while sleeping == False:
        channel = bot.get_channel(config.SpamId)
        if channel:
            result = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=13))
            await channel.send(result)
        random_interval = random.uniform(1, 4)
        await asyncio.sleep(random_interval)

@bot.event
async def on_ready():
    print(f'\033[91mLOGGED IN AS {bot.user.name} ({bot.user.id})\033[0m')
    print(f'\033[91mSERVER STATUS: ONLINE\033[0m')
    print(f'\033[91mMade by https://github.com/amansingh903\033[0m')
    print(f'\033[91m------------------------------------------------------------------------------------------\033[0m')
    if config.SpamId:
        await spam()

@bot.event
async def on_message(msg: discord.Message):
    # Pre-checks for images
    attachment = None
    if msg.attachments:
        attachment = msg.attachments[0]
        if not any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
            attachment = None

    message = msg.content

    try:
        # say function
        if msg.author.id == config.OwnerId and msg.guild.id == config.GuildId:
            if '!say' in message:
                pattern = r'^!say (.*)'
                msgWithoutSay = re.findall(pattern, message)
                if msgWithoutSay:
                    await msg.channel.send(f'{msgWithoutSay[0]}')

        # Solved captcha
        if msg.author.id == config.OwnerId and msg.guild.id == config.GuildId:
            if message == '!solved':
                sleeping = False
                print("Spammer resumed.")
                await spam() # Restart spammer if it stopped

        # Try with ai
        if msg.author.id == 716390085896962058 and msg.guild.id == config.GuildId:
            if len(msg.embeds) > 0:
                embed = msg.embeds[0]
                dictio = embed.to_dict()
                title = dictio.get('title', '')
                
                if "wild pokémon has appeared!" in title.lower():
                    try:
                        if attachment:
                            img_bytes = await attachment.read()
                        elif embed.image:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(embed.image.url) as resp:
                                    img_bytes = await resp.read()
                        else:
                            raise ValueError("No image found")

                        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                        img_tensor = bot_transform(img).unsqueeze(0).to(device)
                        
                        with torch.no_grad():
                            outputs = model(img_tensor)
                            probs = torch.nn.functional.softmax(outputs, dim=1)
                            _, idx = torch.max(probs, 1)
                        
                        pokemon_name = class_names[idx.item()]
                        random_interval = random.uniform(0.5, 2)
                        await asyncio.sleep(random_interval)
                        await msg.channel.send(f'<@716390085896962058> c {pokemon_name}')

                    except Exception as e:
                        print(f"Error processing image: {e}")
                        await msg.channel.send(f'<@716390085896962058> h')


        # catch function if ai fails (Hint Solving)
        if msg.content.startswith('The pokémon is ') and msg.channel.id == config.CatchId:
            cleaned_hint = msg.content.replace('The pokémon is ', '').replace('\\', '').replace('_', '.')
            if cleaned_hint.endswith('.'):
                cleaned_hint = cleaned_hint[:-1]

            with open('bot/data.txt', 'r', encoding='utf-8') as file:
                for line in file:
                    pokemon_from_file = line.strip()
                    if re.fullmatch(cleaned_hint, pokemon_from_file, re.IGNORECASE):
                        await msg.channel.send(f'c {pokemon_from_file}')
                        print(f'Caught via hint: {pokemon_from_file}')
                        break


        # logging
        if "You caught a Level" in msg.content:
            match = re.search(r"Level\s+(\d+)\s+([A-Za-z\-\s]+?)(?=<|\s+\()", msg.content)
            perc_match = re.search(r"\((\d+\.\d+)%\)", msg.content)
    
            if match and perc_match:
                lvl = match.group(1)
                name = match.group(2).strip()
                perc = perc_match.group(1)
                
                
            with open('bot/rares.txt', 'r', encoding='utf-8') as check_rares:
                if name in check_rares.read().splitlines():
                    print(f'\033[93mRARE CAUGHT: {name} | LEVEL: {lvl} | IV: {perc}%\033[0m')
                    await msg.channel.send(f'<@{config.OwnerId}>')
                    # Trigger the log
                    await log_catch_rare(name, lvl, perc)
                else:
                    # Trigger the log for rares
                    await log_catch(name, lvl, perc)
                    
        

        # captcha function
        if msg.content.startswith('Please tell us') and msg.author.id == 716390085896962058:
            sleeping = True
            print('\033[91mCaptcha Found - Spammer Stopped\033[0m')
        

        # fallback to hint incase of incorrect guess
        if msg.content.startswith('That is the wrong') and msg.author.id == 716390085896962058:
            print(f"Incorrect guess, falling back to hint")
            await msg.channel.send(f'<@716390085896962058> h')


        # react function
        if msg.author.id == config.OwnerId and msg.guild.id == config.GuildId:
            if '!react' in message:
                reactionpattern = r"!react (\d*) (.*)"
                temp = re.search(reactionpattern, message)
                if temp:
                    messageId = temp.group(1)
                    emoji = temp.group(2)
                    

    except Exception as e:
        print(f"General error: {e}")
        pass

bot.run(config.token)
