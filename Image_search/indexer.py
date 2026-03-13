import numpy as np
import requests
from io import BytesIO
from .embedder import get_embedding
import json

def build_index_from_json(json_path: str, output_emb_file: str = "embeddings.npy", output_path_file: str = "image_paths.txt"):
    with open(json_path, "r") as f:
        image_urls = json.load(f)

    embeddings = []
    valid_urls = []

    for url in image_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            emb = get_embedding(BytesIO(response.content))  # Pass image bytes
            embeddings.append(emb)
            valid_urls.append(url)
            print(f"✅ Indexed: {url}")
        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")

    np.save(output_emb_file, np.array(embeddings))
    with open(output_path_file, "w") as f:
        for url in valid_urls:
            f.write(url + "\n")

    print(f"\n📦 Saved {len(valid_urls)} embeddings to {output_emb_file}")
    print(f"📝 Saved image URLs to {output_path_file}")
