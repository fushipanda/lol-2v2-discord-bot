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

# Add this after your imports and before the bot setup
previous_categories = set()  # Store category names to avoid duplicates
MAX_HISTORY = 20  # Limit how many we remember

# Add this function to save/load history
def save_category_history():
    with open('category_history.txt', 'w') as f:
        for cat in previous_categories:
            f.write(cat + '\n')

def load_category_history():
    global previous_categories
    try:
        with open('category_history.txt', 'r') as f:
            previous_categories = set(line.strip() for line in f.readlines())
            # Keep only the most recent ones if too many
            if len(previous_categories) > MAX_HISTORY:
                previous_categories = set(list(previous_categories)[-MAX_HISTORY:])
    except FileNotFoundError:
        previous_categories = set()

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
    load_category_history()
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

    global previous_categories

    await ctx.send("🧠 Thinking... Generating categories...")

    excluded_categories_text = ""
    if previous_categories:
        excluded_categories_text = f"\n{', '.join(previous_categories)}"

    # Rotate persona and theme
    system_message = random.choice([
        "You are a creative game designer who makes unique champion challenges.",
        "You are a skill based game designer who creates categories based on gameplay feel, NOT lore or visuals.",
        "You are a chaotic League GM who loves bending rules.",
        "You are a statistics-based AI trained on every League match ever.",
        "You are a League coach creating off-meta drills.",
        "You are a witty game critic inventing sarcastic champion categories.",
        "You are making categories to specifically annoy try-hards and one-tricks.",
        "You are a creative game designer who makes unique champion challenges."
    ])

    prompt_instruction = random.choice([
        f"Create a category based on build synergies.",
        f"Invent a category around unusual champion mechanics or passives.",
        f"Come up with a funny or chaotic challenge category that still works.",
        f"Design a category that creates team-wide synergy opportunities.",
        f"Create a high-skill cap challenge category based on ability usage.",
        f"Create a category based on the same champion skin line.",
        f"Create a category based on champion lore.",
        f"Create a category based on champion region (e.g demacia, ionia, noxus).",
        f"Create a category based on newer released champions (last 2 years)",
        f"Create a category based on weird ability scaling ratios",
        f"Create a category based on a physical feature (e.g., horns, tails, wings)",
        f"Create a category based on champions that players often forget exist"
    ])

    banned_concepts = random.sample([
        "cosmic", "star", "void",
        "yordle", "demacia", "noxus", "ionia",
        "transform", "stealth", "invisible",
        "dash", "blink",
        "animal", "spirit", "demon", "god",
        "elemental", "shapeshifter",
        "fire", "ice", "water", "earth", "wind", "lightning",
        "project", "star guardian"
    ], k=random.randint(3, 6))

    category_text = ""

    if random.randint(1, 4) == 1:
        selected_item = random.choice(options)
        info(f"PROC: selected item is {selected_item}")
        full_prompt = f"""
                        You are given a category and title for a league of legends 2v2

                        The category is {selected_item}.

                        **Format your response exactly like this:**

                        [Emoji related to the category]  {selected_item}
                        Very brief and concise explanation of what defines this category
                        BLANK LINE
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
                max_completion_tokens=400
            )

            category_text = response.choices[0].message.content.strip()

        except Exception as e:
            await ctx.send("⚠️ Sorry, I couldn't generate a category. Please try again later.")
            print(f"OpenAI error: {e}")
    else:

        info(f"SYSTEM MESSAGE: {system_message}")
        info(f"PROMPT INSTRUCTION: {prompt_instruction}")
        info(f"BANNED CONCEPTS: {', '.join(banned_concepts)}")
        info(f"PREVIOUS CONCEPTS: {excluded_categories_text}")

        # You may be inspired by this list of existing categories: {category_list}
        full_prompt = f"""
                        Generate one original and interesting category for a 2v2 League of Legends ARAM game.

                        The category is:
                        - Be based on {prompt_instruction}
                        - **Exclude** anything to do with the rune system or item system
                        - Apply to **at least 6 champions** minimum
                        - Be **unique** and **not directly copied** from the provided examples

                        IMPORTANT: Do NOT create categories about: {', '.join(banned_concepts)},{excluded_categories_text}

                        **Format your response exactly like this:**

                        [Emoji related to the category] Category Name
                        Very brief and concise explanation of what defines this category. The Category Name should be simple and make logical sense to the category.
                        BLANK LINE
                        Example Champions: 
                        Champion1, Champion2, Champion3, ..., Champion6

                        Do not add headers, extra notes, or titles. Just return the formatted output. If the category requires champion duos, syngergies or team combos (if relevant), list them as Champion1 + Champion2,Champion3 + Champion4.
                        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",  # Or use "gpt-5-mini" or "gpt-5-nano"
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": full_prompt}
                ],
                max_completion_tokens=400,
                temperature=random.uniform(0.8, 1.6),
                top_p=random.uniform(0.85, 0.95),
                frequency_penalty=random.uniform(0.5, 1.5),
                presence_penalty=random.uniform(0.3, 1.0)
            )

            category_text = response.choices[0].message.content.strip()

        except Exception as e:
            await ctx.send("⚠️ Sorry, I couldn't generate a category. Please try again later.")
            print(f"OpenAI error: {e}")

    info(f"PROMPT: {category_text}")

# Parse API response (assuming consistent formatting)
    lines = category_text.split('\n')
    category_name = lines[0].strip()
    description = lines[1].strip()  # Description is always on line 2
    champions_line = "No champions listed"
    for i, line in enumerate(lines):
        if "Example Champions" in line and i + 1 < len(lines):
            champions_line = lines[i + 1].strip()
            break
        elif "Example Champions" in line and ":" in line:
            # Sometimes it's on the same line after the colon
            champions_line = line.split(":", 1)[1].strip()
            break

    previous_categories.add(category_name)
    if len(previous_categories) > MAX_HISTORY:
        # Remove oldest entries if we exceed max
        previous_categories = set(list(previous_categories)[-MAX_HISTORY:])
    save_category_history()
    
    info(f"Added '{category_name}' to category history")
        
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

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1398537971459821660/1398540191702057061/add4858a-c768-4d4f-99e3-5ba3abe13745.png?ex=68a9540d&is=68a8028d&hm=3c1055aa0352e2d975ec26f0acd3899dae27fea50ad9969fa1460a2a04ac2954&")
    embed.set_footer(text=f"League of Legends ARAM • {user_settings} Category") 

    # view = RerollView(category, ctx)
    # await ctx.send(embed=embed,view=view)
    await ctx.send(embed=embed)



client.run(discord_token)
