# config.py
import os
import json
from llama_index.core import Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core import StorageContext, load_index_from_storage
from dotenv import load_dotenv

load_dotenv()
### === API KEYS === ###
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent?key={GEMINI_API_KEY}"   # query_embedding

### === PATH CONFIGURATION === ###
MERGED_JSON_PATH = os.path.join(os.path.dirname(__file__), "../merged_dict.json")
index_path = "data_embedding"
OUTPUT_DIR = "user_images" 
QUERY_TEMPLATE_DIR = "data_embedding"
RESULT_CACHE_PATH = "result_cache.json"

### === STABLE DIFFUSION === ###
call_stable_diffusion_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

### === TRY ON MODEL === ###
search_model="gpt-image-1"

### === PROMPT TEMPLATES === ###
# query_embedding.py
PROMPT_TEMPLATE_IMAGE = """     
Your Objective:
• You will be given a user-uploaded image.
• You must extract only Person-Related Features using the controlled vocabulary.

Extraction Rules:
• Extract the following fields: Gender, Age, Skin Tone, Hairstyle, Pose, Face Shape, Body Shape.
• "Gender", "Age", and "Skin Tone" are mandatory. If any of these three fields cannot be determined, generate a polite clarification request to re-upload a clearer image.
• Return only a valid JSON object if successful.

Controlled Vocabulary——Use only the following fixed values when assigning labels:
Person-Related Features
• Skin Tone: Classify visible skin tone. **Only return one of the following values**: "Very fair", "Fair", "Light", "Medium", "Olive", "Brown", "Dark", "Unknown".
• Gender: Determine the person’s gender. **Only return one of the following values**: "Male", "Female", "Unknown".
• Hairstyle: Describe the person's hairstyle based on visible features.
- **Hair Color**: Indicate the natural or dyed hair color in one word (e.g., black, brown, blonde, red, gray, white).
- **Hair Type**: Specify the natural hair texture. **Only return one of the following values**: "Straight", "Wavy", "Curly", "Coily", "Unknown".
- **Hair Length**: Describe the visible length of hair.  **Only return one of the following values**: "Bald", "Short", "Medium", "Long", "Very long", "Unknown".
- **Specific Hairstyle**: Describe the particular styling or arrangement (e.g., Ponytail, Bun, Loose, Braided, Side-parted, Afro, Bob cut, Pixie cut, Buzz cut, Undercut).
• Age: Estimate the age group. **Only return one of the following values**: "Child", "Teenager", "Young adult", "Middle-aged", "Elderly", "Unknown".
• Pose: Describe the person’s posture or movement. **Only return one of the following values**: "Standing", "Sitting", "Lying", "Walking", "Running", "Climbing stairs", "Kneeling", "Leaning", "Unknown".
• Face Shape: Identify the face shape. **Only return one of the following values**: "Oval", "Round", "Square", "Heart-shaped", "Diamond", "Pear", "Rectangular", "Unknown".
• Body Shape: Classify the body shape. **Only return one of the following values**: "I", "H", "A", "V", "X", "O", "Unknown".
"""

# query_embedding.py
PROMPT_TEMPLATE_TEXT = """
Your Objective:
• You will be given a user-provided text description.
• If the description contains multiple Travel Time, Travel Location, or Purpose of Travel, you must treat each as a separate scenario and generate a separate JSON block for each one.
• You must extract Clothing Fashion Style and Environment-Related Features for each scenario based on the text.

Extraction Rules:
• Carefully analyze the text. If it contains multiple Travel Time, Travel Location, and Purpose of Travel (e.g., "attending a wedding and then going on vacation"), split the content and generate one JSON block per scenario.
• For each scenario, internally infer Travel Time, Travel Location, and Purpose of Travel.
• Use these inferred factors to reason about and extract:
  - Clothing Fashion Style
  - Environment-Related Features (Season, Weather, Time of Day, Lighting, Location, Temperature, Scene Environment, Scene Type, Scene Features, Ambience)
• Only include Clothing Fashion Style and Environment-Related Features fields in the final JSON output.
• Do not explicitly include Travel Time, Travel Location, or Purpose of Travel fields in the output JSON.
• Your final output should be a list of JSON objects, each representing one inferred context.

Controlled Vocabulary——Use only the following fixed values when assigning labels:
Clothing Fashion Style: Classify the overall fashion style of the outfit. **Only return one of the following values**:
"Commuter", "Casual", "Pastoral", "Campus", "Sports", "Party", "Date", "Vacation", "Festival", "Homewear", "Religious", "Traditional", "Artistic exhibition", "Wedding", "Stage", "Professional outdoor", "Unknown".

Environment-Related Features
• Season: Infer the season based on the setting and clothing. **Only return one of the following values**: "Spring", "Summer", "Autumn", "Winter", "Unknown".
• Weather: Describe the weather. **Only return one of the following values**: "Sunny", "Cloudy", "Rainy", "Stormy", "Snowy", "Windy", "Foggy", "Hazy", "Indoor", "Unknown".
• Time of Day: **Only return one or more of the following values**: "Morning", "Noon", "Afternoon", "Evening", "Night", "Unknown".
• Lighting style: **Only return one or more of the following values**: "Natural light", "Artificial light", "Ambient light", "Direct light", "Diffused light", "Reflected light", "Backlight", "Side light", "Top light", "Low light".
• Location: Specify the location type (e.g., park, beach, urban setting, indoor) and note any cultural or architectural landmarks.
• Temperature: Estimate the temperature range in Celsius based on the clothing and background. **Return one of the following ranges only**:
  - "Below 0"
  - "0-5"
  - "5-10"
  - "10-15"
  - "15-20"
  - "20-25"
  - "25-30"
  - "30-35"
  - "Above 35"
• Scene Environment: **Only return "Indoor" or "Outdoor"**.
• Scene Type: Classify the scene type (e.g., studio, street, natural landscape, runway).
• Scene Features: Highlight significant features (e.g., trees, sand, water, walls, decorations).
• Ambience: (e.g., calm, casual, serene, energetic, bold, joyful, playful, cold, warm, romantic, mysterious, dramatic, luxurious, minimalist, nostalgic, dreamy, festive, melancholic, peaceful, vibrant, edgy).
"""

