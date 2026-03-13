import requests
import sys
from pathlib import Path

class NASClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url

    def upload_file(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/upload", files=files)
            return response.json()

    def download_file(self, filename, save_path=None):
        response = requests.get(f"{self.base_url}/download/{filename}", stream=True)
        if response.status_code == 200:
            save_path = save_path or filename
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return {"message": f"File downloaded successfully to {save_path}"}
        return response.json()

    def list_files(self):
        response = requests.get(f"{self.base_url}/list")
        return response.json()

    def delete_file(self, filename):
        response = requests.delete(f"{self.base_url}/delete/{filename}")
        return response.json()

def print_usage():
    print("""
Usage: python nas_client.py [--url SERVER_URL] <command> [arguments]
Commands:
    upload <file_path>          - Upload a file to the NAS
    download <filename>         - Download a file from the NAS
    list                       - List all files in the NAS
    delete <filename>          - Delete a file from the NAS
    """)

def main():
    base_url = "http://localhost:5000"
    args = sys.argv[1:]

    # Check for --url parameter
    if len(args) >= 2 and args[0] == "--url":
        base_url = args[1]
        args = args[2:]

    if len(args) < 1:
        print_usage()
        return

    client = NASClient(base_url)
    command = args[0]

    try:
        if command == "upload" and len(args) == 2:
            result = client.upload_file(args[1])
        elif command == "download" and len(args) == 2:
            result = client.download_file(args[1])
        elif command == "list":
            result = client.list_files()
        elif command == "delete" and len(args) == 2:
            result = client.delete_file(args[1])
        else:
            print_usage()
            return
        
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 