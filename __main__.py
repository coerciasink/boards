import os
import yaml
import argparse
import time

start_time = time.time()

from boards.file_utils import create_html_file, create_css_file, create_js_file, create_index_file, create_master_index_file
from boards.dir_utils import getDirList
from boards.ranPick import gen_random
from boards.imgchest import process_images


def load_config(yml_path="config.yml"):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    

parser = argparse.ArgumentParser(description="Generate HTML for media directories.")
parser.add_argument('--random', type=int, help="Select N random images from a directory and generate HTML.")
parser.add_argument('--ranDir', type=str, help="Directory to search images in for --random")
parser.add_argument('--dir', type=str, help="Directory to use for the images")
parser.add_argument('--csvs', nargs='+', help='List of CSV files to use')
parser.add_argument('--col', type=int, help='number of columns to default to (default is set in the config)')
parser.add_argument('--margin', type=int, help='Margin in px (default is set in the config)')
parser.add_argument('--upload', action='store_true', help='Upload images to Imgchest and replace local paths with uploaded URLs')
args = parser.parse_args()

config = load_config()

if args.upload:
    masterDir = os.path.join(os.path.dirname(config["masterDir"]), 'boardsUpload')
else:
    masterDir = config["masterDir"]

# choice = input("which csvs to choose?\n1. misc\n2. SSD files\n3. pinterest\n4. All\n")
# add more options to include more combinations of csv files. 
# choice = 4 # for test puposes

# Determine CSV list
csvList = args.csvs if args.csvs else config.get("csvList", [])


config = {
    'col_count': args.col if args.col else config.get("col_count", []),
    'margin': args.margin if args.margin else config.get("margin", []),
}


if not csvList:
    print("No CSV files provided. Set them in config.yml or pass using --csvs.")
    exit(1)


ranDir = os.path.join(masterDir, "randomised")

if args.random and args.ranDir:
    try:
        gen_random(args.dir, args.random, ranDir)
    except:
        os.makedirs(ranDir, exist_ok=True)
        create_css_file(ranDir, config)
        create_js_file(ranDir)
        gen_random(args.ranDir, args.random, ranDir)
    # exit(0)

if args.dir:
    directories = [{'source_directory': args.dir, 'target_directory': os.path.join(masterDir, 'specifiedDir')}]
else:
    directories = getDirList(csvList, masterDir)

for directory_info in directories:
    source_directory = directory_info["source_directory"]
    target_directory = directory_info["target_directory"]

    subfolders = {}

    # Walk through all subfolders
    for root, _, files in os.walk(source_directory):
        rel_path = os.path.relpath(root, source_directory)
        if rel_path == ".":
            continue  # Skip the base folder itself

        subfolders[rel_path] = sorted(files)

    os.makedirs(target_directory, exist_ok=True)

    # Create HTML files for each subfolder
    for subfolder, files in subfolders.items():
        subfolder_path = os.path.join(source_directory, subfolder)
        subfolder_file = f"{subfolder.replace(os.sep, '_')}.html"  # Replace slashes with underscores
        output_file = os.path.join(target_directory, subfolder_file)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)  #  Ensure parent directory exists
        # uploaded_links = process_images(files) # upload

        create_html_file(files, output_file, subfolder_path, subfolder, decideUpload=args.upload)


    # Create main index file linking to all subfolder pages
    create_index_file(subfolders.keys(), target_directory)
    # After all individual target directory processing
    create_master_index_file(directories, masterDir)


    # Generate CSS & JS (only needed once)
    create_css_file(target_directory, config)
    create_js_file(target_directory)
    print(f"finished with {source_directory}")

create_css_file(masterDir, config)
create_js_file(masterDir)

elapsed_time = time.time() - start_time
print(f"\n✅ Finished in {elapsed_time:.2f} seconds.")
