from dataclasses import dataclass
from queue import Queue
from configparser import ConfigParser
import traceback
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

@dataclass
class QueueMessage:
    """
    0 = Success
    1 = Information
    2 = Warning
    3 = Error
    4 = Uncaught Exception Occurred
    """
    message: str
    message_type: int = 1
    exception: tuple = None


def email_thread(queue: Queue, API: str, TESTER: str, EMAIL: str):
    status = ''
    running = True
    while running:
        data = queue.get()
        if data.message_type == 1:
            status = status + data.message + '\n'
        elif data.message_type == 2:
            status = status + 'Warning: ' + data.message + '\n'
        elif data.message_type == 3:
            status = status + 'Error: ' + data.message + '\n'
        elif data.message_type == 4:
            status = status + 'Error: Test Failed:\n' + str(data.exception[0]) + '\n' + str(data.exception[1]) + '\n' + traceback.format_tb(data.exception[2])[0]
            running = False
        elif data.message_type == 0:
            status = status + 'Test from unit: ' + TESTER + ' has completed successfully, see results attached'
            running = False
        queue.task_done()
    message = Mail(
        from_email=TESTER+'@example.com',
        to_emails=EMAIL,
        subject='Test Results for Tester: '+ TESTER + ' at time: x',
        html_content='<p>' + status + '<p>')
    try:
        sg = SendGridAPIClient(API)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(type(e)) + ' ' + str(e))
    # code for sending email
    print(status)


def write_new_config_file():
    """
    Generates a new config file, Overwrites all previous information

    Exits program when finished
    """
    config = ConfigParser()
    config['KEYS'] = {'SendGrid': 'PASTE_SENDGRID_API_KEY_HERE'}
    config['SETTINGS'] = {'TesterID': 'ENTER_ID_FOR_THIS_DEVICE_HERE',
                          'SendEmailTo': 'ENTER_EMAIL_ADDRESS_RESULTS_SHOULD_BE_SENT_TO',
                          'TestInterval': 'ENTER_TIME_BETWEEN_TESTS_IN_MINUTES',
                          'FirstTestStartTime': 'ENTER_TIME_OF_FIRST_TEST(2020-01-31:15:40)'}
    config['INFO'] = {'LastTest': 'N/A'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    exit()


def set_wake_time(wake_time):
    """
    Asks Sleepy Pi to wake me up when its all over

    Exits program when finished
    """
    print('setting next wake time')
    exit()