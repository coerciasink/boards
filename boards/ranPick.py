
import os
import random
from boards.file_utils import create_html_file, create_css_file, create_js_file

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



def gen_random(input_dir, count, output_dir):
    images = get_all_images_recursively(input_dir)
    if not images:
        print("No images found.")
        return

    selected = random.sample(images, min(count, len(images)))

    media_files = [rel for abs, rel in selected]
    subfolder_name = f"{os.path.basename(input_dir)}"
    output_file = os.path.join(output_dir, f"{subfolder_name}.html")

    create_html_file(
        media_files=media_files,
        target_file=output_file,
        media_dir=input_dir,
        subfolder_name=subfolder_name
    )

    print(f"Created: {output_file}")
