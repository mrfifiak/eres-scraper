import requests
from lxml import html

session = requests.Session()
session.auth = ('user', 'password')
url = 'http://studia.elka.pw.edu.pl/en/info'
result = session.get(url)
tree = html.fromstring(result.content)
page = tree.xpath('//table//tr//text()') #find target element
