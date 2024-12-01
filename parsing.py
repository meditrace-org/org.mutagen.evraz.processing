from pypdf import PdfReader
import requests
from os import remove
import uuid 


def get_text_from_pdf(url):

    response = requests.get(url)
    path = f'ins_{uuid.uuid4()}.pdf'

    if response.status_code == 200:
        with open(path, 'wb') as file:
            file.write(response.content)
    else:
        print('Failed to download file')

    reader = PdfReader(path)
    num = len(reader.pages)
    total = ""
    for i in range(num):
        page = reader.pages[i]
        text = page.extract_text()
        total += text + "\n"


    remove(path)
    return total
