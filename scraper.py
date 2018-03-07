import requests
from lxml import html

'''

session = requests.Session()
session.auth = ('user', 'password')
calendar_url = 'http://studia.elka.pw.edu.pl/cal/'

result = session.get(calendar_url)
calendar_tree = html.fromstring(result.content)
semester = calendar_tree.xpath("//*[contains(text(),'Semestr')]/text()")
temp = semester[0].split(' ')
semester_number = temp[1]

main_page_url = 'https://studia.elka.pw.edu.pl/en/' + semester_number + '/'
result = session.get(main_page_url)
main_page_tree = html.fromstring(result.content)
individual_page = main_page_tree.xpath("//tr//th[@class='nagl']/text()")

length = len(individual_page) - 1

my_subjects = []

for x in range (35,length,2):
    subject_code = individual_page[x]
    subject_name = individual_page[x+1][:-1]
    subject_data = (subject_code, subject_name)
    my_subjects.append(subject_data)

print("Courses you attend: ")

for x in range(0, len(my_subjects)):
    print(str(x+1) + '.', end = ' ')
    print("[%s]" % (my_subjects[x][0]), end = ' ')
    print(my_subjects[x][1])
    
'''


def read_session_data():
    with open('data.conf') as file:
        content = file.read().splitlines()
    details = {
        'username': content[0],
        'password': content[1],
        'subject':  content[2],
        'cell':     content[3]
    }
    return details


def get_individual_page_url(session):
    calendar_url = 'http://studia.elka.pw.edu.pl/cal/'
    result = session.get(calendar_url)
    tree = html.fromstring(result.content)
    semester = tree.xpath("//*[contains(text(),'Semestr')]/text()")
    temp = semester[0].split(' ')
    semester_number = temp[1]
    url = 'https://studia.elka.pw.edu.pl/en/' + semester_number + '/'
    return url


def validate_subject_entry(session, subject, url):
    result = session.get(url)
    tree = html.fromstring(result.content)
    individual_page = tree.xpath("//tr//th[@class='nagl']/text()")
    subjects = extract_subjects(individual_page)
    for s in subjects:
        if subject == s:
            return True
    return False


def extract_subjects(page):
    subjects = []
    for x in range(35, len(page) - 1, 2):
        subject_code = page[x]
        subjects.append(subject_code)
    return subjects


def main():
    session_details = read_session_data()
    session = requests.Session()
    session.auth = (session_details['username'], session_details['password'])
    main_page_url = get_individual_page_url(session)
    if not validate_subject_entry(session, session_details['subject'], main_page_url):
        return


if __name__ == "__main__":
    main()
