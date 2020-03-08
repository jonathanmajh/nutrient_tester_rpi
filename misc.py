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
    task_name: str = ''


def email_thread(queue: Queue, API: str, TESTER: str, EMAIL: str):
    status = ''
    running = True
    while running:
        data = queue.get()
        if data.message_type == 1:
            status = status + data.task_name + ': ' + data.message + '\n'
        elif data.message_type == 2:
            status = status + 'Warning: ' + data.task_name + ': ' + data.message + '\n'
        elif data.message_type == 3:
            status = status + 'Error: ' + data.task_name + ': ' + data.message + '\n'
        elif data.message_type == 4:
            status = status + 'Error: Test Failed: ' + data.task_name + '\n' + str(data.exception[0]) + '\n' + str(data.exception[1]) + '\n' + traceback.format_tb(data.exception[2])[0]
            running = False
        elif data.message_type == 0:
            status = status + 'Test from unit: ' + TESTER + ' has completed successfully, see results attached'
            running = False
        print(data.task_name + ': ' + data.message)
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
                          'FirstTestStartTime': 'ENTER_TIME_OF_FIRST_TEST(2020-01-31:15:40)'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    exit()


#def set_wake_time(wake_time):
#    """
#    set cron schedule? probably easier to do manually since sudo is required
#    """
#    print('setting next wake time')
#    exit()