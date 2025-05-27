# TOWARD: Task-Oriented Wardrobe Assistant for Realistic Dressing

## Overview
**TOWARD** is an end-to-end fashion recommendation system that supports:
- **Multimodal input**: combines both user-uploaded images and textual descriptions.
- **Contextual understanding**: models user appearance and real-world scenarios (e.g., travel, work, leisure).
- **Structured retrieval**: retrieves relevant outfit components based on semantic matching.
- **Try-on image generation**: generates realistic try-on images using state-of-the-art generative models.
- It is designed to help users visualize complete outfit suggestions tailored to their real-world travel or task-based scenarios.
![Figure 1. Overall system workflow](framework.png)

## System Design
- **Database Construction**: The Gemini model is employed to perform parallel filtering and feature extraction on raw image data.
![Figure 2. Feature extraction on raw image data](extraction.png)
- **User Input and Information Parsing**
- **Index Construction and Retrieval**
- **Image Generation and Fusion**

\textbf {User Input and Information Parsing}. Users upload full-body images and provide travel-related information through the interface. The system uses regular expression templates and predefined fields to detect missing information, and invokes the Gemini model to perform automatic recognition and prompt completion suggestions.

\textbf {Index Construction and Retrieval}. A vector index is built using the LlamaIndex framework. High-dimensional feature matching is performed based on semantic representations of environmental context and personal attributes, retrieving multiple records that best match the user's input.

\textbf {Image Generation and Fusion}. Based on the retrieval results, the Stable Diffusion model is used to generate clothing images, while background information  is incorporated directly into the input for the GPT image model. This results in multiple visualized outfit images that integrate the user's appearance with realistic environmental contexts, forming a comprehensive personalized "travel wardrobe."

## Getting Started
### Key Steps for Realistic Dressing
1. Upload a full-body user image and provide a scene description (e.g., “I'm going to a beach vacation in July”).
2. Add your API_KEY in [config.py](config.py).
3. Start the backend with Flask to receive POST requests for generation.
4. Use Frontend or Postman/cURL to interact with `/admin/submit` and `/admin/getResults`.
5. Run [app.py](app.py) to execute the entire pipeline.

## Dataset  
Preparing...


## Citing FashionReGen
If you find this repository useful, please cite our paper:
```
@inproceedings{TOWARD,
  author       = {Peng Jin and
                  Yilin Wen and
                  Mingzhe Yu and
                  Yunshan Ma and
                  Rong Zheng and
                  Jintu Fan and
                  Chong Wah NGO},
  title        = {TOWARD: Task-Oriented Wardrobe Assistant for Realistic Dressing},
  booktitle    = {{WWW} (Companion Volume)},
  pages        = {xxx},
  publisher    = {{ACM}},
  year         = {2025}
}
```

## Citing FashionReGen
