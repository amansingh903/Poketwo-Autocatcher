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
import logging

# Moel Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
spam_task = None
BOT_AUTHOR_ID = 716390085896962058

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

with open('bot/data.txt', 'r', encoding='utf-8') as file:
    pokemon_names = [line.strip() for line in file if line.strip()]

async def spam():
    global sleeping
    while not sleeping:
        channel = bot.get_channel(config.SpamId)
        if channel:
            result = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=13))
            await channel.send(result)
        random_interval = random.uniform(1, 4)
        await asyncio.sleep(random_interval)


def in_owner_scope(msg: discord.Message) -> bool:
    return bool(msg.guild and msg.author.id == config.OwnerId and msg.guild.id == config.GuildId)


def should_process_guild_message(msg: discord.Message) -> bool:
    return bool(msg.guild and msg.guild.id == config.GuildId)


def ensure_spam_task() -> None:
    global spam_task
    if config.SpamId and not sleeping and (spam_task is None or spam_task.done()):
        spam_task = asyncio.create_task(spam())
        logger.info("Spammer task started.")

@bot.event
async def on_ready():
    print(f'\033[91mLOGGED IN AS {bot.user.name} ({bot.user.id})\033[0m')
    print(f'\033[91mSERVER STATUS: ONLINE\033[0m')
    print(f'\033[91mMade by https://github.com/amansingh903\033[0m')
    print(f'\033[91m------------------------------------------------------------------------------------------\033[0m')
    ensure_spam_task()

@bot.event
async def on_message(msg: discord.Message):
    global sleeping

    if msg.author.id == bot.user.id:
        return

    if not should_process_guild_message(msg):
        return

    # Pre-checks for images
    attachment = None
    if msg.attachments:
        attachment = msg.attachments[0]
        if not any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
            attachment = None

    message = msg.content

    try:
        # say function
        if in_owner_scope(msg):
            if '!say' in message:
                pattern = r'^!say (.*)'
                msgWithoutSay = re.findall(pattern, message)
                if msgWithoutSay:
                    await msg.channel.send(f'{msgWithoutSay[0]}')

        # Solved captcha
        if in_owner_scope(msg):
            if message == '!solved':
                sleeping = False
                logger.info("Spammer resumed.")
                ensure_spam_task()

        # Try with ai
        if msg.author.id == BOT_AUTHOR_ID:
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
                                async with session.get(embed.image.url, timeout=10) as resp:
                                    resp.raise_for_status()
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

                    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, OSError) as e:
                        logger.warning("Error processing image: %s", e)
                        await msg.channel.send(f'<@716390085896962058> h')

        # catch function if ai fails (Hint Solving)
        if msg.content.startswith('The pokémon is ') and msg.channel.id == config.CatchId:
            cleaned_hint = msg.content.replace('The pokémon is ', '').replace('\\', '').replace('_', '.')
            if cleaned_hint.endswith('.'):
                cleaned_hint = cleaned_hint[:-1]

            for pokemon_from_file in pokemon_names:
                if re.fullmatch(cleaned_hint, pokemon_from_file, re.IGNORECASE):
                    await msg.channel.send(f'c {pokemon_from_file}')
                    logger.info('Caught via hint: %s', pokemon_from_file)
                    break


        # logging
        if msg.content.startswith('Congratulations') and msg.author.id == BOT_AUTHOR_ID:
            match = re.search(r"Level\s+\d+\s+([A-Za-z\-\s]+?)(?=<|\s+\()", msg.content)
            if match:
                pokemon_name = match.group(1)
                logger.info('Caught %s', pokemon_name)
        

        # captcha function
        if msg.content.startswith('Please tell us') and msg.author.id == BOT_AUTHOR_ID:
            sleeping = True
            logger.warning('Captcha Found - Spammer Stopped')
        

        # fallback to hint incase of incorrect guess
        if msg.content.startswith('That is the wrong') and msg.author.id == BOT_AUTHOR_ID:
            logger.info("Incorrect guess, falling back to hint")
            await msg.channel.send(f'<@716390085896962058> h')


        # react function
        if in_owner_scope(msg):
            if '!react' in message:
                reactionpattern = r"!react (\d*) (.*)"
                temp = re.search(reactionpattern, message)
                if temp:
                    messageId = temp.group(1)
                    emoji = temp.group(2)

    except (AttributeError, RuntimeError, ValueError) as e:
        logger.exception("General runtime error in on_message: %s", e)

bot.run(config.token)
