import json
import glob

for pkg_json in glob.glob("packages/*/package.json"):
    with open(pkg_json, "r") as f:
        data = json.load(f)
    
    if "scripts" in data and "copy-python" in data["scripts"]:
        # Update copy-python to remove __pycache__
        script = data["scripts"]["copy-python"]
        if "rm -rf" not in script:
            data["scripts"]["copy-python"] = "mkdir -p dist/python && cp -r ../../fde_lab ../../demo ../../pyproject.toml dist/python/ && find dist/python -name '__pycache__' -type d -exec rm -rf {} +"
            with open(pkg_json, "w") as f:
                json.dump(data, f, indent=2)

print("Updated copy-python scripts")
