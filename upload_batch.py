import os
import csv
import requests
import hashlib
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
import time



load_dotenv()

IMG_CHEST_API_KEY = os.getenv("IMG_CHEST_API_KEY")
HEADERS = {"Authorization": f"Bearer {IMG_CHEST_API_KEY}"}

# Hardcoded paths
master_dir = os.path.dirname(__file__)
csv_files = [
    # "fileLists/misc.csv",
    "fileLists/onSsd.csv",
    # "fileLists/pinterest.csv"
]

def connect_db():
    return psycopg2.connect(
        dbname="boards",
        user="postgres",
        password="password",
        host="localhost"
    )

def create_table_if_not_exists(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_cache (
            hash TEXT PRIMARY KEY,
            link TEXT NOT NULL
        )
    """)

def compute_hash(image_path):
    with open(image_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_link_by_hash(cursor, hash_val):
    cursor.execute("SELECT link FROM image_cache WHERE hash = %s", (hash_val,))
    row = cursor.fetchone()
    return row[0] if row else None

def save_link(cursor, hash_val, link):
    cursor.execute("""
        INSERT INTO image_cache (hash, link)
        VALUES (%s, %s)
        ON CONFLICT (hash) DO NOTHING
    """, (hash_val, link))

def upload_images(image_paths):
    files = []
    for image_path in image_paths:
        with open(image_path, 'rb') as f:
            filename = os.path.basename(image_path)
            files.append(('images[]', (filename, f.read(), 'image/jpeg')))

    data = {'title': os.path.basename(image_paths[0])}
    resp = requests.post("https://api.imgchest.com/v1/post", headers=HEADERS, files=files, data=data)
    resp.raise_for_status()

    post_id = resp.json()["data"]["id"]

    info = requests.get(f"https://api.imgchest.com/v1/post/{post_id}", headers=HEADERS)
    info.raise_for_status()

    image_list = info.json()["data"]["images"]
    if not image_list or len(image_list) != len(image_paths):
        raise Exception("Mismatch in uploaded image count")

    for path, img in zip(image_paths, image_list):
        print(f"⬆️ {path} → {img['link']}")
    return [img["link"] for img in image_list]

def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def get_dirs_from_csv(csv_paths):
    dirs = []
    for csv_file in csv_paths:
        full_path = os.path.join(master_dir, csv_file)
        if not os.path.exists(full_path):
            print(f"⚠️ File not found: {full_path}")
            continue
        with open(full_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    dirs.append(row[0])
    return dirs

def gather_media_files(directories):
    media_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webp'):
                    media_files.append(os.path.join(root, f))
    return media_files


def upload_all():
    conn = connect_db()
    cur = conn.cursor()
    create_table_if_not_exists(cur)

    directories = get_dirs_from_csv(csv_files)
    print(f"📁 Found {len(directories)} directories")

    media_files = gather_media_files(directories)
    print(f"🖼️  Found {len(media_files)} media files")

    # Step 1: Filter only uncached files
    uncached = []
    for path in media_files:
        hash_val = compute_hash(path)
        if not load_link_by_hash(cur, hash_val):
            uncached.append((path, hash_val))
        # else:
            # print(f"✅ Already uploaded: {path}")

    print(f"🚀 Ready to upload {len(uncached)} new files")

    # Step 2: Upload in batches of 20
    for batch in chunked(uncached, 20):
        paths_to_upload = [p for p, _ in batch]
        hashes = [h for _, h in batch]

        try:
            uploaded_links = upload_images(paths_to_upload)
            for (path, hash_val), link in zip(batch, uploaded_links):
                save_link(cur, hash_val, link)
                # print(f"📝 Saved to DB: {hash_val[:10]} → {link} | {path}")
        except Exception as e:
            print(f"❌ Failed batch upload: {e}")

        conn.commit()

    cur.close()
    conn.close()
    print("✅ Upload complete")


if __name__ == "__main__":
    start_time = time.time()
    upload_all()
    elapsed_time = time.time() - start_time
    print(f"\n✅ Finished in {elapsed_time:.2f} seconds.")

