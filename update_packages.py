import json
import glob
import os

repo_url = "https://github.com/smg99/fde-lab"

for pkg_json in glob.glob("packages/*/package.json"):
    with open(pkg_json, "r") as f:
        data = json.load(f)
    
    pkg_name = os.path.basename(os.path.dirname(pkg_json))
    if pkg_name == "cli-core":
        continue
    
    data["repository"] = {
        "type": "git",
        "url": f"{repo_url}.git",
        "directory": f"packages/{pkg_name}"
    }
    data["homepage"] = f"{repo_url}/tree/main/packages/{pkg_name}#readme"
    data["bugs"] = {
        "url": f"{repo_url}/issues"
    }
    if "keywords" not in data:
        data["keywords"] = ["fde-lab", "ai", "worker", "agent", pkg_name]
    
    with open(pkg_json, "w") as f:
        json.dump(data, f, indent=2)

print("Updated package.json files")
