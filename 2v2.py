import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import random
import openai
from datetime import datetime

#nodemon --exec python3 2v2.py
user_settings = "2v2"

class C:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'  # Reset color

# Simple functions for different message types
def timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def info(msg):
    print(f"{timestamp()} {C.BLUE}INFO{C.END}\t{msg}")

def debug(msg):
    print(f"{timestamp()} {C.CYAN}DEBUG{C.END}\t{msg}")

def warning(msg):
    print(f"{timestamp()} {C.YELLOW}WARNING{C.END}\t{msg}")

def error(msg):
    print(f"{timestamp()} {C.RED}ERROR{C.END}\t{msg}")

# Or just override print globally for automatic INFO formatting
def colored_print(*args, **kwargs):
    message = ' '.join(str(arg) for arg in args)
    print(f"{timestamp()} {C.GREEN}INFO{C.END}\t{message}", **kwargs)

# class RerollView(discord.ui.View):
#     def __init__(self, category_func, ctx):
#         super().__init__(timeout=3600)  # 1 hour timeout
#         self.category_func = category_func
#         self.ctx = ctx
    
#     @discord.ui.button(label='Reroll', style=discord.ButtonStyle.primary, emoji='🎲')
#     async def reroll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
#         try:
#             # Call your category function again
#             await interaction.response.defer()
#             await self.category_func(self.ctx)
#         except Exception as e:
#             error(f"Reroll error: {e}")

# Load environment variables
load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")
intents = discord.Intents.default()
intents.message_content = True  # If using message commands

# Set OpenAI key
openai.api_key = openai_api_key

if not discord_token:
    raise ValueError("Missing Discord token in .env file.")
if not openai_api_key:
    raise ValueError("Missing OpenAI API key in .env file.")

# Create bot instance
client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Category reference list (used in the prompt)
category_list = """PROJECT Skins
Animal Companions
Champs in a Band
Blue
Assassins
Armored Champs
Bandle City
Enchanters
Star Guardian Skins
Void
Exposed Bell
Ixtal
Hat/Headwear
Mecha Skins
Demacia
Mages
One-Eyed Champs
Global Ultimates
Matching Skin Lines
Bruisers
Champs with Ultimate Skin
Ranged
Freljord
Tanks
Darkin
Yordle
5 Randoms
Noxus
Short Kings/Queens (Short-statured Champions)
Fire and Ice (Champions with fire or ice abilities)
AD Only
Top 5 Mastery
First Letter of Last Name
One-Trick Champions
Champs with Worlds Team Skins
Duelists
Shurima
Old Random
Artists
Hard CC Masters
Odyssey Skins
Weapon Wielders
RNG (Randomized Picks)
Flying Champs
Wombo Combo
Orange
Piltover
Least 5 Mastery
Purple
Silencers
Spin Again
Bearded Champs
Non-Humanoid
Ionia
Masked Champs
Yellow
Undead
Green
Zaun
Targon
Speedsters (Enhanced Movement Speed)
Supports
Shield Bearers
Villains
Elderwood Skins
Pentakill Potentials
AP Only
Skillshot Masters
Animal Like
Red
Festive Skins (Holiday-themed Skins)
First Letter of First Name
Bilgewater
Shape Shifters
Bare Hands (Champions without weapons)
Shadow Isles
Reworked Champs
Tall Champs
Heroes"""
options = category_list.splitlines()

# ---------- BOT EVENTS ----------

@client.event
async def on_ready():
    print("---------- League 2v2 Bot is ready ----------")

@client.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")
    await client.process_commands(message)

# ---------- !roll COMMAND ----------

@client.command()
async def roll(ctx):
    """
    Randomly selects an item from a hardcoded list and posts it.
    """
    await ctx.send("🎲 Rolling...")
    await asyncio.sleep(2)
    selected_item = random.choice(options)
    await ctx.send(f"🎲 The category is... **{selected_item}**!")

# ---------- !category COMMAND ----------

