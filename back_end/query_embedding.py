import os
import json
import base64
import requests
import re
from config import GEMINI_API_KEY, GEMINI_API_URL, PROMPT_TEMPLATE_IMAGE, PROMPT_TEMPLATE_TEXT

API_KEY = GEMINI_API_KEY
API_URL = GEMINI_API_URL

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def clean_output_text(output):
    if output.startswith("```json"):
        output = output[len("```json"):].strip()
    if output.endswith("```"):
        output = output[:-len("```")].strip()
    return output

def call_gemini_api_with_image(image_path):
    image_base64 = encode_image(image_path)
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": PROMPT_TEMPLATE_IMAGE.strip()},
                    {"inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_base64
                    }},
                    {"text": "Please extract only person-related features."}
                ]
            }
        ]
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        result = response.json()
        try:
            return clean_output_text(result["candidates"][0]["content"]["parts"][0]["text"])
        except (KeyError, IndexError):
            return None
    return None

def call_gemini_api_with_text(text_description):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": PROMPT_TEMPLATE_TEXT.strip()},
                    {"text": text_description}
                ]
            }
        ]
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        result = response.json()
        try:
            return clean_output_text(result["candidates"][0]["content"]["parts"][0]["text"])
        except (KeyError, IndexError):
            return None
    return None

def validate_person_features(person_data):
    for key in ["Gender", "Age", "Skin Tone"]:
        if key not in person_data or (isinstance(person_data[key], str) and person_data[key].lower() == "unknown"):
            return False
    return True

def validate_environment_features(env):
    problems = []
    e = env.get("Environment-Related Features", {})
    if e.get("Season", "Unknown").lower() == "unknown":
        problems.append("Please provide the travel time (season or month")
    if e.get("Location", "Unknown").lower() == "unknown":
        problems.append("Please provide the travel location (city or place")
    if e.get("Scene Environment", "Unknown").lower() == "unknown":
        problems.append("Please describe the purpose of travel (e.g., tourism, photography, conference).")
    if problems:
        for p in problems:
            print(p)
        return False
    return True

def flatten_json(y, prefix=""):
    out = {}
    if isinstance(y, dict):
        for k, v in y.items():
            new_key = f"{prefix}{k}" if prefix == "" else f"{prefix}.{k}"
            out.update(flatten_json(v, new_key))
    elif isinstance(y, list):
        for i, v in enumerate(y):
            new_key = f"{prefix}.{i}" if prefix else str(i)
            out.update(flatten_json(v, new_key))
    else:
        out[prefix] = y
    return out

def clean_and_format(flat_json):
    lines = []
    for key, value in flat_json.items():
        if isinstance(value, str) and value.strip().lower() == "unknown":
            continue
        if isinstance(value, (list, dict)) and len(value) == 0:
            continue
        clean_key = re.sub(r'\.\d+', '', key)
        clean_key = re.sub(r'^Environment-Related Features\.', '', clean_key)
        clean_key = clean_key.replace('_', ' ').replace('.', ' ').strip()
        lines.append(f"{clean_key}: {value}")
    return "\n".join(lines)

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_text(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def extract_valid_person_features():
    while True:
        img_path = input("Please input the image path: ").strip()
        print("\n[Step 1] Extracting person features from image...")
        person_json_str = call_gemini_api_with_image(img_path)
        if not person_json_str:
            print("Failed to extract person features. Please try again.")
            continue
        try:
            person_data = json.loads(person_json_str)
            if validate_person_features(person_data):
                return person_data
            else:
                print("Gender, Age, or Skin Tone missing. Please re-upload a clearer image.")
        except json.JSONDecodeError:
            print("Invalid JSON received. Please try again.")

def extract_valid_environment_features():
    while True:
        description = input("\n请输入文本描述 / Please input the text description: ").strip()
        print("\n[Step 2] Extracting environment features from text...")
        env_str = call_gemini_api_with_text(description)
        if not env_str:
            print("Failed to extract environment features. Please try again.")
            continue
        try:
            data = json.loads(env_str)
            if isinstance(data, dict):  
                data = [data]
            all_valid = all(validate_environment_features(env) for env in data)
            if all_valid:
                return data
            else:
                print("Incomplete information in one or more scenarios.")
        except json.JSONDecodeError:
            print("Invalid JSON format returned. Try again.")

def main():
    person_data = extract_valid_person_features()
    environment_list = extract_valid_environment_features()

    print("\n[Step 3] Saving multiple scenarios...")
    for i, env in enumerate(environment_list):
        merged = person_data.copy()
        merged.update(env)

        json_file = f"query_info_{i+1}.json"
        txt_file = f"query_embedding_{i+1}.txt"

        save_json(merged, json_file)
        flat = flatten_json(merged)
        txt = clean_and_format(flat)
        save_text(txt, txt_file)

        print(f"[✓] Saved: {json_file} + {txt_file}")

