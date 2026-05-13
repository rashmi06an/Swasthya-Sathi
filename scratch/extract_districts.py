import json
import sys

content_path = '/Users/rashmianand/.gemini/antigravity/brain/8f376703-0779-47f2-81a7-5e4063a4cbea/.system_generated/steps/144/content.md'
output_path = 'data/indian_districts.json'

try:
    with open(content_path, 'r') as f:
        content = f.read()
    
    if '---' in content:
        json_str = content.split('---', 1)[1].strip()
    else:
        json_str = content.strip()
    
    data = json.loads(json_str)
    districts = []
    for state_data in data['states']:
        districts.extend(state_data['districts'])
    
    districts = sorted(list(set(districts)))
    
    with open(output_path, 'w') as f:
        json.dump(districts, f, indent=2)
    
    print(f"Successfully extracted {len(districts)} districts to {output_path}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
