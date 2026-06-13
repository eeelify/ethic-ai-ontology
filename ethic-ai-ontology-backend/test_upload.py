import requests
import docx

# Create a sample docx
doc = docx.Document()
doc.add_paragraph("This is a biometric system that uses personal data for hiring.")
doc.save("test.docx")

files = {'file': ('test.docx', open('test.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
data = {'text': ''}

response = requests.post("http://127.0.0.1:8000/analyze-text", data=data, files=files)
print(response.status_code)
print(response.json())
