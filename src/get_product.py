import requests
import json
import re
from bs4 import BeautifulSoup

def clean_description(description):
    if not description:
        return ""

    soup = BeautifulSoup(description, "html.parser")

    # Thêm ký tự xuống dòng vào cuối các thẻ khối
    for tag in soup.find_all(['p', 'div', 'li', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        tag.append('\n')

    text = soup.get_text()

    text = text.replace("\xa0", " ")

    # Thay thế các ký tự xuống dòng liên tiếp thành một lần xuống dòng
    text = re.sub(r'\n\s*\n', '\n', text)

    return text

def get_product_detail(productid, agent):
    base_url = "https://api.tiki.vn/product-detail/api/v1/products/{}"
    url = base_url.format(productid)

    headers = {'User-Agent': agent.random}
    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            print(f"Error retrieving data from server from: {url}")
            return None, productid, None

        result = json.loads(res.text)

        description = clean_description(result['description'])

        product_data = {
            'id': result['id'],
            'name': result['name'],
            'url_key': result['url_key'],
            'price': result['price'],
            'description': description,
            'images': result['images']
        }
        return product_data, None, None
    except Exception as e:
        print(f"An error has occurred: {e}")
        return None, None, productid
