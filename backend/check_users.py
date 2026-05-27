import json

with open('mock_database.json', 'r') as f:
    data = json.load(f)

users = data.get('users', {})
print(f'Total users: {len(users)}')
for k, v in list(users.items())[:5]:
    email = v.get('email', 'N/A')
    has_hash = 'password_hash' in v
    ph = str(v.get('password_hash', ''))[:50]
    print(f'Email: {email}')
    print(f'Has password_hash: {has_hash}')
    print(f'Hash preview: {ph}')
    print()
