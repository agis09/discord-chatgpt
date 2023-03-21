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


def ask(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
        stream=True
    )
    response_text = ""
    for chunk in response:
        if chunk:
            content = chunk['choices'][0]['delta'].get('content')
            if content:
                response_text += content
                yield content
    else:
        messages.append({'role': 'assistant', 'content': response_text})
    return messages


async def fetch_gpt_response(prompt, channel):
    send_message = ""
    for response_chunk in ask(prompt):
        send_message += response_chunk
        if len(send_message) > 100:
            await channel.send(send_message)
            send_message = ""
    await channel.send(send_message)


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
        await message.channel.send("オタク reset !!!!")
        return
    elif content.lower().startswith("set:"):
        chat_context.append({"role": "system", "content": content[4:]})

    else:
        chat_context.append({"role": "user", "content": content})

    print(f"User: {content}")

    # Fetch and send GPT-4 response
    await fetch_gpt_response(chat_context, message.channel)
    await message.channel.send("::continue?::")

client.run(os.environ['DISCORD_API'])
