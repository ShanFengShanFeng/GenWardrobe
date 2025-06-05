import os
import json
import re
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from config import GEMINI_API_KEY, image_search_prompt

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def extract_fields_from_json(data_dict):   
    # extract field
    target_fields = [
        "Season", "Weather", "Time Of Day", "Lighting Style",
        "Location", "Temperature", "Scene Environment",
        "Scene Type", "Scene Features", "Ambience"
    ]
    extracted = {}
    env_data = data_dict.get("Environment-Related Features", {})
    for field in target_fields:
        for key in env_data.keys():
            if key.lower().strip() == field.lower().strip():
                value = env_data[key]
                extracted[field] = ", ".join(value) if isinstance(value, list) else value
                break
    return extracted

# Gemini Prompt
def build_prompt(field_dict):
    prompt = image_search_prompt.format(field_dict=field_dict)
    return prompt

def get_gemini_query_from_environment(env_fields: dict):
# Step 1: Build Gemini prompt
    prompt = build_prompt(field_dict=env_fields)
    print("Prompt used for Gemini:")
    print(prompt)

    try:
        # Step 2: Query Gemini for search query
        response = model.generate_content(prompt)
        time.sleep(1)  
        response_text = response.text.strip()

        if "Search Query:" not in response_text:
            print("Gemini response missing 'Search Query:'")
            return [], "No query found"

        # Step 3: Extract actual search query string
        query = response_text.split("Search Query:")[-1].strip()
        print(f"Extracted Query: {query}")
        return [query], "Success"

    except Exception as e:
        print(f"Error during query/image fetch: {e}")
        return [], "Exception occurred"