import { useEffect, useState } from "react";

function ImageGallery({ useSearchResults = false, files = [] }) {
  const [imageUrls, setImageUrls] = useState([]);

  useEffect(() => {
    if (files.length) return;
    const source = useSearchResults
      ? "/search.results.json"
      : "/image.urls.json";

    fetch(source)
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched image URLs:", data);
        setImageUrls(data);
      })
      .catch((err) => console.error("Failed to load image URLs:", err));
  }, [useSearchResults, files.length]);

  const galleryItems = files.length
    ? files.map((file) => ({
        key: file.id || file.url || file.src,
        src: file.url || file.src,
        alt: file.name || "Uploaded",
      }))
    : imageUrls.map((url) => ({ key: url, src: url, alt: "Uploaded" }));

  const heading = files.length
    ? "Your Pictures"
    : useSearchResults
    ? "Search Results"
    : "Uploaded Images";

  return (
    <div>
      <h2>{heading}</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
        {galleryItems.map((item) => (
          <img
            key={item.key}
            src={item.src}
            alt={item.alt}
            onError={(e) => {
              e.target.src = "/images/placeholder.png";
              e.target.alt = "Image failed to load";
            }}
            style={{
              width: "200px",
              borderRadius: "8px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
              objectFit: "cover",
              backgroundColor: "#0f172a",
            }}
          />
        ))}
      </div>
    </div>
  );
}

export default ImageGallery;
