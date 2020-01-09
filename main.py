# get system config from config.ini
# get system time
# when system time matches test time run test
# get results from test and send email

from configparser import ConfigParser
from pathlib import Path


def main():
    config = ConfigParser()
    if Path('config.ini').is_file():
        print("Found config file")
        config.read('config.ini')
        try:
            SENDGRID_API = config['KEYS']['SendGrid']
            TESTER_ID = config['SETTINGS']['TesterID']
            EMAIL_ADDRESS = config['SETTINGS']['SendEmailTo']
            TEST_INTERVAL = config['SETTINGS']['TestInterval']
            FIRST_TEST = config['SETTINGS']['FirstTestStartTime']
        except KeyError as e:
            print('Invalid Config File, Please Reconfig')
            write_config_file()
            exit()
            print('This should not run')
    else:
        print("No config file found... Creating new config file")
        write_config_file()
        exit()
        

def write_config_file():
    config = ConfigParser()
    config['KEYS'] = {'SendGrid': 'PASTE_SENDGRID_API_KEY_HERE'}
    config['SETTINGS'] = {'TesterID': 'ENTER_ID_FOR_THIS_DEVICE_HERE',
                            'SendEmailTo': 'ENTER_EMAIL_ADDRESS_RESULTS_SHOULD_BE_SENT_TO',
                            'TestInterval': 'ENTER_TIME_BETWEEN_TESTS_IN_MINUTES', 
                            'FirstTestStartTime': 'ENTER_TIME_AND_DATE_OF_FIRST_TEST (2020-01-31:15:40)'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

main()
