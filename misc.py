import os
import base64
import traceback
from configparser import ConfigParser
from dataclasses import dataclass
from queue import Queue
from zipfile import ZipFile

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId)


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
    file_name: str = ''


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
            status = status + 'Error: Test Failed: ' + data.task_name + '\n' + \
                str(data.exception[0]) + '\n' + str(data.exception[1]
                                                    ) + '\n' + traceback.format_tb(data.exception[2])[0]
            running = False
        elif data.message_type == 0:
            status = status + 'Test from unit: ' + TESTER + \
                ' has completed successfully, see results attached'
            running = False
        print(data.task_name + ': ' + data.message)
        queue.task_done()
    print('sending email')
    zip_file = '{}.zip'.format(data.file_name)
    with ZipFile(zip_file, 'w') as zip:
        zip.write('{}.jpg'.format(data.file_name))
        zip.write('{}_hist.png'.format(data.file_name))
        zip.write('{}_hist.json'.format(data.file_name))

    message = Mail(
        from_email=TESTER+'@example.com',
        to_emails=EMAIL,
        subject='Test Results for Tester: ' + TESTER + ' at time: x',
        html_content='<p>' + status + '<p>')
    with open(zip_file, 'rb') as f:
        data = f.read()
        f.close()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('application/zip')
    attachment.file_name = FileName(data.file_name)
    attachment.disposition = Disposition('attachment')
    attachment.content_id = ContentId('Test Results')
    message.attachment = attachment
    try:
        sg = SendGridAPIClient(API)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(type(e)) + ' ' + str(e))
    # code for sending email
    print('finished sending email')
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
    config['INFO'] = {'Completed': '0'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    exit()


# def set_wake_time(wake_time):
#    """
#    set cron schedule? probably easier to do manually since sudo is required
#    """
#    print('setting next wake time')
#    exit()
