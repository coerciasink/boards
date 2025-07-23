import os
import requests
import hashlib
import psycopg2
import time
from dotenv import load_dotenv
from pathlib import Path

import logging

log_file_path = os.path.join(os.path.dirname(__file__), "upload.log")
logging.basicConfig(filename=log_file_path, level=logger.info)

load_dotenv()

IMG_CHEST_API_KEY = os.getenv("IMG_CHEST_API_KEY")
HEADERS = {"Authorization": f"Bearer {IMG_CHEST_API_KEY}"}
LIST_FILE_PATH = "ssdMediaFiles.txt"

def connect_db():
    return psycopg2.connect(
        dbname="boards",
        user="postgres",
        password="password",
        host="localhost"
    )

def create_table_if_not_exists(cursor):
    logger.info("[DB] Ensuring image_cache table exists...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_cache (
            hash TEXT PRIMARY KEY,
            link TEXT NOT NULL
        )
    """)

def compute_hash(image_path):
    logger.info(f"[HASH] Computing hash for: {image_path}")
    with open(image_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_link_by_hash(cursor, hash_val):
    cursor.execute("SELECT link FROM image_cache WHERE hash = %s", (hash_val,))
    row = cursor.fetchone()
    if row:
        logger.info(f"[CACHE HIT] Found link for hash {hash_val}")
    else:
        logger.info(f"[CACHE MISS] No link found for hash {hash_val}")
    return row[0] if row else None

def save_link(cursor, hash_val, link):
    cursor.execute("""
        INSERT INTO image_cache (hash, link)
        VALUES (%s, %s)
        ON CONFLICT (hash) DO NOTHING
    """, (hash_val, link))
    logger.info(f"[CACHE SAVE] Saved link to DB: {hash_val} → {link}")

def upload_images(image_paths):
    logger.info(f"[UPLOAD] Uploading {len(image_paths)} image(s)...")
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
        logger.info(f" {path} → {img['link']}")
    return [img["link"] for img in image_list]

def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def read_file_list(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines or not lines[0].startswith("#"):
        raise Exception("First line of file must be a counter starting with '#'")

    current_index = int(lines[0][1:].strip())
    file_paths = [line.strip() for line in lines[1:] if line.strip()]
    return current_index, file_paths

# def write_updated_index(index, lines):
def write_updated_index(index):
    with open(LIST_FILE_PATH, "r+", encoding='utf-8') as f:
        f.write(f"#{index}\n")
        logger.info(f"index updated: {index}\n")
        # for line in lines:
        #     f.write(line + "\n")

def upload_all():
    start_time = time.time()
    conn = connect_db()
    cur = conn.cursor()
    create_table_if_not_exists(cur)

    index, file_paths = read_file_list(LIST_FILE_PATH)
    
    logger.info(f" Starting from index {index} of {len(file_paths)}")

    remaining_files = file_paths[index:]
    logger.info(f"  Processing {len(remaining_files)} files...")

    uncached = []
    for path in remaining_files:
        if not os.path.exists(path):
            logger.info(f" File not found: {path}")
            index += 1
            continue
        uncached.append(path)

    logger.info(f" Ready to upload {len(uncached)} new files")

    def try_upload_with_retries(paths_to_upload, retries=3, delay=1):
        for attempt in range(1, retries + 1):
            try:
                return upload_images(paths_to_upload)
            except Exception as e:
                logger.info(f" Attempt {attempt} failed: {e}")
                if attempt == retries:
                    raise
                time.sleep(delay)

    for batch in chunked(uncached, 18):
        paths_to_upload = batch 
        try:
            uploaded_links = try_upload_with_retries(paths_to_upload)
            for path, link in zip(batch, uploaded_links):
                hash_val = compute_hash(path)
                save_link(cur, hash_val, link)
                index += 1
                write_updated_index(index)
            conn.commit()
            time.sleep(2)  # optional throttle
        except Exception as e:
            logger.info(f" Failed batch upload after retries: {e}")
            break  # stop further uploads

        conn.commit()
        write_updated_index(index)

        logger.info(" Upload complete for batch")
        elapsed_time = time.time() - start_time
        logger.info(f"\n Elapsed time: {elapsed_time:.2f} seconds.")
        filesUploaded = index - indexOriginal
        per_img = int(elapsed_time)/filesUploaded
        logger.info(f"\n {per_img} seconds.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    start_time = time.time()
    index, file_paths = read_file_list(LIST_FILE_PATH)
    indexOriginal = index
    upload_all()
    elapsed_time = time.time() - start_time
    logger.info(f"\n Finished in {elapsed_time:.2f} seconds.")
    indexFinal, file_paths = read_file_list(LIST_FILE_PATH)
    filesUploaded = indexFinal - indexOriginal
    per_img = int(elapsed_time)/filesUploaded

    logger.info(f"\n {per_img} seconds.")

