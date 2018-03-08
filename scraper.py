import requests
import string
import time
from lxml import html


# TODO: SEND AND EMAIL ON UPDATE


def read_session_data():
    with open('data.conf', 'r') as file:
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
    print(semester)
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


def get_subject_page_url(subject, url):
    return url + subject + '/info'


def get_row_to_listen(session, url, cell):
    result = session.get(url)
    tree = html.fromstring(result.content)
    row = tree.xpath("//table[2]//tr[td//text()[contains(., '%s')]][1]//text()" % cell)
    return row


def cut_spaces_and_nonprintables(row, cell):
    for index, item in enumerate(row):
        if item == cell:
            for i in range(2,9,2):
                row[index + i] = ''.join([x for x in row[index + i] if x in string.printable])
                row[index + i] = row[index + i][:-4]
    print(row)

def has_been_updated(row, cell):
    for index, item in enumerate(row):
        if item == cell:
            for i in range(4, 9, 2):
                if row[index + i] != '':
                    return True
    return False


def main():
    session_details = read_session_data()
    session = requests.Session()
    session.auth = (session_details['username'], session_details['password'])
    main_page_url = get_individual_page_url(session)
    if not validate_subject_entry(session, session_details['subject'], main_page_url):
        return
    while True:
        subject_page_url = get_subject_page_url(session_details['subject'], main_page_url)
        #subject_page_url = 'https://studia.elka.pw.edu.pl/en/17Z/ECIRS.A/info/'
        print(subject_page_url)
        row_to_listen = get_row_to_listen(session, subject_page_url, session_details['cell'])
        print(row_to_listen)
        cut_spaces_and_nonprintables(row_to_listen, session_details['cell'])
        if has_been_updated(row_to_listen, session_details['cell']):
            break
        else:
            time.sleep(60)
            continue
    print("Cell '%s' in ERES system has been updated!" % session_details['cell'])



if __name__ == "__main__":
    main()