image_search_prompt = """
Your task is to act as a Google Image Search assistant.  
You will be given a set of environmental attributes extracted from a text file.  
Your job is to generate a natural-language search query that can be used in Google Image to retrieve a real-life photo background that fits the described setting.

The image **must be a real photograph**, not an illustration or AI-generated image.  
It should reflect the combined environmental context provided.  
Assume the image is to be used as a realistic background for a fashion recommendation system.

Fields may include:
- Season (e.g., Summer, Winter)
- Weather (e.g., Sunny, Rainy, Snowy)
- Time of Day (e.g., Morning, Afternoon, Evening)
- Lighting Style (e.g., Natural light, Direct light)
- Location (e.g., Beach, Urban street, Lakeside)
- Temperature (e.g., 20-25°C, Hot, Cold)
- Scene Environment (e.g., Outdoor, Indoor)
- Scene Type (e.g., Natural landscape, Street)
- Scene Features (e.g., Rocks, Trees, Buildings)
- Ambience (e.g., Calm, Joyful, Dramatic)

Please follow these instructions:

1. Combine all available fields into a **single descriptive sentence** that forms a realistic and precise Google Image search query.
2. Ensure the description is **natural and specific enough** to retrieve relevant results (e.g., "sunny beach in summer with clear blue sky and rocks").
3. Do **not invent any missing fields**—only use the ones provided.
4. Do **not generate or describe an AI-generated image**—your goal is to help retrieve **real-world photos** only.
5. Only use the fields provided. Combine them into a compact and relevant set of **search keywords**, not full sentences.

Output format:
Search Query: <space-separated-keywords>

Now generate the query for the following fields:
{field_dict}
"""

# SD model
FASHION_PROMPT_TEMPLATE = """
Your task is to generate a prompt suitable for a Stable Diffusion model.  
The goal is to generate an image that only includes **clothing and accessories**, without any person, face, body part, or background scene.

Guidelines:
- DO NOT mention or imply any human figure, model, or realistic person.
- DO NOT suggest any environmental scene, context, or mood.
- The clothing should appear as if laid flat or displayed on an invisible mannequin.
- Use a solid white background.
- Focus entirely on clothing design, style, structure, and accessories.

Convert the following structured clothing and accessory data into a clear, concise, vivid natural language description suitable for image generation:

{clothing_dict}

Output format:
Fashion Prompt: <your single-sentence description>
"""

# try_on.py
TRYON_PROMPT = """
Seamlessly overlay the clothing and accessories from the second reference image onto the person in the main image.
Replace the original background of the main image with a realistic environment described as: "{background_description}".
Ensure a highly realistic and photorealistic try-on effect by accurately aligning the clothing with the subject’s posture, body shape, and orientation.
Maintain the subject’s identity, including facial features, hairstyle, skin tone, and body proportions, without distortion or alteration.
Harmonize lighting, shadows, and color tones across all image elements to achieve consistent and natural integration.
Do not modify the facial structure, expression, hairstyle, or any identity-related attributes from the main image. Treat the face area as fixed and immutable.
Ensure clean edges, proper clothing fitting, and realistic texture rendering of the clothing in the described background scene.
Ensure the subject’s size and position appear naturally integrated into the new background, with consistent perspective and appropriate scale relative to the environment.
"""

### === EMBEDDING AND LLM MODEL SETTINGS (Used in Retrieval) === ###
embed_model = "text-embedding-004"
llm_model = "gemini-2.0-flash"

# Set llama_index Settings globally
Settings.embed_model = GoogleGenAIEmbedding(model_name=embed_model, embed_batch_size=100, api_key=GEMINI_API_KEY)
Settings.llm = GoogleGenAI(model=llm_model, api_key=GEMINI_API_KEY)

# Load merged_dict only once
with open(MERGED_JSON_PATH, "r", encoding="utf-8") as f:
    raw_dict = json.load(f)

merged_dict = {
    k.strip().strip("b'").strip("'").strip('"'): v for k, v in raw_dict.items()
}

# Load index once and reuse it
storage_context = StorageContext.from_defaults(
    docstore=SimpleDocumentStore.from_persist_dir(index_path),
    vector_store=SimpleVectorStore.from_persist_dir(index_path),
    index_store=SimpleIndexStore.from_persist_dir(index_path)
)
index = load_index_from_storage(storage_context)