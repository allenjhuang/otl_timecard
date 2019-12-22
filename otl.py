import constants
import selenium_extras.expected_conditions_additions as AdditionalEC
from selenium_extras.wrapper import Browser
from utils import log_wrap

import csv
import logging
import os
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sys
import time
import toml


class OracleTimeAndLabor(Browser):
    """
    Parameters
    ----------
        browser : str
            Valid options are: "chrome", "edge", "firefox", "ie"
        driver_path : str, optional
            File path to webdriver. Will look in PATH if not set.
        driver_wait_time : int, optional
            Amount of time in seconds to wait when locating elements before
            timing out in seconds.
        username : str, optional
            Oracle SSO username automatically filled in if provided
        password : str, optional
            Oracle SSO password automatically filled in if provided

    Attributes
    ----------
        driver : selenium.webdriver object
            The webdriver object will differ depending on the browser used.
        driver_default_wait : selenium.webdriver.support.ui.WebDriverWait
    """

    def __init__(
        self,
        browser,
        driver_path=None,
        default_wait_time=30,
        username=None,
        password=None
    ):
        super().__init__(browser, driver_path, default_wait_time)
        self._default_wait_time = default_wait_time
        self._username = username
        self._password = password

    @log_wrap(
        logging_func=logging.info,
        before_msg="Opening the Oracle E-Business Suite website"
    )
    def open_oracle_ebusiness_suite(self):
        ebusiness_url = constants.urls['oracle']['ebusiness']
        sso_url = constants.urls['oracle']['single_sign_on']
        self.driver.get(ebusiness_url)
        expected_urls = (
            ebusiness_url,
            sso_url
        )
        self.driver_default_wait.until(AdditionalEC.url_is_one_of(
            expected_urls
        ))
        if self.driver.current_url == ebusiness_url:
            pass  # Goal of this function reached.
        elif self.driver.current_url == sso_url:
            self._login_oracle_sso(self._username, self._password)
            ebusiness_no_query_parameters_url =  \
                constants.urls['oracle']['ebusiness_no_query_parameters']
            sso_hiccup_url =  \
                constants.urls['oracle']['single_sign_on_hiccup']
            expected_urls = (
                ebusiness_url,
                ebusiness_no_query_parameters_url,
                sso_url,
                sso_hiccup_url
            )
            self.driver_default_wait.until(AdditionalEC.any_of(
                AdditionalEC.url_is_one_of(expected_urls),
                EC.url_contains(ebusiness_no_query_parameters_url)
            ))
            if (
                self.driver.current_url == ebusiness_url
                or self.driver.current_url == ebusiness_no_query_parameters_url
                or ebusiness_no_query_parameters_url in self.driver.current_url
            ):
                pass  # Goal of this function reached.
            else:
                # Retry.
                self.open_oracle_ebusiness_suite()

    @log_wrap(
        logging_func=logging.info,
        before_msg="Logging into Oracle Single Sign On"
    )
    def _login_oracle_sso(self, username=None, password=None):
        if username is not None:
            username_input = self.get_element(locator=(By.ID, "sso_username"))
            username_input.send_keys(username)
        if password is not None:
            password_input = self.get_element(locator=(By.ID, "ssopassword"))
            password_input.send_keys(password + Keys.RETURN)
        if username is None or password is None:
            logging.info(
                "Please type in the login details and continue within "
                f"{self._default_wait_time} seconds."
            )
        self.driver_default_wait.until(EC.url_changes(
            constants.urls['oracle']['single_sign_on']
        ))

    @log_wrap(
        logging_func=logging.info,
        before_msg="Navigating to recent timecards"
    )
    def navigate_to_recent_timecards(self):
        overtime_eligible_otl_link = self.get_element(
            locator=(
                By.LINK_TEXT,
                "US OTL - Emps Eligible for Overtime (Project Accounting)"
            )
        )
        overtime_eligible_otl_link.click()
        recent_timecards_link = self.get_element(
            locator=(
                By.LINK_TEXT, "Recent Timecards"
            )
        )
        recent_timecards_link.click()
        self.driver_default_wait.until(AdditionalEC.any_of(
            EC.url_contains(constants.urls['oracle']['timecards_partial']),
            EC.url_contains(constants.urls['oracle']['timecards_alt_partial'])
        ))

    @log_wrap(
        logging_func=logging.info,
        before_msg="Creating a new timecard"
    )
    def create_new_timecard(self):
        create_timecard_button = self.get_element(
            locator=(By.ID, "Hxccreatetcbutton")
        )
        create_timecard_button.click()
        self.driver_default_wait.until(AdditionalEC.any_of(
            EC.url_contains(constants.urls['oracle']['timecards_partial']),
            EC.url_contains(constants.urls['oracle']['timecards_alt_partial'])
        ))

    @log_wrap(
        logging_func=logging.info,
        before_msg="Begin filling out timecard"
    )
    def fill_in_timecard_details(timecard_file):
        # Parse the .csv file.
        csv_dictreader = csv.DictReader(timecard_file)
        # This is the timecard site's table tbody XPath.
        html_table_tbody_xpath = "//span[@id='Hxctimecard']/table[2]//table[2]/tbody/tr[5]/td/table/tbody/tr[5]/td[2]/table/tbody/"
        while (True):
            self._fill_details(csv=csv, html_rows_xpath=html_rows_xpath, csv_start=csv_start, csv_end=csv_end)
            add_html_row(html_rows_xpath=html_rows_xpath, csv_end=csv_end, times=NUMBER_OF_ROWS_BEFORE_ADD)  # Click "Add Another Row" a number of times to match the .csv file rows.
            csv_start += NUMBER_OF_ROWS_BEFORE_ADD
            csv_end += NUMBER_OF_ROWS_BEFORE_ADD
            print(current_time() + " csv_start = " + str(csv_start))
            print(current_time() + " csv_end = " + str(csv_end))
            if (csv_end >= len_of_csv):
                fill_details(csv=csv, html_rows_xpath=html_rows_xpath, csv_start=csv_start, csv_end=len_of_csv)  # Finish off the timecard details.
                print(current_time() + " Finished filling out timecard details.")
                break

    @log_wrap(
        logging_func=logging.info,
        before_msg="Filling out row"
    )
    def _fill_row(
        self, csv_dictreader, html_table_tbody_xpath, row
    ):
        list_of_inputs = _get_list_of_inputs_for_current_row(self, html_table_tbody_xpath, row)
        csv_col = -1  # Need a counter here since the total csv columns and total html inputs don't match - we are ignoring the html input for hours.
        # Loop through columns.
        for html_col in range(len(list_of_inputs)):
            # Set the cell_data to send to the HTML input.
            if (html_col < constants.COLS_BEFORE_TIME):
                csv_col += 1
                cell_data = csv[csv.columns[csv_col]][row]  # The html and csv cols are still matching here.
            elif (html_col % 3 in [0, 2]):  # We want to ignore the html input for hours.
                csv_col += 1
                preparsed_cell_data = csv[csv.columns[csv_col]][row]  # Will be used multiple times soon.
                cell_data = None  # Initialize to None.
                for time_format in ["%I:%M:%S %p", "%H:%M", "%I:%M %p", "%X"]:  # Check for these time formats.
                    try:
                        cell_data = datetime.datetime.strptime(preparsed_cell_data, time_format).strftime("%H:%M")
                        break
                    except Exception:
                        pass
                if (cell_data is None):  # cell_data will remain at None if the preparsed_cell_data doesn't match one of the expected time formats.
                    print(current_time() + " Warning: Skipping row " + str(row) + " csv_col " + str(csv_col) + ", because the cell was empty in the csv or the date format does not match one of the following formats: [\"%I:%M:%S %p\", \"%H:%M\", \"%I:%M %p\", \"%X\"].")
                    continue
            else:
                continue

            # Fill input with cell_data.
            if not hasattr(cell_data, '__len__'):
                print(current_time() + " Warning: Skipping row " + str(row) + " csv_col " + str(csv_col) + ", because data is not present.")
                continue
            # Debug/status messages
            print(current_time() + " row = " + str(row))
            print(current_time() + " col = " + str(csv_col))
            print(current_time() + " csv.columns[csv_col] = " + csv.columns[csv_col])
            print(current_time() + " cell_data = " + str(cell_data))
            # Makes sure the keys send. Sometimes doesn't send due to the javascript on the page.
            while (True):  # Emulating a do-while loop in Python.
                list_of_inputs[html_col].clear()
                list_of_inputs[html_col].send_keys(cell_data)
                if (html_col == 0):  # Implemented mandatory sleep for the Project field or else there might be pop-ups when filling in the Task field.
                    if (platform != 'Linux'):
                        list_of_inputs[html_col+1].click()  # Click away from the current input so that the javascript on the page runs. FIXME: StaleElementReferenceException sometimes encountered around here on Linux. Skipping this on Linux for now.
                    time.sleep(5)  # TODO: Maybe set it to a non-arbitrary number.
                if (list_of_inputs[html_col].get_attribute("value") != cell_data):
                    time.sleep(1)
                else:  # If the input value matches the cell_data, then break out of the while loop.
                    break

    @log_wrap(
        logging_func=logging.debug,
        before_msg="Getting list of inputs for current row"
    )
    def _get_list_of_inputs_for_current_row(self, html_table_tbody_xpath, row):
        return self.get_elements(
            locator=(
                By.XPATH,
                # XPath is 1-indexed and the first row is the header, so we
                # start at the 2nd tr.
                html_table_tbody_xpath + "tr[" + str(row + 2) + "]//input"
            )
        )

    @log_wrap(
        logging_func=logging.info,
        before_msg="Adding HTML row"
    )
    def _add_html_row(self, html_rows_xpath, csv_end, times):  # TODO: Looks like the site adds 6 rows with one click now. Should probably remove the multiple button clicks, though it doesn't hurt.
        print(current_time() + " add_html_row(html_rows_xpath, csv_end, times)")
        # Add html rows n amount of times.
        for n in range(times):  # FIXME: Looks like the Linux version of the webdriver struggles to find the "Add Another Row" button sometimes here.
            element = wait.until(EC.visibility_of_element_located((By.XPATH, html_rows_xpath + "//button[contains(., 'Add Another Row')]")))
            element.click()
            wait.until(EC.visibility_of_element_located((By.XPATH, html_rows_xpath + "[" + str(csv_end + n + 2) + "]")))  # Wait until a new HTML row is added. FIXME: Doesn't seem to be working as expected. The print statement on the next line appears to execute before the new HTML row is found. Maybe check and compare the length of the list of html rows before and after instead.
            print(current_time() + " HTML row added.")
        print(current_time() + " Finished adding " + str(times) + " HTML rows.")
