import os
from collections import defaultdict
from pathlib import Path
import psycopg2
from jinja2 import Template
import yaml

from boards.imgchest import process_images, compute_hash
from boards.mediaBlocks import blocksForUpload, blocksNormal
import extraFiles.upload_batch as ub 
import logging

logger = logging.getLogger(__name__) 

def load_config(yml_path="config.yml"):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()
masterDir = config["masterDir"]

index_index_path = os.path.join(masterDir, "index-index.html")

url_path = index_index_path.replace("\\", "/")

# href_link = Path(masterDir, "index.html").absolute().as_uri() # this is a an absolute path link for the back to index link
href_link = "../index.html"

def makeHtmlBoard(media_files, target_file, media_dir, subfolder_name,
                    template_path='templates/template.html', full_paths=None, 
                    decideUpload=False, page_num=1, total_pages=1):
    return
    




def create_index_file(subfolders, target_directory, template_path='templates/index_template.html'):
    index_file = os.path.join(target_directory, "index.html")

    with open(template_path, "r", encoding="utf-8") as template:
        index_template = template.read()

    # Convert subfolder list into a nested tree
    def build_tree(paths):
        tree = defaultdict(dict)
        for path in paths:
            parts = path.split(os.sep)
            current = tree
            for part in parts:
                current = current.setdefault(part, {})
        return tree

    # Recursively turn tree into nested HTML
    def tree_to_html(tree, path_prefix=""):
        html = "<ul>\n"
        for name in sorted(tree.keys()):
            full_path = os.path.join(path_prefix, name) if path_prefix else name
            file_link = f"{full_path.replace(os.sep, '_')}.html"
            if tree[name]:  # has children
                html += f'<li><a href="{file_link}">{name}\n{tree_to_html(tree[name], full_path)}</a></li>\n'
            else:
                html += f'<li><a href="{file_link}">{name}</a></li>\n'
        html += "</ul>\n"
        return html

    folder_tree = build_tree(subfolders)
    nested_html = tree_to_html(folder_tree)

    html_content = index_template.replace("{{index_links}}", nested_html)
    html_content = html_content.replace("{{ href_link }}", href_link)

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html_content)



def create_css_file(target_directory, config, css_template_path='templates/template.css'):
    with open(css_template_path, "r", encoding="utf-8") as template_file:
        template = Template(template_file.read())
        rendered_css = template.render(config)
    with open(os.path.join(target_directory, "styles.css"), "w", encoding="utf-8") as output_file:
        output_file.write(rendered_css)


def create_js_file(target_directory, js_template_path='templates/template.js'):
    with open(js_template_path, "r", encoding="utf-8") as template:
        js_content = template.read()
    with open(os.path.join(target_directory, "script.js"), "w", encoding="utf-8") as f:
        f.write(js_content)


def create_master_index_file(directories, output_path):
    css_filename = "styles.css"

    content = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "    <meta charset='UTF-8'>",
        "    <title>All Index Pages</title>",
        f"    <link rel='stylesheet' href='{css_filename}'>",
        "</head>",
        "<body>",
        "    <div class='container'>",
        "    <h1>All Index Pages</h1>",
        "    <ul class='index-list'>"
    ]

    for d in directories:
        index_file = os.path.join(d["target_directory"], "index.html")
        try:
            index_path = os.path.relpath(index_file, output_path)
        except ValueError:
            index_path = index_file.replace("\\", "/")  # optional: make it web-friendly

        folder_name = os.path.basename(d["target_directory"])
        content.append(f'        <li><a class="link" href="{index_path}">{folder_name}</a></li>')

    content.append("    </ul>")
    content.append("    </div>")
    content.append("</body>")
    content.append("</html>")

    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(content))





