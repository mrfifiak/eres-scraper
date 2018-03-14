import requests
import time
from lxml import html
import getpass
import re
import copy
import sys


class Scraper:
    def __init__(self):
        self.main_page_url = "https://studia.elka.pw.edu.pl/en/"
        self.individual_page_url = None
        self.session = requests.Session()
        self.marks_page_url = None
        self.response = None
        self.subjects = None
        self.subject_to_track = None
        self.cell_to_track = None
        self.row_to_track = None

    def get_login_credentials(self):
        self.session.auth = (input("username: "), getpass.getpass("password: "))

    def login(self):
        while True:
            self.get_login_credentials()
            self.response = self.session.get(self.main_page_url)
            if self.response.status_code == 401:  # HTTP 401 Client Error: Unauthorized
                print("Wrong username and/or password.")
                continue
            else:
                self.individual_page_url = self.response.url
                break

    def get_individual_subjects(self):
        subjects_tree = html.fromstring(self.response.content)
        subjects = subjects_tree.xpath("//tr[th[@class='nagl'] and th[@class='zaw0']]")
        self.subjects = []
        for s in subjects:
            for child in s:
                if re.match("[A-Z]+[-]*[1-9]*[A-Z]*.[A-B]", str(child.text)):
                    self.subjects.append(child.text)

    def get_subject_to_track(self):
        while True:
            self.subject_to_track = None
            print(self.subjects)
            subject = input("Enter subject code: ")
            for s in self.subjects:
                if s == subject:
                    self.subject_to_track = subject
                    break
            if self.subject_to_track is not None:
                break
            else:
                print("Wrong subject code.")
                continue
        self.get_marks_page_url()

    def get_marks_page_url(self):
        self.marks_page_url = self.individual_page_url + self.subject_to_track + "/info"
        self.get_cell_to_track()

    def get_cell_to_track(self):
        self.cell_to_track = input("Enter cell name to track: ")
        self.get_row_containing_cell()

    def get_row_containing_cell(self):
        self.response = self.session.get(self.marks_page_url)
        marks_tree = html.fromstring(self.response.content)
        marks = marks_tree.xpath("//tr[td[contains(text(), '%s')]]" % self.cell_to_track)
        if not marks:
            print("%s not found in %s page. Terminating."
                  % (self.cell_to_track, self.subject_to_track))
            sys.exit()
        else:
            self.row_to_track = self.prettify_element(marks)

    def prettify_element(self, element):
        row = self.extract_element_content(element)
        row = self.remove_predecessors(row)
        return row

    def extract_element_content(self, element):
        row = []
        print(element)
        sys.stdout.flush()
        for child in element[0]:
            row.append(copy.deepcopy(child.text))
        print(row)
        return row

    def remove_predecessors(self, row):
        for r in row:
            if r == self.cell_to_track:
                index = row.index(r)
                break
        row = row[index:len(row)-1]
        print(row)
        return row






'''
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
'''


def main():
    scraper = Scraper()
    scraper.login()
    scraper.get_individual_subjects()
    scraper.get_subject_to_track()


if __name__ == "__main__":
    main()
