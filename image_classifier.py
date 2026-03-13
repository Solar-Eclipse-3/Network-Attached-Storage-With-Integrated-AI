import torch
from torchvision import models, transforms
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import json
import requests
from io import BytesIO
import colorsys
import re

# Load pretrained ResNet50
_model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
_model.eval()

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def classify_image(local_path):
    img = Image.open(local_path).convert("RGB")
    tensor = _transform(img).unsqueeze(0)   # type: ignore

    with torch.no_grad():
        output = _model(tensor)
        label_idx = output.argmax().item()
        label = models.ResNet50_Weights.DEFAULT.meta["categories"][label_idx]

    # Normalize label to 'car' if it's a vehicle
    label = label.lower()
    if any(x in label for x in ["car", "van", "jeep", "pickup", "suv", "wagon", "convertible"]):
        label = "car"

    color = detect_dominant_color(img)
    return [label, color]

def classify_pet(local_path):
    img = Image.open(local_path).convert("RGB")
    tensor = _transform(img).unsqueeze(0) # type: ignore

    with torch.no_grad():
        output = _model(tensor)
        label_idx = output.argmax().item()
        label = models.ResNet50_Weights.DEFAULT.meta["categories"][label_idx].lower()
        label = label.replace("_", " ")

    tags = []

    # Regex-based normalization
    if re.search(r"\b(dog|puppy|collie|hound|terrier|retriever|bulldog)\b", label):
        tags.append("dog")
    elif re.search(r"\b(cat|kitten|tabby|siamese|persian)\b", label):
        tags.append("cat")

    tags.append(label)
    return tags

def classify_any(local_path):
    # Try car first
    tags = classify_image(local_path)
    if "car" in tags:
        return tags
    # Otherwise, try pet
    return classify_pet(local_path)

def detect_dominant_color(img, k=3):
    w, h = img.size
    crop = img.crop((w//4, h//4, 3*w//4, 3*h//4)).resize((50, 50))
    pixels = np.array(crop).reshape(-1, 3)

    pixels = [p for p in pixels if not (p[0] < 50 and p[1] < 50 and p[2] < 50)]
    if not pixels:
        pixels = np.array(crop).reshape(-1, 3)

    kmeans = KMeans(n_clusters=k, random_state=0).fit(pixels)
    counts = Counter(kmeans.labels_)
    dominant_index = counts.most_common(1)[0][0]
    dominant_rgb = kmeans.cluster_centers_[dominant_index]

    return map_rgb_to_color_name(dominant_rgb)

def map_rgb_to_color_name(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

    if s < 0.2:
        if v > 0.8: return "white"
        elif v < 0.2: return "black"
        else: return "gray"

    if h < 0.05 or h > 0.95: return "red"
    elif 0.55 < h < 0.75: return "blue"
    elif 0.25 < h < 0.45: return "green"
    elif 0.1 < h < 0.25: return "yellow"
    else: return "unknown"

def generate_metadata(url_json_path="public/image.urls.json", output_path="public/image.metadata.json"):
    with open(url_json_path) as f:
        urls = json.load(f)

    metadata = {}
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_bytes = BytesIO(response.content)

            tags = classify_any(img_bytes)   # use unified classifier
            filename = url.split("/")[-1]
            metadata[filename] = tags
            print(f"✅ Tagged {filename}: {tags}")

        except Exception as e:
            print(f"⚠️ Failed to classify {url}: {e}")

    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\n📝 Saved metadata to {output_path}")
