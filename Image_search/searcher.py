import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from Image_search.embedder import get_embedding
import json

def search(query_image_path, top_k=5, emb_file="embeddings.npy", path_file="image_paths.txt", metadata_file="dist/image.metadata.json"):
    # Step 1: Filter filenames by tags
    query_tags = query_image_path.lower().split()
    with open(metadata_file) as f:
        metadata = json.load(f)

    matching_files = [
        fname for fname, tags in metadata.items()
        if all(tag in tags for tag in query_tags)
    ]

    # Step 2: Load all URLs and embeddings
    with open(path_file, "r") as f:
        all_urls = f.read().splitlines()
    all_embs = np.load(emb_file)

    # Step 3: Filter URLs and embeddings
    filtered_data = [
        (url, emb) for url, emb in zip(all_urls, all_embs)
        if url.split("/")[-1] in matching_files
    ]

    if not filtered_data:
        print("⚠️ No matching images found for tags:", query_tags)
        return []

    filtered_urls, filtered_embs = zip(*filtered_data)

    # Step 4: Embed the query image
    query_emb = get_embedding(query_image_path).reshape(1, -1)

    # Step 5: Compare against filtered embeddings
    scores = cosine_similarity(query_emb, np.array(filtered_embs))[0]
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = [(filtered_urls[i], float(scores[i])) for i in top_indices]
    return results

def search_by_tags(tag_query, metadata_file="dist/image.metadata.json", path_file="image_paths.txt"):
    import json

    query_tags = tag_query.lower().split()
    with open(metadata_file) as f:
        metadata = json.load(f)

    matching_files = [
        fname for fname, tags in metadata.items()
        if all(tag in tags for tag in query_tags)
    ]

    if not matching_files:
        print("⚠️ No matches found for:", tag_query)
        return []

    with open(path_file, "r") as f:
        all_urls = f.read().splitlines()

    results = [
        url for url in all_urls
        if url.split("/")[-1] in matching_files
    ]
    return results

def save_results_to_json(results, output_path="dist/search.results.json"):
    import json
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
