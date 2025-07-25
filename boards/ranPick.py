import os
import random
from boards.filemaking.file_utils import create_html_file
import logging
import yaml

def load_config(yml_path="config.yml"):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
from math import ceil

config = load_config()
logger = logging.getLogger(__name__) 

def get_all_images_recursively(base_dir):
    valid_exts = ('.jpg', '.jpeg', '.png')
    image_paths = []

    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(valid_exts):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir)
                image_paths.append((full_path, rel_path))  # (absolute, relative)
    return image_paths

def gen_random(imageList, count, target_dir, input_dir, paginate=False, page_size=config["page_size"], decideUpload=False):
    if not imageList:
        logger.waring("No images found.")
        return

    sampled_images = random.sample(imageList, count)
    if paginate:
        total_pages = ceil(len(sampled_images) / page_size)
        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * page_size
            end = start + page_size
            paginated = sampled_images[start:end]
            output_file = os.path.join(target_dir, f"random_page{page_num}.html")

            create_html_file(
                media_files=paginated,
                target_file=output_file,
                media_dir=input_dir,
                subfolder_name="random",
                decideUpload=decideUpload,
                page_num=page_num,
                total_pages=total_pages
            )
    else:
        output_file = os.path.join(target_dir, f"random.html")
        create_html_file(sampled_images, output_file, input_dir, "random", decideUpload=False)

    logger.info(f"Created: {output_file}")
