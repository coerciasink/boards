import csv
import os
import argparse
import yaml
from pathlib import Path
from boards.imgchest import process_images, connect_db
import time

start_time = time.time()



def load_config(yml_path="config.yml"):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def getDirList(csvList, base_dir):
    all_dirs = []
    for csv_file in csvList:
        csv_path = os.path.join(base_dir, csv_file)
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            continue
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    all_dirs.append(row[0])
    return all_dirs

def gather_all_files_from_dirs(dir_list):
    media_files = []
    for directory in dir_list:
        for root, _, files in os.walk(directory):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.jpg', '.jpeg', '.png', '.gif', '.mp4'):
                    media_files.append(os.path.join(root, f))
    return media_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload all media files from CSV-specified directories.")
    parser.add_argument("--dir", help="Optional single directory to upload")
    args = parser.parse_args()

    # Load config and determine base directory
    config = load_config()
    base_dir = os.path.dirname(__file__)
    csvList = config.get("csvList", [])

    # Ensure DB table exists
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS image_cache (
        hash TEXT PRIMARY KEY,
        link TEXT NOT NULL
    )
    """)


    

    # Determine which directories to upload
    if args.dir:
        directories = [args.dir]
    else:
        directories = getDirList(csvList, base_dir)

    print(f"Found directories: {directories}")
    media_files = gather_all_files_from_dirs(directories)
    print(f"Uploading {len(media_files)} media files...")

    process_images(media_files)

    conn.commit()
    cur.close()
    conn.close()

    elapsed_time = time.time() - start_time
    print(f"\n✅ Finished in {elapsed_time:.2f} seconds.")
