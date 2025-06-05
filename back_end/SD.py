import os
import json
import requests
from urllib.parse import urlparse, unquote
import google.generativeai as genai
from config import GEMINI_API_KEY, STABILITY_API_KEY, llm_model, FASHION_PROMPT_TEMPLATE, call_stable_diffusion_url

genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(clothing_dict):
    prompt = FASHION_PROMPT_TEMPLATE.format(clothing_dict=json.dumps(clothing_dict, indent=2))
    model = genai.GenerativeModel(llm_model)
    response = model.generate_content(prompt)
    if response.text:
        lines = response.text.splitlines()
        for line in lines:
            if line.lower().startswith("fashion prompt:"):
                return line[len("Fashion Prompt:"):].strip()
        return response.text.strip()
    else:
        raise RuntimeError("No response from Gemini")

def call_stable_diffusion(prompt_text, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    url = call_stable_diffusion_url
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*"
    }
    data = {
        "prompt": prompt_text,
        "negative_prompt": (
            "face, people, person, human, model, portrait, crowd, scenery, background, "
            "room, photo, sky, realistic face, artistic style, cartoon, text, watermark, blurry"
        ),
        "output_format": "png"
    }

    response = requests.post(url, headers=headers, files={"none": ''}, data=data)

    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Image saved: {file_path}")
    else:
        print(f"Stable Diffusion API failed: {response.status_code}, {response.text}")

def get_image_with_r1_sd(r1: dict, req_id: str, file_path: str) -> str:
    # Extract clothing info
    clothing_info = r1.get("Persons", [{}])[0].get("Clothing and Accessories Features", {})
    if not clothing_info:
        print("No clothing info found in R1.")
        return ""

    # Generate prompt
    prompt = call_gemini(clothing_info)

    # Generate image
    call_stable_diffusion(prompt, file_path)

    # Return path if successful
    return file_path if os.path.exists(file_path) else ""