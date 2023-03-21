import os
import openai
import discord

# Initialize OpenAI API
openai.api_key = os.environ['API_KEY']

# Initialize Discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Initialize chat context
chat_context = []


async def fetch_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=prompt,
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = response['choices'][0]['message']['content'].strip()
    return message


@client.event
async def on_ready():
    print(f"{client.user.name} is online!")


@client.event
async def on_message(message):
    print(f"Message received from {message.author}: {message.content}")

    if message.author == client.user:
        return

    if message.channel.name != "gpt":
        return

    content = message.content.strip()

    if content.lower().startswith("reset:"):
        chat_context.clear()
        await message.channel.send("bot reset !!!!")
        return
    elif content.lower().startswith("set:"):
        chat_context.append({"role": "system", "content": content[4:]})

    else:
        chat_context.append({"role": "user", "content": content})

    print(f"User: {content}")

    # Fetch and send GPT-4 response
    response = await fetch_gpt_response(chat_context)
    chat_context.append({"role": "assistant", "content": response})
    await message.channel.send(response)

client.run(os.environ['DISCORD_API'])
