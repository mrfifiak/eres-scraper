import requests
from lxml import html

session = requests.Session()
session.auth = ('user', 'password')
calendar_url = 'http://studia.elka.pw.edu.pl/cal/'

result = session.get(calendar_url)
calendar_tree = html.fromstring(result.content)
semester = calendar_tree.xpath("//*[contains(text(),'Semestr')]/text()") #find target element
temp = semester[0].split(' ')
semester_number = temp[1]

main_page_url = 'https://studia.elka.pw.edu.pl/en/' + semester_number + '/'
result = session.get(main_page_url)
main_page_tree = html.fromstring(result.content)