@client.command()
async def category(ctx):
    """
    Generates a custom League category using GPT with a clean format.
    """

    await ctx.send("🧠 Thinking... Generating categories...")

    # Rotate persona and theme
    system_message = random.choice([
        "You are a creative game designer who makes unique champion challenges.",
        "You are a chaotic League GM who loves bending rules.",
        "You are a statistics-based AI trained on every League match ever.",
        "You are a League coach creating off-meta drills.",
        "You are a witty game critic inventing sarcastic champion categories."
    ])

    prompt_instruction = random.choice([
        f"Create a category based on build synergies.",
        f"Invent a category around unusual champion mechanics or passives.",
        f"Come up with a funny or chaotic challenge category that still works.",
        f"Design a category that creates team-wide synergy opportunities.",
        f"Create a high-skill cap challenge category based on ability usage.",
        f"Create a category based on champion skin lines.",
        f"Create a category based on champion lore."
    ])

    category_text = ""

    if random.randint(1, 6) == 1:
        selected_item = random.choice(options)
        info(f"PROC: selected item is {selected_item}")
        full_prompt = f"""
                        You are given a category and title for a league of legends 2v2

                        The category is {selected_item}.

                        **Format your response exactly like this:**

                        [Emoji related to the category]  {selected_item}
                        Very brief and concise explanation of what defines this category

                        Example Champions:
                        Champion1, Champion2, Champion3, ..., Champion6

                        Do not add headers, extra notes, or titles. Just return the formatted output. If the category requires champion duos, list them as Champion1 + Champion2,Champion3 + Champion4.
                        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=200,
                temperature=random.uniform(1.3, 1.8),
                top_p=random.uniform(0.85, 0.95)
            )

            category_text = response.choices[0].message.content.strip()

        except Exception as e:
            await ctx.send("⚠️ Sorry, I couldn't generate a category. Please try again later.")
            print(f"OpenAI error: {e}")
    else:

        info(f"SYSTEM MESSAGE: {system_message}")
        info(f"PROMPT INSTRUCTION: {prompt_instruction}")

        # You may be inspired by this list of existing categories: {category_list}
        full_prompt = f"""
                        Generate one original and interesting category for a 2v2 League of Legends ARAM game.

                        The category is:
                        - Be based on {prompt_instruction}
                        - **Exclude** anything to do with the rune system or item system
                        - Apply to **at least 6 champions** minimum
                        - Be **unique** and **not directly copied** from the provided examples



                        **Format your response exactly like this:**

                        [Emoji related to the category] Category Name
                        Very brief and concise explanation of what defines this category

                        Example Champions: 
                        Champion1, Champion2, Champion3, ..., Champion6

                        Do not add headers, extra notes, or titles. Just return the formatted output. If the category requires champion duos, syngergies or team combos (if relevant), list them as Champion1 + Champion2,Champion3 + Champion4.
                        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=200,
                temperature=random.uniform(1.3, 1.8),
                top_p=random.uniform(0.85, 0.95)
            )

            category_text = response.choices[0].message.content.strip()

        except Exception as e:
            await ctx.send("⚠️ Sorry, I couldn't generate a category. Please try again later.")
            print(f"OpenAI error: {e}")

# Parse API response (assuming consistent formatting)
    lines = category_text.split('\n')
    category_name = lines[0].strip()
    description = lines[1].strip()  # Description is always on line 2
    champions_line = lines[4].strip()
        
    # Create embed for API response
    embed = discord.Embed(
        title=f"{category_name}",
        description=description,
        color=0x0099FF  # Blue for generated categories
    )
    embed.add_field(
        name="✨ Example Champions:",
        value=champions_line,
        inline=False
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1398537971459821660/1398540191702057061/add4858a-c768-4d4f-99e3-5ba3abe13745.png?ex=6885bb8d&is=68846a0d&hm=e4de2dd37f050078d27a8ae0d7c3150d7c9e0d882baddaff1670d76a28887a7c&")
    embed.set_footer(text=f"League of Legends ARAM • {user_settings} Category") 

    # view = RerollView(category, ctx)
    # await ctx.send(embed=embed,view=view)
    await ctx.send(embed=embed)



client.run(discord_token)
