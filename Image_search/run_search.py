from Image_search.searcher import search

def main():
    query_image = "https://firebasestorage.googleapis.com/v0/b/your-bucket/o/MinecraftIcon2.png?alt=media"
    top_k = 5

    results = search(query_image, top_k=top_k)
    print(f"\n🔍 Top {top_k} matches for: {query_image}\n")
    for i, (path, score) in enumerate(results, 1):
        print(f"{i}. {path} — Similarity: {score:.3f}")

if __name__ == "__main__":
    main()
