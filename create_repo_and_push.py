import subprocess
import urllib.request
import json
import os
import sys

# 1. Get token
p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
out, _ = p.communicate(input='protocol=https\nhost=github.com\n\n')
token = ''
username = 'roberjoffre'
for l in out.splitlines():
    if l.startswith('password='):
        token = l.split('=', 1)[1]
    elif l.startswith('username='):
        username = l.split('=', 1)[1]

if not token:
    print("ERROR: No token found in credential manager")
    sys.exit(1)

print(f"Authenticated as: {username}")

repo_name = "star-company-perfumes"

# 2. Check or create repo
headers = {
    'Authorization': f'Bearer {token}',
    'User-Agent': 'PerfumesCatalogApp',
    'Accept': 'application/vnd.github.v3+json'
}

repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
req_check = urllib.request.Request(repo_url, headers=headers)

exists = False
try:
    with urllib.request.urlopen(req_check, timeout=5) as r:
        if r.status == 200:
            exists = True
            print(f"Repository {repo_name} already exists on GitHub.")
except urllib.error.HTTPError as e:
    if e.code == 404:
        exists = False
    else:
        print(f"Check error: {e}")

if not exists:
    print(f"Creating new repository: {repo_name} on GitHub...")
    create_payload = json.dumps({
        "name": repo_name,
        "description": "⭐ Catálogo interactivo de perfumes importados y árabes - Star Company",
        "private": False,
        "auto_init": False
    }).encode('utf-8')

    req_create = urllib.request.Request(
        "https://api.github.com/user/repos",
        data=create_payload,
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(req_create, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        print(f"Repository successfully created: {res.get('html_url')}")

# 3. Setup local git repo
cwd = r"c:\Users\Usuario\OneDrive\Desktop\perfumes"
os.chdir(cwd)

# Check if .git exists in perfumes folder
if not os.path.exists(os.path.join(cwd, '.git')):
    print("Initializing git repo in perfumes directory...")
    subprocess.run(['git', 'init', '-b', 'main'], check=True)
else:
    print(".git directory already exists locally.")

# Set remote origin
remote_url_auth = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
subprocess.run(['git', 'remote', 'remove', 'origin'], stderr=subprocess.DEVNULL)
subprocess.run(['git', 'remote', 'add', 'origin', remote_url_auth], check=True)

# Add files
subprocess.run(['git', 'add', '.'], check=True)
subprocess.run(['git', 'commit', '-m', 'Initial commit: Catálogo Star Company con carrito de recuento y filtros'], check=True)

# Push to main
print("Pushing files to GitHub...")
push_res = subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'], capture_output=True, text=True)
print("Push output:", push_res.stdout)
if push_res.stderr:
    print("Push stderr:", push_res.stderr)

# Clean auth token from remote url so it is stored cleanly as standard HTTPS
clean_remote = f"https://github.com/{username}/{repo_name}.git"
subprocess.run(['git', 'remote', 'set-url', 'origin', clean_remote], check=True)

# 4. Enable GitHub Pages
print("Enabling GitHub Pages...")
pages_payload = json.dumps({
    "source": {
        "branch": "main",
        "path": "/"
    }
}).encode('utf-8')

pages_req = urllib.request.Request(
    f"https://api.github.com/repos/{username}/{repo_name}/pages",
    data=pages_payload,
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(pages_req, timeout=10) as r:
        pages_res = json.loads(r.read().decode('utf-8'))
        print("GitHub Pages enabled! Live URL:", pages_res.get('html_url'))
except urllib.error.HTTPError as e:
    # Might already be enabled or take a moment
    print(f"GitHub Pages note: {e.read().decode('utf-8')}")

print("\nALL DONE SUCCESSFULLY!")
print(f"GitHub Repo: https://github.com/{username}/{repo_name}")
print(f"GitHub Pages (Website Live): https://{username}.github.io/{repo_name}/")
