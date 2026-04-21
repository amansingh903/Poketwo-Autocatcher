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
from pathlib import Path
from datetime import datetime, timezone

# Moel Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load names and model
CLASS_NAMES_PATH = Path("bot/class_names.json")
MODEL_PATH = Path("bot/pokemon_model_lite.pth")
if not CLASS_NAMES_PATH.exists():
    raise FileNotFoundError(f"Missing class names file: {CLASS_NAMES_PATH}")
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Missing model file: {MODEL_PATH}")

with open(CLASS_NAMES_PATH, 'r') as f:
    class_names = json.load(f)

model = models.mobilenet_v3_small()
num_ftrs = model.classifier[3].in_features
model.classifier[3] = nn.Linear(num_ftrs, len(class_names))
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
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
http_session = None
STATE_PATH = Path(config.StateFilePath)
last_catch_attempt_ts = 0.0
last_hint_request_ts = 0.0
last_captcha_ts = None
last_caught_name = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

with open('bot/data.txt', 'r', encoding='utf-8') as file:
    pokemon_names = [line.strip() for line in file if line.strip()]


def load_runtime_state() -> None:
    global sleeping, last_captcha_ts, last_caught_name
    if not STATE_PATH.exists():
        return
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as state_file:
            state = json.load(state_file)
        sleeping = bool(state.get("sleeping", sleeping))
        last_captcha_ts = state.get("last_captcha_ts")
        last_caught_name = state.get("last_caught_name")
        logger.info("Loaded runtime state from %s", STATE_PATH)
    except (OSError, ValueError) as exc:
        logger.warning("Failed to load runtime state: %s", exc)


def save_runtime_state() -> None:
    state = {
        "sleeping": sleeping,
        "last_captcha_ts": last_captcha_ts,
        "last_caught_name": last_caught_name,
    }
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_PATH, "w", encoding="utf-8") as state_file:
            json.dump(state, state_file, ensure_ascii=True, indent=2)
    except OSError as exc:
        logger.warning("Failed to save runtime state: %s", exc)


async def send_with_cooldown(
    channel: discord.abc.Messageable,
    content: str,
    cooldown_seconds: float,
    timestamp_attr: str,
) -> None:
    global last_catch_attempt_ts, last_hint_request_ts
    now = asyncio.get_running_loop().time()
    last_ts = last_catch_attempt_ts if timestamp_attr == "catch" else last_hint_request_ts
    wait_for = cooldown_seconds - (now - last_ts)
    if wait_for > 0:
        await asyncio.sleep(wait_for)
    await channel.send(content)
    if timestamp_attr == "catch":
        last_catch_attempt_ts = asyncio.get_running_loop().time()
    else:
        last_hint_request_ts = asyncio.get_running_loop().time()


async def fetch_image_with_retry(url: str, retries: int = 3, base_delay: float = 0.5) -> bytes:
    session = await get_http_session()
    last_error = None
    for attempt in range(retries):
        try:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.read()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            last_error = exc
            if attempt == retries - 1:
                break
            await asyncio.sleep(base_delay * (2 ** attempt))
    raise RuntimeError(f"Failed to fetch image after retries: {last_error}")


def validate_startup() -> None:
    if not (0 < config.AiConfidenceThreshold <= 1):
        raise ValueError("AI_CONFIDENCE_THRESHOLD must be between 0 and 1.")
    if not CLASS_NAMES_PATH.exists():
        raise FileNotFoundError(f"Missing class names file: {CLASS_NAMES_PATH}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing model file: {MODEL_PATH}")
    if model.classifier[3].out_features != len(class_names):
        raise RuntimeError("Model output size does not match class_names count.")
    if config.StateFilePath.strip() == "":
        raise ValueError("STATE_FILE_PATH cannot be empty.")


async def get_http_session() -> aiohttp.ClientSession:
    global http_session
    if http_session is None or http_session.closed:
        http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
    return http_session

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
    print(f'\033[91mVISIT https://github.com/amansingh903\033[0m')
    print(f'\033[91m------------------------------------------------------------------------------------------\033[0m')
    load_runtime_state()
    await get_http_session()
    ensure_spam_task()


