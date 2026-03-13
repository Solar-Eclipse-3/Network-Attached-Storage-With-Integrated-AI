from firebase_file_ops import download_file, upload_file
from filewizard_ai import sort_and_tag_file
import os

# Pipeline for FileWizardAi to download, sort, and reupload files
def run_pipeline(file_name):
    # Save the file in ./temp/ with its base name
    local_path = os.path.join("temp", os.path.basename(file_name))

    # Makes sure ./temp/ exists
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    download_file(file_name, local_path)

    tags = sort_and_tag_file(local_path)
    tag_path = "_".join(tags) if tags else "unsorted"
    new_cloud_path = f"sorted/{tag_path}/{os.path.basename(file_name)}"

    upload_file(local_path, new_cloud_path)