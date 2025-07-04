import os
import hashlib
import json
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# CONFIG
IMG_FOLDER = 'path/to/images'
HASH_RECORD_FILE = 'imgchest_hashes.json'
# IMG_CHEST_TOKEN = 'YOUR_IMG_CHEST_API_TOKEN' Uncomment if not using config.yml
IMG_CHEST_UPLOAD_URL = 'https://api.imgchest.com/v1/file'

HEADERS = {
    "Authorization": f"Bearer {IMG_CHEST_TOKEN}"
}

# Load or initialize hash record
if os.path.exists(HASH_RECORD_FILE):
    with open(HASH_RECORD_FILE, 'r') as f:
        hash_records = json.load(f)
else:
    hash_records = {}

def get_image_hash(filepath):
    """Return SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def upload_to_imgchest(filepath):
    """Upload a single image and return the direct image link."""
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f)}
        response = requests.post(IMG_CHEST_UPLOAD_URL, headers=HEADERS, files=files)

    if response.status_code == 201:
        data = response.json()
        return data['data']['direct_url']  # <-- direct image URL
    else:
        print(f"Failed to upload {filepath}: {response.text}")
        return None

def process_images(folder):
    output_links = []
    for filename in tqdm(os.listdir(folder)):
        fullpath = os.path.join(folder, filename)
        if not os.path.isfile(fullpath):
            continue
        img_hash = get_image_hash(fullpath)

        if img_hash in hash_records:
            output_links.append(hash_records[img_hash])
        else:
            link = upload_to_imgchest(fullpath)
            if link:
                hash_records[img_hash] = link
                output_links.append(link)

    # Save updated hash record
    with open(HASH_RECORD_FILE, 'w') as f:
        json.dump(hash_records, f, indent=2)

    return output_links

# === Run ===
if __name__ == "__main__":
    links = process_images(IMG_FOLDER)
    print("\nUploaded/Found links:")
    print("\n".join(links))
