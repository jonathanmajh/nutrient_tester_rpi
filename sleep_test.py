from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import subprocess

API = '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'
EMAIL = 'jonathanmajh@gmail.com'
TIME = datetime.now()

def main():
    message = Mail(
        from_email='tester@example.com',
        to_emails=EMAIL,
        subject='Test Results for Tester at time: ' + str(TIME),
        html_content='<p>hi<p>')
    try:
        sg = SendGridAPIClient(API)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(type(e)) + ' ' + str(e))
    # code for sending email
    
main()

# scheduling
# https://www.raspberrypi.org/documentation/linux/usage/cron.md
# */5 * * * * python3 /home/pi/sleep-test.py >> /home/pi/logs/tests.log 2>&1