from observer import Subscriber
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class Mailer(Subscriber):
    def __init__(self, name, from_address, to_address, password):
        super().__init__(name)
        self.password = password
        self.from_address = from_address
        self.to_address = to_address
        self.body = None
        self.subject = None

    def update(self, payload):
        print("Payload obtained, sending an email.")
        self.prepare_msg_body(payload)

    def prepare_msg_body(self, payload):
        self.body = "%s cell from %s subject updated in ERES.\n\n"  \
                    "Your score: %s\n" \
                    "Minimal score: %s\n" \
                    "Average score: %s\n" \
                    "Maximal score: %s\n" \
                    "Number of marks: %s\n\n" \
                    "This email was sent automatically by ERES Scraper. Please do not respond to it." \
                    % (payload['cell'],
                       payload['subject'],
                       payload['personal_score'],
                       payload['min_score'],
                       payload['avg_score'],
                       payload['max_score'],
                       payload['no_of_marks']
                       )

        self.send(payload)

    def send(self, payload):
       msg = MIMEMultipart()
       msg['From'] = self.from_address
       msg['To'] = self.to_address
       subject = "[ERES SCRAPER][%s] Data update notified on %s" % (payload['subject'], payload['cell'])
       msg["Subject"] = subject

       body = self.body
       msg.attach(MIMEText(body, 'plain'))

       server = smtplib.SMTP('smtp.gmail.com', 587)
       server.starttls()
       server.login(self.from_address, self.password)
       text = msg.as_bytes()
       server.sendmail(self.from_address, self.to_address, text)
       server.quit()


