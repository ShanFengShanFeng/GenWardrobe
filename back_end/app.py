import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import requests
from io import BytesIO
from PIL import Image
from pipeline import generate_all_results, results_store, save_results_cache
from try_on import generate_final_tryon
import traceback
import base64
from config import OUTPUT_DIR, RESULT_CACHE_PATH, embed_model, llm_model, GEMINI_API_KEY, index_path
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import StorageContext, load_index_from_storage
from base64 import b64decode
import re

app = Flask(__name__)
CORS(app)

@app.route('/admin/submit', methods=['POST'])
def submit():
    data = request.get_json()
    fullbodyshot_url = data.get("fullbodyshot")
    description = data.get("description")

    if not (fullbodyshot_url and description):
        return jsonify({"errNo": 1, "errMsg": "Missing fields"}), 400

    try:
        # Generate request ID
        req_id = str(uuid.uuid4())

        # Download image and save locally
        if fullbodyshot_url.startswith("data:image"):
            # Extract base64 content after comma
            base64_data = re.sub("^data:image/.+;base64,", "", fullbodyshot_url)
            image_data = b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
        else:
            # Fallback to URL download
            response = requests.get(fullbodyshot_url)
            if response.status_code != 200:
                return jsonify({"errNo": 2, "errMsg": "Failed to download image"}), 400
            image = Image.open(BytesIO(response.content))


        USER_IMAGE_DIR = os.path.join(OUTPUT_DIR, req_id)
        os.makedirs(USER_IMAGE_DIR, exist_ok=True)  
        local_img_path = os.path.join(USER_IMAGE_DIR, f"{req_id}_fullbody.jpg")
        image.save(local_img_path)

        # Run full LLM pipeline
        result = generate_all_results(description, local_img_path, req_id)

        # Save result
        results_store[req_id] = result
        save_results_cache()

        # Format output structure as per requirement
        flattened_result1 = []
        for r1_list in result.get("result1", []):
            flattened_result1.extend(r1_list)

        flattened_result2 = []
        # seen_urls = set()
        for img in result.get("result2", []):
            for key, text in img.items():
                if key.startswith("text"):
                    flattened_result2.append({
                        key: text
                    })

        flattened_result3 = []
        for r3_item in result.get("result3", []):
            if isinstance(r3_item, list):
                flattened_result3.extend(r3_item)
            else:
                flattened_result3.append(r3_item)

        # Process flattened_result3 for base64 (optional)
        final_result3 = []
        for i, img in enumerate(flattened_result3):
            try:
                for key, url in img.items():
                    if key.startswith("text"):
                        local_path = url.lstrip("/")
                        with open(local_path, "rb") as f:
                            img_base64 = base64.b64encode(f.read()).decode()
                        final_result3.append({
                            key: url,
                            "base64": img_base64
                        })
            except Exception as e:
                print(f"⚠️ Failed to load result3 image {url}: {e}")

        flattened_result3 = final_result3


        return jsonify({
            "errNo": 0,
            "errMsg": "",
            "data": {
                "id": req_id,
                "profile": fullbodyshot_url,
                "query1": result.get("query1", []),
                "result1": flattened_result1,
                "result2": flattened_result2,
                "result3": flattened_result3
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"errNo": 500, "errMsg": str(e)}), 500
    
    print(json.dumps(results_store, indent=2))

@app.route('/admin/getResults', methods=['GET'])
def get_results():
    req_id = request.args.get("id")
    result = results_store.get(req_id)
    print("DEBUG - result fetched from results_store:")
    print(json.dumps(result, indent=2)) 
    if result is None:
        return jsonify({"errNo": 4, "errMsg": "Result not found"}), 404

    tryon_data = []
    profile_path = result["profile"]
    result2 = result.get("result2", [])
    result3 = result.get("result3", [])

    # Collecting all clothing paths
    clothing_mapping = []
    for item in result3:
        print("DEBUG - current item in result3:", item)  
        if not isinstance(item, dict):
            continue
        for key, url in item.items():
            if key.startswith("text"):
                index = key.replace("text", "")
                clothing_mapping.append({
                    "index": index,
                    "clothing_path": url.lstrip("/")
                })

    print("clothing_mapping:", clothing_mapping)

    # Initialize counter
    tryon_counter = 1

    # Generate try-on images
    for mapping in clothing_mapping:
        index = mapping["index"]
        clothing_path = mapping["clothing_path"]

        background_query = ""
        for bg_item in result2:
            bg_query = bg_item.get(f"text{index}")
            if bg_query:
                background_query = bg_query
                break

        print(f"Generating try-on for clothing: {clothing_path}")
        print(f"Using background query: {background_query}")

        tryon_path, tryon_b64 = generate_final_tryon(
            req_id=req_id,
            clothing_path=clothing_path,
            background_query=background_query,
            full_body_path=profile_path,
            tryon_counter=tryon_counter
        )
        tryon_counter += 1

        if tryon_path and tryon_b64:
            tryon_data.append({
                "image": tryon_path,
                "base64": tryon_b64,
                "text": f"final_tryon_{tryon_counter - 1}"
            })

    return jsonify({
        "errNo": 0,
        "errMsg": "",
        "data": {"list": tryon_data}
    })



@app.route('/')
def index():
    return "Flask server is running."

@app.route('/admin/test', methods=['GET'])
def test_connection():
    return "test ok", 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050)