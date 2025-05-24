import shutil
import os
from boards.file_utils import create_html_file, create_css_file, create_js_file
import csv

def copy_images_to_directory(image_names, source_dir, target_dir):
    """
    Copy images from source directory to target directory.
    """
    os.makedirs(os.path.join(target_dir, "images"), exist_ok=True)
    for image_name in image_names:
        shutil.copy(os.path.join(source_dir, image_name), os.path.join(target_dir, "images", image_name))


def getDirList(csvList, masterDir):
    all_rows = []
    for csv_path in csvList:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Prepend masterDir to target_directory
                row["target_directory"] = os.path.join(masterDir, row["target_directory"])
                all_rows.append(row)
    return all_rows

