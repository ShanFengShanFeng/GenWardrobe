import base64
import requests

def image_url_to_base64(url):
    response = requests.get(url)
    return base64.b64encode(response.content).decode('utf-8')

# Example image URLs
urls = [
    "https://www.popsci.com/wp-content/uploads/2023/01/10/Ocean-1010062.png",
    "https://upload.wikimedia.org/wikipedia/commons/5/53/Tanjong-beach-palm-tree-Sentosa.JPG",
    "https://www.lulus.com/blog/wp-content/uploads/2024/02/2597871.jpg"
]

# Convert and print
for i, url in enumerate(urls):
    b64 = image_url_to_base64(url)
    print(f"Image {i+1} Base64: {b64[:60]}")
