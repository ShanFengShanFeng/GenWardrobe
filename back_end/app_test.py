from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

results_store = {}

@app.route('/admin/submit', methods=['POST'])
def submit():
    data = request.get_json()
    # headshot = data.get("headshot")
    fullbodyshot = data.get("fullbodyshot")
    description = data.get("description")

    if not (fullbodyshot and description):
    # if not (headshot and fullbodyshot and description):
        return jsonify({"errNo": 1, "errMsg": "Missing fields"}), 400

    req_id = str(uuid.uuid4())
    # results_store[req_id] = {
    #     "profile": "profile_url",
    #     "query1": ["item1", "item2"],
    #     "result1": ["look1", "look2"],
    #     "result2": ["tip1", "tip2"]
    # }

    # mock test response
    results_store[req_id] = {
    "profile": "https://images.pexels.com/photos/4708397/pexels-photo-4708397.jpeg",
    "query1": [
        "Gender: Female\nAge: Young adult\nSkin Tone: Olive\nHairstyle Hair Color: Brown\nHairstyle Hair Type: Wavy\nHairstyle Hair Length: Long\nHairstyle Specific Hairstyle: Loose\nPose: Standing\nFace Shape: Oval\nClothing Fashion Style: Vacation\nSeason: Spring\nLighting style: Natural light\nLocation: Island, possibly coastal area\nTemperature: 10-15\nScene Environment: Outdoor\nScene Type: Natural landscape\nAmbience: Casual"
    ],
    "result1": [
        {
            "Persons": [
                {
                    "Person-Related Features": {
                        "Skin Tone": "Olive",
                        "Gender": "Female",
                        "Hairstyle": {
                            "Color": "Black",
                            "Type": "Wavy",
                            "Length": "Long",
                            "Specific Style": "Loose"
                        },
                        "Age": "Young adult",
                        "Pose": "Standing",
                        "Face Shape": "Diamond",
                        "Body Shape": "Petite"
                    },
                    "Clothing and Accessories Features": {
                        "Clothing Items": {
                            "Upper Body": [],
                            "Lower Body": [],
                            "Full-Body Clothing": [
                                {
                                    "Category": "Romper",
                                    "Subcategory": "Floral romper",
                                    "Color": "Multicolor",
                                    "Material": "Unknown",
                                    "Silhouette": "A-line",
                                    "Design features": "Sleeveless romper with floral print, V-neckline, elastic waistband, relaxed fit shorts, lightweight fabric, casual summer style"
                                }
                            ],
                            "Special Clothing": []
                        },
                        "Clothing Fashion Style": "Vacation",
                        "Accessories": {
                            "Head Accessories": [
                                {
                                    "Category": "Sunglasses",
                                    "Subcategory": "Oval sunglasses",
                                    "Color": "Black",
                                    "Material": "Plastic",
                                    "Design features": "Black oval sunglasses, dark tinted lenses, thin frame, retro style"
                                },
                                {
                                    "Category": "Earrings",
                                    "Subcategory": "Stud earrings",
                                    "Color": "Silver",
                                    "Material": "Metal",
                                    "Design features": "Small silver stud earrings, minimalist design"
                                }
                            ],
                            "Feet Accessories": [
                                {
                                    "Category": "Sandals",
                                    "Subcategory": "Flip-flops",
                                    "Color": "Brown",
                                    "Material": "Rubber",
                                    "Design features": "Brown rubber flip-flops, flat sole, casual summer footwear"
                                }
                            ]
                        }
                    }
                }
            ],
            "Environment-Related Features": {
                "Background Dominant Color": "Blue",
                "Season": "Summer",
                "Weather": "Sunny",
                "Time of Day": "Afternoon",
                "Lighting style": "Natural light",
                "Location": ["Coastal", "Island"],
                "Temperature": "25-30",
                "Scene Environment": "Outdoor",
                "Scene Type": "Natural landscape",
                "Scene Features": ["Ocean", "Grass", "Hills", "Islands"],
                "Ambience": ["Calm", "Serene", "Joyful"]
            }
        }
    ],
    "result2": [
        {
            "url": "https://www.popsci.com/wp-content/uploads/2023/01/10/Ocean-1010062.png",
            "base64": "iVBORw0KGgoAAAANSUhEUgAAB9AAAARlCAYAAADh11wiAAAACXBIWXMAAC4j"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/5/53/Tanjong-beach-palm-tree-Sentosa.JPG",
            "base64": "/9j/4YpFRXhpZgAASUkqAAgAAAALAA4BAgALAAAAkgAAAA8BAgAGAAAAsgAA"
        }
    ],
    "result3": [
        {
            "url": "https://www.lulus.com/blog/wp-content/uploads/2024/02/2597871.jpg",
            "base64": "/9j/4AAQSkZJRgABAQEASABIAAD/2wCEAAYFBQYGBgYGBggJCAYIChAKCgkK"
        }
    ]
}


    return jsonify({
    "errNo": 0,
    "errMsg": "",
    "data": {
        "profile": results_store[req_id]["profile"],
        "query1": results_store[req_id]["query1"],
        "id": req_id,
        "result1": results_store[req_id]["result1"],
        "result2": results_store[req_id]["result2"],
        "result3": results_store[req_id]["result3"]  
    }
})


@app.route('/admin/getResults', methods=['GET'])
def get_results():
    req_id = request.args.get("id")
    selected = request.args.getlist("selectedImageList")

    if req_id not in results_store:
        return jsonify({"errNo": 1, "errMsg": "Invalid ID"}), 404

    result2_list = results_store[req_id].get("result2", [])

    list_data = []
    for selected_url in selected:
        for image_obj in result2_list:
            if image_obj["url"] == selected_url:
                list_data.append({
                    "image": {
                        "url": image_obj["url"],
                        "base64": image_obj["base64"]
                    },
                    "text": "You look so pretty"
                })
                break

    return jsonify({
        "errNo": 0,
        "errMsg": "",
        "data": {"list": list_data}
    })


@app.route('/')
def index():
    return "Flask server is running."

@app.route('/admin/test', methods=['GET'])
def test_connection():
    return "test ok", 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050)

