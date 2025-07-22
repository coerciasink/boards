import os
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import logging

logger = logging.getLogger(__name__) 

# Load the .env file
load_dotenv()

IMG_CHEST_API_KEY = os.getenv("IMG_CHEST_API_KEY")
HEADERS = {"Authorization": f"Bearer {IMG_CHEST_API_KEY}"}

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

# Based loosely on keikazuki's approach
def upload_image(image_path):
    with open(image_path, 'rb') as f:
        files = {'images[]': (os.path.basename(image_path), f, 'image/jpeg')}
        data = {'title': os.path.basename(image_path)}
        resp = requests.post("https://api.imgchest.com/v1/post", headers=HEADERS, files=files, data=data)

    resp.raise_for_status()
    post_id = resp.json()["data"]["id"]

    # Now get the image info
    info = requests.get(f"https://api.imgchest.com/v1/post/{post_id}", headers=HEADERS)
    info.raise_for_status()

    image_list = info.json()["data"]["images"]
    if not image_list:
        raise Exception("No images returned in response")

    return image_list[0]["link"]

def process_images(image_paths):
    try:
        conn = connect_db()
        cur = conn.cursor()
        create_table_if_not_exists(cur)

        results = []

        for image_path in image_paths:
            hash_val = compute_hash(image_path)
            cached_link = load_link_by_hash(cur, hash_val)

            if cached_link:
                # print(f"🔁 Cached: {image_path} → {cached_link}")
                results.append(cached_link)
                continue

            try:
                direct_link = upload_image(image_path)
                logging.info(f"⬆️ Uploaded {image_path} → {direct_link}")
                save_link(cur, hash_val, direct_link)
                # print(f"📝 Saved to DB: {hash_val[:10]} → {direct_link}")
                results.append(direct_link)
                conn.commit()
            except Exception as e:
                logging.warning(f"❌ Upload error for {image_path}: {e}")

        conn.commit()
        dir = os.path.dirname(image_paths[0])
        logging.info(f"Commit successful. for {dir}")
        cur.close()
        conn.close()
        return results

    except Exception as e:
        logging.info(f"❌ Critical DB error: {e}")
        return []
