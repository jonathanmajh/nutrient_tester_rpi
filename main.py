# get system config from config.ini
# get system time
# when system time matches test time run test
# get results from test and send email

from configparser import ConfigParser
from pathlib import Path
from datetime import datetime, timedelta
from threading import Thread
from queue import Queue
from test import test_main
from misc import email_thread, write_new_config_file


def main():
    DATETIME_FORMAT = '%Y-%m-%d:%H:%M'
    config = ConfigParser()
    test_time = datetime.now()
    if Path('config.ini').is_file():
        print("Found config file")
        config.read('config.ini')
        try:
            SENDGRID_API = config['KEYS']['SendGrid']
            TESTER_ID = config['SETTINGS']['TesterID']
            EMAIL_ADDRESS = config['SETTINGS']['SendEmailTo']
            FIRST_TEST = datetime.strptime(
                config['SETTINGS']['FirstTestStartTime'], DATETIME_FORMAT)
            Completed = config['INFO']['Completed']
        except (KeyError, ValueError) as e:
            print('Invalid Config File, Please Reconfig config file: ' + str(e))
            write_new_config_file()
        else:
            if test_time < FIRST_TEST:
                quit()
            # default behavior is to RUN tests
            queue = Queue()
            test_thread = Thread(target=test_main, args=(queue, Completed, test_time, DATETIME_FORMAT))
            monitor = Thread(target=email_thread, args=(
                queue, SENDGRID_API, TESTER_ID, EMAIL_ADDRESS))
            print('starting queue')
            test_thread.start()
            monitor.start()
            print('waiting for queue to finish')
            test_thread.join()
            monitor.join()
            print('queue finished')
            # update config file with new run time
            Completed = Completed + 1
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
    else:
        print("No config file found... Creating new config file")
        write_new_config_file()


main()
