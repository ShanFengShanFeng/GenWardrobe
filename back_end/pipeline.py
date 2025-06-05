import os
import uuid
import json
import base64
import shutil
import tempfile
from query_embedding import call_gemini_api_with_image, call_gemini_api_with_text, validate_person_features, validate_environment_features, flatten_json, clean_and_format
from retrieve import query_index, find_json_data, StorageContext, load_index_from_storage, run_retrieval
from google_image import extract_fields_from_json, build_prompt, model as google_image_model
from google_image import get_gemini_query_from_environment
from SD import call_gemini as sd_prompt_generator, call_stable_diffusion, get_image_with_r1_sd
from datetime import datetime
from try_on import generate_final_tryon
from config import RESULT_CACHE_PATH
from config import GEMINI_API_KEY

# Load existing cache if available
if os.path.exists(RESULT_CACHE_PATH):
    with open(RESULT_CACHE_PATH, "r") as f:
        results_store = json.load(f)
else:
    results_store = {}

def save_results_cache():
    with open(RESULT_CACHE_PATH, "w") as f:
        json.dump(results_store, f)

def encode_image_url_to_base64(url):
    import requests
    from io import BytesIO
    response = requests.get(url)
    return base64.b64encode(BytesIO(response.content).read()).decode()

def generate_all_results(description, fullbodyshot_path, req_id, selectedImageList=None):
    # Step 1: Generate U_Profile from U2 image
    user_folder = os.path.join("user_images", req_id)
    os.makedirs(user_folder, exist_ok=True)

    profile_str = call_gemini_api_with_image(fullbodyshot_path)
    person_data = json.loads(profile_str)
    if not validate_person_features(person_data):
        raise ValueError("Missing critical person features: Gender / Age / Skin Tone")

    # Step 2: Generate Text_Q and flatten as Q1
    text_q_str = call_gemini_api_with_text(description)
    scenarios = json.loads(text_q_str)
    print("[Gemini Text Output]", text_q_str)
    if isinstance(scenarios, dict):
        scenarios = [scenarios]

    results = []
    all_q1_texts = []

    clothing_counter = 1  # for unique clothing image names
    tryon_counter = 1     # for unique try-on image names

    for i, scenario in enumerate(scenarios):
        if not validate_environment_features(scenario):
            continue

        merged = person_data.copy()
        merged.update(scenario)

        # flatten and save query
        flat = flatten_json(merged)
        q1_text = clean_and_format(flat)
        all_q1_texts.append(q1_text)

        # save temp Q1 txt
        # Q1 path (text file for retrieval input)
        q1_path = f"data_embedding/query_{req_id}.txt"
        with open(q1_path, "w", encoding="utf-8") as f:
            f.write(q1_text)

        # Step3: R1 Retrieval from Q1
        r1_json_data = run_retrieval(req_id)  
        r2_query = []
        r3_images = []
        
        for r1 in r1_json_data:
            # Extract environment fields from R1
            env_fields = extract_fields_from_json(r1)

            # Step 4: R2 - generate query using Gemini + Environment fields
            gemini_query_results, status = get_gemini_query_from_environment(env_fields)

            if status == "Success":
                if isinstance(gemini_query_results, str):
                    gemini_query_results = [gemini_query_results]  # 🚑 Fix here
                for query in gemini_query_results:
                    r2_query.append({f"text{len(r2_query)+1}": query})

            # Step 5: R3 - generate image via SD module
            clothing_image_path = os.path.join("user_images", req_id, f"{req_id}_clothing_{clothing_counter}.png")
            image_path = get_image_with_r1_sd(r1, req_id, clothing_image_path)

            if image_path:
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    r3_images.append({
                        f"text{clothing_counter}": f"/user_images/{req_id}/{os.path.basename(image_path)}",
                        # "base64": b64
                    })
            clothing_counter += 1

        # Append try-on images to result3
        results.append({
            "query1": q1_text,
            "result1": r1_json_data,
            "result2": r2_query,
            "result3": r3_images
        })

    save_results_cache()
    return {
        "id": req_id,
        "profile": fullbodyshot_path,
        "query1": [r["query1"] for r in results],
        "result1": [r["result1"] for r in results],
        "result2": [q for r in results for q in r["result2"]],
        "result3": [img for r in results for img in r["result3"]]  # Flatten result3
    }