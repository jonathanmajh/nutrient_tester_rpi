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
from misc import email_thread, write_new_config_file, set_wake_time


def main():
    DATETIME_FORMAT = '%Y-%m-%d:%H:%M'
    config = ConfigParser()
    if Path('config.ini').is_file():
        print("Found config file")
        config.read('config.ini')
        try:
            SENDGRID_API = config['KEYS']['SendGrid']
            TESTER_ID = config['SETTINGS']['TesterID']
            EMAIL_ADDRESS = config['SETTINGS']['SendEmailTo']
            TEST_INTERVAL = config.getint('SETTINGS', 'TestInterval')
            FIRST_TEST = datetime.strptime(
                config['SETTINGS']['FirstTestStartTime'], DATETIME_FORMAT)
            LAST_TEST = config['INFO']['LastTest']
        except (KeyError, ValueError) as e:
            print('Invalid Config File, Please Reconfig config file: ' + str(e))
            write_new_config_file()
        else:
            if not LAST_TEST == 'N/A':  # if value is n/a then the machine has just been powered on and should run its first test
                try:
                    last_test = datetime.strptime(LAST_TEST, DATETIME_FORMAT)
                except ValueError:
                    pass  # if the date cant be read lets run a test to overwrite the date
                    # goes back to main loop to run tests
                else:  # check to make sure the correct amount of time has passed
                    print('loaded last test time')
                    time_for_this_test = last_test + \
                        timedelta(minutes=TEST_INTERVAL)
                    if datetime.now() < time_for_this_test:  # have not reached the correct time yet
                        set_wake_time(time_for_this_test)
                        # set wake 
                        # consider making wake time a bit early, so waking a bit early would not cause a shutdown
                    else:
                        if datetime.now() < FIRST_TEST:
                            set_wake_time(FIRST_TEST)
                            # set wake time
                        # run test by having it go to the default
            else:
                time_for_this_test = FIRST_TEST
            # default behavior is to RUN tests
            queue = Queue()
            test_thread = Thread(target=test_main, args=(queue, ))
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
            config['INFO']['LastTest'] = datetime.now().strftime(
                DATETIME_FORMAT)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            time_for_next_test = time_for_this_test + \
                timedelta(minutes=TEST_INTERVAL)
            set_wake_time(time_for_next_test)
    else:
        print("No config file found... Creating new config file")
        write_new_config_file()


main()