@bot.event
async def on_disconnect():
    global http_session, spam_task
    if spam_task and not spam_task.done():
        spam_task.cancel()
        spam_task = None
    if http_session and not http_session.closed:
        await http_session.close()
        http_session = None
    save_runtime_state()

@bot.event
async def on_message(msg: discord.Message):
    global sleeping, last_captcha_ts, last_caught_name

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
                save_runtime_state()
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
                            img_bytes = await fetch_image_with_retry(embed.image.url)
                        else:
                            raise ValueError("No image found")

                        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                        img_tensor = bot_transform(img).unsqueeze(0).to(device)
                        
                        with torch.no_grad():
                            outputs = model(img_tensor)
                            probs = torch.nn.functional.softmax(outputs, dim=1)
                            _, idx = torch.max(probs, 1)
                            confidence = probs[0][idx.item()].item()
                        
                        pokemon_name = class_names[idx.item()]
                        if confidence < config.AiConfidenceThreshold:
                            logger.info(
                                "Low confidence prediction %.3f for %s, requesting hint.",
                                confidence,
                                pokemon_name,
                            )
                            await send_with_cooldown(
                                msg.channel,
                                f'<@{BOT_AUTHOR_ID}> h',
                                config.HintCooldownSeconds,
                                "hint",
                            )
                        else:
                            random_interval = random.uniform(0.5, 2)
                            await asyncio.sleep(random_interval)
                            await send_with_cooldown(
                                msg.channel,
                                f'<@{BOT_AUTHOR_ID}> c {pokemon_name}',
                                config.CatchCooldownSeconds,
                                "catch",
                            )

                    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, OSError, RuntimeError) as e:
                        logger.warning("Error processing image: %s", e)
                        await send_with_cooldown(
                            msg.channel,
                            f'<@{BOT_AUTHOR_ID}> h',
                            config.HintCooldownSeconds,
                            "hint",
                        )

        # catch function if ai fails (Hint Solving)
        if msg.content.startswith('The pokémon is ') and msg.channel.id == config.CatchId:
            cleaned_hint = msg.content.replace('The pokémon is ', '').replace('\\', '').replace('_', '.')
            if cleaned_hint.endswith('.'):
                cleaned_hint = cleaned_hint[:-1]

            for pokemon_from_file in pokemon_names:
                if re.fullmatch(cleaned_hint, pokemon_from_file, re.IGNORECASE):
                    await send_with_cooldown(
                        msg.channel,
                        f'c {pokemon_from_file}',
                        config.CatchCooldownSeconds,
                        "catch",
                    )
                    logger.info('Caught via hint: %s', pokemon_from_file)
                    break


        # logging
        if msg.content.startswith('Congratulations') and msg.author.id == BOT_AUTHOR_ID:
            match = re.search(r"Level\s+\d+\s+([A-Za-z\-\s]+?)(?=<|\s+\()", msg.content)
            if match:
                pokemon_name = match.group(1)
                last_caught_name = pokemon_name
                save_runtime_state()
                logger.info('Caught %s', pokemon_name)
        

        # captcha function
        if msg.content.startswith('Please tell us') and msg.author.id == BOT_AUTHOR_ID:
            sleeping = True
            last_captcha_ts = datetime.now(timezone.utc).isoformat()
            save_runtime_state()
            logger.warning('Captcha Found - Spammer Stopped')
        

        # fallback to hint incase of incorrect guess
        if msg.content.startswith('That is the wrong') and msg.author.id == BOT_AUTHOR_ID:
            logger.info("Incorrect guess, falling back to hint")
            await send_with_cooldown(
                msg.channel,
                f'<@{BOT_AUTHOR_ID}> h',
                config.HintCooldownSeconds,
                "hint",
            )


        # react function
        if in_owner_scope(msg):
            if '!react' in message:
                reactionpattern = r"!react (\d*) (.*)"
                temp = re.search(reactionpattern, message)
                if temp:
                    messageId = int(temp.group(1))
                    emoji = temp.group(2)
                    target_message = await msg.channel.fetch_message(messageId)
                    await target_message.add_reaction(emoji)
                    logger.info("Added reaction %s to message %s", emoji, messageId)

    except (AttributeError, RuntimeError, ValueError, discord.DiscordException) as e:
        logger.exception("General runtime error in on_message: %s", e)

validate_startup()
bot.run(config.token)
