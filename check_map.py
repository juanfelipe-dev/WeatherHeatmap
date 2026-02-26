import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','heatmap_project.settings')
import django
django.setup()
from weather.views import US_CITIES, weather_map
from django.test import RequestFactory

print('US_CITIES length:', len(US_CITIES))
req = RequestFactory().get('/')
resp = weather_map(req)
content = resp.content.decode('utf-8')
import re, json
m=re.search(r'id="geojsonData">(.*?)</script>', content, re.S)
if m:
    data=json.loads(m.group(1))
    print('features returned:', len(data.get('features', [])))
else:
    print('no geojson data found')
