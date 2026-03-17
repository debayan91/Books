import requests
import os

url = "http://127.0.0.1:5000"

# 1. Upload test1.pdf
with open('test1.pdf', 'rb') as f:
    res = requests.post(f"{url}/upload", files={'file': f})
    assert res.status_code == 200
    file1_id = res.json()['id']

# 2. Upload test2.pdf
with open('test2.pdf', 'rb') as f:
    res = requests.post(f"{url}/upload", files={'file': f})
    assert res.status_code == 200
    file2_id = res.json()['id']

# 3. Test /info
res = requests.post(f"{url}/info", json={'file': file1_id})
assert res.status_code == 200
assert res.json()['pages'] == 10

# 4. Test /extract
res = requests.post(f"{url}/extract", json={'file': file1_id, 'ranges': '1-3'})
assert res.status_code == 200
with open('out_extract.pdf', 'wb') as f:
    f.write(res.content)
print("Extract OK")

# 5. Test /merge (original)
res = requests.post(f"{url}/merge", json={'files': [file1_id, file2_id]})
assert res.status_code == 200
with open('out_merge.pdf', 'wb') as f:
    f.write(res.content)
print("Merge OK")

# 6. Test /extract_merge
payload = {
    'files': [
        {'id': file1_id, 'ranges': '1'},
        {'id': file2_id, 'ranges': '10'}
    ]
}
res = requests.post(f"{url}/extract_merge", json=payload)
assert res.status_code == 200
with open('out_em.pdf', 'wb') as f:
    f.write(res.content)
print("Extract+Merge OK")
