import os
import yaml
import argparse
import time
start_time = time.time()
import logging
from datetime import date
from boards.filemaking.file_utils import create_html_file, create_css_file, create_js_file, create_index_file, create_master_index_file
from boards.dir_utils import getDirList
from boards.ranPick import gen_random
from math import ceil
import traceback


# set up logger
today = date.today()
from boards.log_utils import setup_logger
logger = setup_logger(__name__)
logger.info(f"today is {today}, Starting application...")
   

# arguments 
parser = argparse.ArgumentParser(description="Generate HTML for media directories.")
parser.add_argument('--random', type=int, help="Select N random images from a directory and generate HTML.")
parser.add_argument('--ranDir', type=str, help="Directory to search images in for --random")
parser.add_argument('--dir', type=str, help="Directory to use for the images")
parser.add_argument('--csvs', nargs='+', help='List of CSV files to use')
parser.add_argument('--useLists', action='store_true', help='use list files from config')
parser.add_argument('--imageLists', nargs='+', help='List of imagelist files to use. videos can be used too, probably')
parser.add_argument('--col', type=int, help='number of columns to default to (default is set in the config)')
parser.add_argument('--margin', type=int, help='Margin in px (default is set in the config)')
parser.add_argument('--upload', action='store_true', help='Upload images to Imgchest and replace local paths with uploaded URLs')
args = parser.parse_args()

# config
def load_config(yml_path="config.yml"):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

configCss = {
    'col_count': args.col if args.col else config.get("col_count", []),
    'margin': args.margin if args.margin else config.get("margin", []),
}

# default case when pagination is not applied
total_pages = 1 
page_num = 1

# use lists?
if args.useLists or args.imageLists:
    listDir = os.path.join(os.path.dirname(config["masterDir"]), 'imglists')
    os.makedirs(listDir, exist_ok=True)
    usingLists = True
    imgList_List = args.imageLists if args.imageLists else config.get("imageLists", []) # list of list images.
    base_dir = os.path.dirname(__file__)
    
    
    for imgList in imgList_List:
        imgListFile = os.path.join(base_dir, imgList)
        with open(imgListFile, "r", encoding="utf-8") as f:
            images = [line.strip() for line in f if line.strip()] # essentially removes newlines and empty lines, and each line is a list item of list - images.

        filename = os.path.splitext(os.path.basename(imgListFile))[0]
        create_css_file(listDir, configCss)
        create_js_file(listDir)

        if config["paginate"]:
            page_size = config["page_size"]
            total_items = len(images)
            total_pages = ceil(total_items / page_size)

        for page_num in range(1, total_pages + 1):

            start_idx = (page_num - 1) * page_size
            end_idx = start_idx + page_size
            paginated_images = images[start_idx:end_idx]            

            output_file = os.path.join(listDir, f"{filename}_page{page_num}.html")
            
            logger.info(f"Generating page {page_num}/{total_pages} for {filename}")

            create_html_file(
                media_files=paginated_images,
                target_file=output_file,
                media_dir=listDir,
                subfolder_name=filename,
                decideUpload=False,
                page_num=page_num,
                total_pages=total_pages
    )
    

# upload?
if args.upload:
    logger.info("upload case")
    masterDir = os.path.join(os.path.dirname(config["masterDir"]), 'boardsUpload')
else:
    masterDir = config["masterDir"]

# get the dir list
csvList = args.csvs if args.csvs else config.get("csvList", [])
if not csvList:
    logger.info("No CSV files provided. Set them in config.yml or pass using --csvs.")
    exit(1)

if args.dir:
    directories = [{'source_directory': args.dir, 'target_directory': os.path.join(masterDir, 'specifiedDir')}]
else:
    directories = getDirList(csvList, masterDir)

from boards.dir_utils import getAllFiles
from boards.ranPick import get_all_images_recursively

# random ?
if args.random:
    logger.info("random case")
    if not args.ranDir:
        imageList = getAllFiles(csvList)
    else:
        imageList = get_all_images_recursively(args.dir)

    # workDir = masterDir + 'randomised'
    workDir = masterDir
    logger.info(f"{workDir}")

    os.makedirs(workDir, exist_ok=True)
    create_css_file(workDir, configCss)
    create_js_file(workDir)

    decideUpload = args.upload

    logger.info("upload? %s", decideUpload)

    try:
        gen_random(imageList, args.random, workDir, workDir, paginate=config["paginate"], page_size=config["page_size"], decideUpload=decideUpload)
    except Exception as e:
        logger.info(f"Error: {e}")
        logger.error(traceback.format_exc())

# normal case
if not args.random and not usingLists:
    logger.info("normal case")
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

            if config["paginate"]:
                page_size = config["page_size"]
                total_pages = ceil(len(files) / page_size)
                for page_num in range(1, total_pages + 1):
                    start_idx = (page_num - 1) * page_size
                    end_idx = start_idx + page_size
                    paginated_files = files[start_idx:end_idx]

                    output_file = os.path.join(target_directory, f"{subfolder.replace(os.sep, '_')}_page{page_num}.html")

                    create_html_file(
                        media_files=paginated_files,
                        target_file=output_file,
                        media_dir=subfolder_path,
                        subfolder_name=subfolder,
                        decideUpload=args.upload,
                        page_num=page_num,
                        total_pages=total_pages
                    )
            else:
                create_html_file(files, output_file, subfolder_path, subfolder, decideUpload=args.upload)


        # Create main index file linking to all subfolder pages
        create_index_file(subfolders.keys(), target_directory)
        # After all individual target directory processing
        create_master_index_file(directories, masterDir)


        # Generate CSS & JS (only needed once)
        create_css_file(target_directory, configCss)
        create_js_file(target_directory)
        logger.info(f"finished with {source_directory}")

# closing stuff
create_css_file(masterDir, configCss)
create_js_file(masterDir)

elapsed_time = time.time() - start_time
logger.info(f"\n Finished in {elapsed_time:.2f} seconds.")
