import discord
from discord.ext import commands
import config
import re
import asyncio
import random
from threading import Timer



# Set the command prefix for your selfbot
bot = commands.Bot(command_prefix="!", self_bot=True)
sleeping=config.sleep


async def spam():
    while sleeping==False:
        channel = bot.get_channel(config.SpamId)
        result = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=13))
        await channel.send(result)
        random_interval = random.uniform(1, 4)  # Random interval between 1 second and 5 seconds
        await asyncio.sleep(random_interval)





@bot.event
async def on_ready():
    print(f'\033[91mLOGGED IN AS {bot.user.name} ({bot.user.id})\033[0m')
    print(f'\033[91mSERVER STATUS: ONLINE\033[0m')
    print(f'\033[91mMade by amansingh903\033[0m')
    print(f'\033[91m------------------------------------------------------------------------------------------\033[0m')
    #spam function
    if config.SpamId:
        await spam()
        





@bot.event
async def on_message(msg: discord.Message):
    message = msg.content
    try :


        #say function
        if msg.author.id == config.OwnerId and msg.guild.id== config.GuildId:
            if '!say' in message:
                pattern = r'^!say (.*)'
                msgWithoutSay = re.findall(pattern,message)
                await msg.channel.send(f'{msgWithoutSay[0]}')
        
        
        #solved function
        if msg.author.id == config.OwnerId and msg.guild.id== config.GuildId:
            if message == '!solved':
                sleeping=False


        #hint function
        if msg.author.id == 716390085896962058 and msg.guild.id== config.GuildId:
            if len(msg.embeds) > 0:
                embeds = msg.embeds
                for embed in embeds:
                    dictio = embed.to_dict()
                title = dictio['title']
                if (("wild pokémon has appeared!" in title) == True):
                    hint = ["hint", "h"]
                    random_hint=hint[random.randint(0,1)]
                    await msg.channel.send(f'<@716390085896962058> {random_hint}')


        #catch function
        if (msg.content.startswith('The pokémon is ') and msg.channel.id ==config.CatchId):
            catchpattern = r'^The pokémon is (.*).$'
            hint = re.findall(catchpattern,message)
            temp=hint[0]
            temp2 = re.sub(r'_','.',temp)
            cleaned_text = temp2.replace(r'\.','.')
            with open('data.txt', 'r',encoding='utf-8') as file:
                for line in file:
                    line = line.rstrip()
                    match = re.search(cleaned_text, line)
                    if match:  
                        await msg.channel.send(f'<@716390085896962058> c {match.group(0)}')
                        print(f'Caught a {match.group(0)}')


        #captcha function
        if (msg.content.startswith('Please tell us') and msg.author.id == 716390085896962058):
            sleeping=True
            print('\033[91mCaptcha Found\033[0m')


        #react function
        if msg.author.id == config.OwnerId and msg.guild.id== config.GuildId:
            if '!react' in message:
                reactionpattern = r"!react (\d*) (.*)"
                temp= re.search(reactionpattern, message)
                messageId = temp.group(1)
                emoji = temp.group(2)
                
                
        

    except:
        pass
    
        
            



    






bot.run(config.token)
