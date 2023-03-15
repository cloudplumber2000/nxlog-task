import argparse
import requests
from urllib.parse import urlparse, urlsplit, urlunsplit
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Script to download PNG files from a URL.')
parser.add_argument('url', type=str, help='URL to download from')
parser.add_argument('output_dir', type=str, help='Output directory path')
parser.add_argument('--username', type=str, help='Username for Basic Authentication')
parser.add_argument('--password', type=str, help='Password for Basic Authentication')
args = parser.parse_args()

args_url_sanitized = urlparse(args.url)
args_url_scheme = args_url_sanitized.scheme

response = requests.get(args.url, allow_redirects=True)
response.raise_for_status()

if response.status_code == 401:
    if not (args.username and args.password):
        print("This URL requires Basic Authentication. Please provide a username and password.")
        args.username = input("Enter username: ")
        args.password = input("Enter password: ")
    response = requests.get(args.url, headers={'Authorization': requests.auth.HTTPBasicAuth(args.username, args.password)}, allow_redirects=True)
    response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

png_files = []

for img in soup.find_all('img'):
    src = img.get('src')
    validate_src = urlsplit(src)
    if ".png" in validate_src.path.lower() or ".png" in validate_src.query.lower():
        if all([validate_src.scheme, validate_src.netloc, validate_src.path]):
            png_files.append(urlunsplit(validate_src))
        elif all([validate_src.netloc, validate_src.path]):
            validate_src = validate_src._replace(scheme=args_url_scheme)
            png_files.append(urlunsplit(validate_src))
        elif not "base64" in validate_src.path:
            validate_src = validate_src._replace(scheme=args_url_scheme, netloc=args_url_sanitized.netloc)
            png_files.append(urlunsplit(validate_src))
            
for png_file in png_files:
    response = requests.get(png_file, allow_redirects=True)
    response.raise_for_status()
    with open(f"{args.output_dir}/{png_file.split('/')[-1]}", 'wb') as f:
        f.write(response.content)
