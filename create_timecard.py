from otl import OracleTimeAndLabor

import logging
import sys
import toml


def main():
    # Set up logging.
    logging_handlers = [
        # logging.FileHandler(filename="create_timecard.log"),  # Log to file.
        logging.StreamHandler(sys.stdout)  # Log to standard output (console).
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        handlers=logging_handlers
    )
    logging.info(f"BEGIN {sys.argv[0]}")
    # Load config file.
    logging.info("Loading config file")
    config = toml.load("config.toml")
    # Load secrets file if found.
    is_secrets_found = False
    try:
        secrets = toml.load(config['secrets']['file']['path'])
        is_secrets_found = True
    except FileNotFoundError:
        pass

    logging.info("Creating browser instance")
    browser_choice = config['browser']['choice']
    browser = OracleTimeAndLabor(
        browser=browser_choice,
        driver_path=config['browser']['webdriver'][browser_choice]['path'],
        default_wait_time=config['browser']['webdriver']['default_wait_time'],
        # Will need to manually input login details if not provided.
        sso_username=secrets['username'] if is_secrets_found else None,
        sso_password=secrets['password'] if is_secrets_found else None
    )
    browser.open_oracle_ebusiness_suite()
    browser.navigate_to_recent_timecards()
    browser.create_new_timecard()
    browser.fill_in_timecard_details(
        timecard_path=config['timecard']['file']['path']
    )
    logging.info(f"END {sys.argv[0]}\n\n")


if __name__ == '__main__':
    main()
