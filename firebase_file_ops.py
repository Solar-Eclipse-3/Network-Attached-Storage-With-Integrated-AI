from firebase_config import bucket
import os
import json
from urllib.parse import quote

# Lets FileWizardAi download files in Firebase
def download_file(file_name, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    blob = bucket.blob(file_name)
    blob.download_to_filename(local_path)
    print(f"✅ Downloaded {file_name} to {local_path}")
    
# Lets FileWizardAi upload files to Firebase after sorting
def upload_file(local_path, cloud_path):
    blob = bucket.blob(cloud_path)
    blob.upload_from_filename(local_path)
    blob.make_public()
    print(f"✅ Uploaded {local_path} to {cloud_path}")
    print(f"🌐 Public URL: {blob.public_url}")
    return blob.public_url

# Lists all items inside firebase storage for FileWizardAi to access
def list_files(prefix=""):
    blobs = bucket.list_blobs(prefix=prefix)
    for blob in blobs:
        print(blob.name)

# Deletes a file from storage
def delete_file(blob_name):
    blob = bucket.blob(blob_name)
    if blob.exists():
        blob.delete()
        print(f"✅ Deleted {blob_name}")
    else:
        print(f"⚠️ File not found: {blob_name}")

# Sorts all files in storage by name, type, or date.
def sort_files(prefix="", by="name"):
    """
    :param prefix: Folder path (e.g., "uploads/")
    :param by: "name", "type", or "date"
    """
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    if not blobs:
        print("No files found.")
        return

    if by == "name":
        blobs.sort(key=lambda b: b.name.lower())
    elif by == "type":
        blobs.sort(key=lambda b: b.content_type or "")
    elif by == "date":
        blobs.sort(key=lambda b: b.updated or b.time_created)
    else:
        print(f"⚠️ Unknown sort key: {by}")
        return

    print(f"📂 Sorted files in '{prefix}' by {by}:")
    for blob in blobs:
        print(f"• {blob.name} ({blob.content_type}, updated {blob.updated})")

# get urls of the images upload to firebase
def get_public_urls(prefix="uploads/"):
    blobs = bucket.list_blobs(prefix=prefix)
    urls = []

    for blob in blobs:
        blob.make_public()
        urls.append(blob.public_url)

    return urls

def save_urls_to_json(prefix="uploads/", output_file="public/image.urls.json"):
    urls = get_public_urls(prefix)
    with open(output_file, "w") as f:
        json.dump(urls, f, indent=2)
    print(f"✅ Saved {len(urls)} URLs to {output_file}")
    