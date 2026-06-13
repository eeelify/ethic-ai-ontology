import requests
import docx

doc = docx.Document()
doc.add_paragraph("biometric hiring personal data")
doc.save("test.docx")

files = {'file': ('test.docx', open('test.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}

response = requests.post("http://127.0.0.1:8000/analyze-text", files=files)
print(response.status_code)
print(response.json())
