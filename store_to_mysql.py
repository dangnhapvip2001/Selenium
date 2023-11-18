import requests
from bs4 import BeautifulSoup

url = 'https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops'
soup = BeautifulSoup(response.content, 'html.parser')
name = [name.text for name in soup.find_all('a', class_='title')] # Lay ten san pham
price = [price.text for price in soup.find_all(
    'h4', class_='pull-right price')] # Lay gia san pham
description = [desc.text for desc in soup.find_all(
    'p', class_='description')] # Lay mo ta san pham
rating = []
for rate in soup.find_all('div', class_='ratings'): # Lay danh gia san pham
    flag = 0
for r in rate.find_all('span'):
    flag += 1
rating.append(flag)

def Store_to_mysql():
    connection = mysql.connector.connect(host='127.0.0.1', user='root', password='sieunhan1234')
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE data_db")
    print("Connection to MySQL Established!")
    insert_data()