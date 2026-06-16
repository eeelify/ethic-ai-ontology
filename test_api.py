import requests

url = "http://127.0.0.1:8000/analyze-text"
data = {
    "text": "Bu sistem kredi başvurularını otomatik olarak değerlendirip insanları profilliyor."
}
try:
    response = requests.post(url, json=data)
    print("Status:", response.status_code)
    print("Text:", response.text)
except Exception as e:
    print("Error:", e)
