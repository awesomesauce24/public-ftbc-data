import requests

url = 'https://ftbc.fandom.com/api.php'
params = {
    'action': 'query',
    'format': 'json',
    'titles': 'Tropical Islands',
    'prop': 'extracts',
    'explaintext': True,
}

response = requests.get(url, params=params, timeout=10)
print(f'Status: {response.status_code}')
print(f'Response length: {len(response.text)}')
print('First 1000 chars:')
print(response.text[:1000])
