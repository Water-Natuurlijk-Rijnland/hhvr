import json
import random

geojson_path = '/Users/marc/Projecten/peilbeheer/peilbesluiten/rijnland_kaartlagen/Gemaal/Gemaal_layer0.geojson'

try:
    with open(geojson_path, 'r') as f:
        data = json.load(f)
    
    features = data.get('features', [])
    codes = [f['attributes']['CODE'] for f in features if 'attributes' in f and 'CODE' in f['attributes']]
    
    if codes:
        random_codes = random.sample(codes, 5)
        for code in random_codes:
            print(code)
    else:
        print("No codes found.")

except Exception as e:
    print(f"Error: {e}")
