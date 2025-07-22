import os
import csv

# Allowed media extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webp'}

def get_media_files(directories):
    media_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    media_files.append(os.path.join(root, f))
    return media_files

def read_directories_from_csv(csv_path):
    directories = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:  # skip empty lines
                directories.append(row[0])
    return directories

def write_file_list_to_txt(file_paths, output_txt):
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write("#0\n")
        for path in file_paths:
            f.write(f"{path}\n")

if __name__ == '__main__':
    csv_input = "fileLists\onSsd.csv"      # Your CSV file with directory paths
    output_txt = 'ssdMediaFiles.txt'     # Output text file

    dirs = read_directories_from_csv(csv_input)
    media_files = get_media_files(dirs)
    write_file_list_to_txt(media_files, output_txt)

    print(f"Saved {len(media_files)} media file paths to {output_txt}")
