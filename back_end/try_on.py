import base64
from openai import OpenAI
import os
import requests
from PIL import Image
from io import BytesIO
from config import OPENAI_API_KEY, search_model, TRYON_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

prompt = TRYON_PROMPT

def generate_final_tryon(req_id, clothing_path, background_query, full_body_path, tryon_counter=1):
    # Create output path
    root_id = req_id.split("_")[0]
    out_dir = os.path.join("user_images", root_id)
    os.makedirs(out_dir, exist_ok=True)

    # File paths
    out_path = os.path.join(out_dir, f"{root_id}_tryon_{tryon_counter}.png")
    clothing_path = os.path.join("user_images", req_id, os.path.basename(clothing_path))
    full_body_path = os.path.join("user_images", root_id, f"{root_id}_fullbody.jpg")
    
    try:
        # Build the final prompt with Gemini-generated background description
        final_prompt = TRYON_PROMPT.format(background_description=background_query)

        # Open image files in binary mode (full body + clothing)
        with open(full_body_path, "rb") as f1, open(clothing_path, "rb") as f2:
            result = client.images.edit(
                model=search_model,
                image=[f1, f2], 
                prompt=final_prompt
            )

        # Decode and save the result
        image_data = base64.b64decode(result.data[0].b64_json)
        with open(out_path, "wb") as f:
            f.write(image_data)

        print(f"✅ Try-on image saved to {out_path}")
        return out_path, base64.b64encode(image_data).decode("utf-8")

    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return "", ""