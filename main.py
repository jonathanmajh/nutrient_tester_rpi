# get system config from config.ini
# get system time
# when system time matches test time run test
# get results from test and send email

from configparser import ConfigParser
from pathlib import Path
from datetime import datetime, timedelta


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
            FIRST_TEST = config['SETTINGS']['FirstTestStartTime']
            LAST_TEST = config['INFO']['LastTest']
        except (KeyError, ValueError) as e:
            print('Invalid Config File, Please Reconfig config file: ' + str(e))
            write_new_config_file()
        else:
            if not LAST_TEST == 'N/A': # if value is n/a then the machine has just been powered on and should run its first test
                try:
                    last_test = datetime.strptime(LAST_TEST, DATETIME_FORMAT)
                except ValueError:
                    pass  # if the date cant be read lets run a test to overwrite the date
                    # goes back to main loop to run tests
                else:  # check to make sure the correct amount of time has passed
                    time_for_next_test = last_test + \
                        timedelta(minutes=TEST_INTERVAL)
                    if datetime.now() < time_for_next_test:  # have not reached the correct time yet
                        set_wake_time(time_for_next_test)
                        # set wake time
                    else:
                        if datetime.now() < time_for_first_test:
                            set_wake_time(time_for_first_test)
                            # set wake time
                        # run test by having it go to the default
                        pass

            # default behaviour is to RUN tests
            pass
            # update config file with new run time
            config['INFO']['LastTest'] = datetime.now().strftime(
                DATETIME_FORMAT)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            
    else:
        print("No config file found... Creating new config file")
        write_new_config_file()


def write_new_config_file():
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
    """
    exit()

main()
