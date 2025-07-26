import os
import argparse
from jinja2 import Template
from Crypto.Cipher import AES
import base64
import hashlib
import logging

logger = logging.getLogger(__name__) 

# --- Find all .html files in a directory recursively ---
def find_html_files(directory):
    html_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".html"):
                html_files.append(os.path.join(root, file))
    return html_files

# --- Padding for AES encryption (PKCS7) ---
# Padding function that works with bytes
def pad(data: bytes) -> bytes:
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)

def encrypt_html_content(html_content: str, password: str) -> str:
    key = hashlib.sha256(password.encode()).digest()
    iv = b'\x00' * 16  # For consistent output. Replace with random IV for better security.
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext_bytes = html_content.encode("utf-8")
    padded = pad(plaintext_bytes)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode("utf-8")


# --- Inject encrypted body into template ---
def create_encrypted_html(input_html_path, output_html_path, password, template_path="encrypted_template.html"):
    with open(input_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    encrypted_html = encrypt_html_content(html_content, password)

    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    final_html = template.render(ENCRYPTED_HTML=encrypted_html)

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f" Encrypted: {output_html_path}")

# --- Main script ---
def main():
    parser = argparse.ArgumentParser(description="Encrypt the <body> of HTML files in a directory.")
    parser.add_argument("-i", "--input", required=True, help="Path to the directory")
    parser.add_argument("-p", "--password", required=True, help="Password to use for encryption")
    args = parser.parse_args()

    html_files = find_html_files(args.input)
    template_path = os.path.join("templates", "encrypted_template.html")

    for file in html_files:
        create_encrypted_html(file, file, args.password, template_path)

if __name__ == "__main__":
    main()
