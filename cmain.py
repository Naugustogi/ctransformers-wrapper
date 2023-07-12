import time
import discord
from discord.ext import commands
from ctransformers import AutoModelForCausalLM
import io
import base64
import json
import requests
from PIL import Image, PngImagePlugin

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
print("lade model")
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
print("start discord package")
token = "" 
intents = discord.Intents.default()
client = discord.Client(intents=intents)
#llm = AutoModelForCausalLM.from_pretrained('orca-mini-3b.ggmlv3.q4_0.bin', model_type='llama')
llm = AutoModelForCausalLM.from_pretrained('orca-mini-3b.ggmlv3.q8_0.bin', model_type='llama')
print("apply context")
with open("Assistant.txt", "w") as file:
    pass
with open("Assistant.txt", "a") as file:
    file.write("You are a smart Sage, you can answer any question. Enju is your creator." + "\n")
    #file.write("User: Hello how are you doing?" + "\n")
    #file.write("Sage: I'm fine. I can help you with any problem." + "\n")
    file.close()
print("Ready")

#------------------------------------------------
def generate_image(prompt):
    url = "http://127.0.0.1:7860"

    payload = {
        "prompt": prompt,
        "steps": 20,
        "width": 1024,
        "height": 768
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    r = response.json()

    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image_path = 'output.png'
        image.save(image_path, pnginfo=pnginfo)
        return image_path
#------------------------------------------------
@client.event
async def on_message(message):
    print("def loaded")
    if message.author == client.user:
        return
#------------------------------------------------
    if  client.user.mentioned_in(message):
        prompt = message.content[23:]
        channel = message.channel
        user_name = message.author.name
        print(message.author.name)
        if message.author.name == "enju_aihara":
            user_name = "Creator Enju:"
        if("reset" in prompt):
            llm.reset()
            return
            
        if "gens" in prompt:
            image_prompt = prompt.replace("gens", "").strip()
            image_path = generate_image(image_prompt)
            await channel.send(file=discord.File(image_path))
            return
            
        print(message.author.name, prompt)
        with open("Assistant.txt", "a") as file:
            #file.write("You are an highly advanced intelligent AI System." + "\n")
            file.write(user_name + ":" + prompt + "\n")
            file.write("Sage:")
            file.close
        with open("Assistant.txt", "r") as file:
            context = file.read()
            file.close()
        #-----------------------------------------
        response = ""
        response = llm(context, reset = True, temperature = 0.1, repetition_penalty = 1.1, max_new_tokens = 1000)
        if(len(response) >= 3999):
            response = response[:3999]
        await channel.send(response)
        #-----------------------------------------
        with open("Assistant.txt", "a") as file:
            file.write(response + "\n")
            file.close()

        with open("Assistanten.txt", "a") as file:
            file.write("Sage:" + response + "\n")
            file.write(user_name + ":" + prompt + "\n")
            file.close()
        
        #with open("Assistant.txt", "w") as file:
        #    pass
        #    file.close
        #-----------------------------------------

client.run(token)
