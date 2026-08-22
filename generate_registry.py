import json
import glob
import os

packages = []
for pkg_json in glob.glob("packages/*/package.json"):
    with open(pkg_json, "r") as f:
        data = json.load(f)
    
    pkg_name = os.path.basename(os.path.dirname(pkg_json))
    if pkg_name == "cli-core":
        continue
        
    npm_name = data["name"]
    version = data["version"]
    worker_id = pkg_name.replace("-", "_")
    
    packages.append({
        "worker_id": worker_id,
        "npm_package": npm_name,
        "version": version,
        "source_directory": f"packages/{pkg_name}",
        "github_url": f"https://github.com/smg99/fde-lab/tree/main/packages/{pkg_name}",
        "npm_url": f"https://www.npmjs.com/package/{npm_name}",
        "publication_status": "published",
        "cli_command": f"npx {npm_name}"
    })

os.makedirs("registry", exist_ok=True)
with open("registry/packages.json", "w") as f:
    json.dump(packages, f, indent=2)

print("Generated registry/packages.json")
