import requests
from lxml import html
import getpass
import re
import sys
import time
from observer import Publisher
from mailer import Mailer


class Scraper(Publisher):
    def __init__(self):
        super().__init__()
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

    # part of loop below

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
        row = self.remove_non_alphanumerics(row)
        return row

    def extract_element_content(self, element):
        row = []
        for child in element[0]:
            row.append(child.text)
        return row

    def remove_predecessors(self, row):
        for r in row:
            if r == self.cell_to_track:
                index = row.index(r)
                break
        row = row[index:len(row)-1]
        return row

    def remove_non_alphanumerics(self, row):
        alphanumerical_row = []
        print(row)
        for r in row:
            temp = r.replace(u'\xa0', u'')
            new_cell = temp.replace(u' ', u'')
            alphanumerical_row.append(new_cell)
        print(alphanumerical_row)
        return alphanumerical_row

    def prepare(self):
        self.login()
        self.get_individual_subjects()
        self.get_subject_to_track()

        from_addr = input("Enter email address to send update message FROM [GMAIL SUPPORT ONLY]: ")
        to_addr = input("Enter email address to send update message TO: ")
        password = getpass.getpass("password: ")

        mailer = Mailer("mailer", from_addr, to_addr, password)
        super().register(mailer.name)

    def scrap(self):
        while True:
            self.get_row_containing_cell()
            updated = self.check_update()
            if updated:
                break
            else:
                print("There were on update in ERES system. Next check in 10 seconds.")
                time.sleep(10)
                continue

    def check_update(self):
        for i in range(1, len(self.row_to_track)):
            if self.row_to_track[i] != "":
                return True
        return 


def main():
    scraper = Scraper()
    scraper.prepare()
    scraper.scrap()


if __name__ == "__main__":
    main()
