import os
import json
import re

files_to_fix = [
    "fde_lab/pocs/customer_onboarding_engineer/demo_data/acme_health/normal/onboarding.json",
    "output/onboarding-config.json"
]

for f in files_to_fix:
    if os.path.exists(f):
        with open(f, 'r') as file:
            content = file.read()
        
        # Remove trailing comma in slack webhook line
        content = re.sub(r'"webhook_url": "https://example.com/webhook",', r'"webhook_url": "https://example.com/webhook"', content)
        
        with open(f, 'w') as file:
            file.write(content)
        print(f"Fixed {f}")
