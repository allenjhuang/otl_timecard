import constants
import selenium_extras.expected_conditions_additions as AdditionalEC
from selenium_extras.wrapper import Browser
from utils import log_wrap

import csv
from datetime import datetime
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time


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
        sso_username : str, optional
            Oracle SSO username automatically filled in if provided
        sso_password : str, optional
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
        sso_username=None,
        sso_password=None
    ):
        super().__init__(browser, driver_path, default_wait_time)
        self._default_wait_time = default_wait_time
        self._sso_username = sso_username
        self._sso_password = sso_password

    @log_wrap(before_msg="Opening the Oracle E-Business Suite website")
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
            self._login_oracle_sso(self._sso_username, self._sso_password)
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

    @log_wrap(before_msg="Navigating to recent timecards")
    def navigate_to_recent_timecards(self):
        overtime_eligible_otl_link = self.get_element_by_link_text(
            "US OTL - Emps Eligible for Overtime (Project Accounting)"
        )
        overtime_eligible_otl_link.click()
        recent_timecards_link = self.get_element_by_link_text(
            "Recent Timecards"
        )
        recent_timecards_link.click()
        self.driver_default_wait.until(AdditionalEC.any_of(
            EC.url_contains(constants.urls['oracle']['timecards_partial']),
            EC.url_contains(constants.urls['oracle']['timecards_alt_partial'])
        ))

    @log_wrap(before_msg="Creating a new timecard")
    def create_new_timecard(self):
        create_timecard_button = self.get_element_by_id("Hxccreatetcbutton")
        create_timecard_button.click()
        self.driver_default_wait.until(AdditionalEC.any_of(
            EC.url_contains(constants.urls['oracle']['timecards_partial']),
            EC.url_contains(constants.urls['oracle']['timecards_alt_partial'])
        ))

    @log_wrap(
        before_msg="Begin filling out timecard",
        after_msg="Finished filling out timecard"
    )
    def fill_in_timecard_details(self, timecard_path):
        with open(timecard_path) as timecard_file:
            csv_reader = csv.reader(timecard_file)
            # Discard the first row since it only contains the headers.
            next(csv_reader)
            # This is the timecard site's table tbody XPath.
            html_table_tbody_xpath =  \
                constants.timecard['html']['table_tbody_xpath']
            for row_num, row in enumerate(csv_reader):
                current_html_row_inputs_list = self._get_list_of_html_inputs(
                    self._get_html_row_xpath(row_num, html_table_tbody_xpath)
                )
                if len(current_html_row_inputs_list) == 0:
                    self._add_html_row(html_table_tbody_xpath, row_num)
                    current_html_row_inputs_list =   \
                        self._get_list_of_html_inputs(
                            self._get_html_row_xpath(
                                row_num, html_table_tbody_xpath
                            )
                        )
                self._fill_html_row(
                    html_inputs_list=current_html_row_inputs_list,
                    csv_row_data=self._row_data_generator(row)
                )

    @log_wrap(before_msg="Logging into Oracle Single Sign On")
    def _login_oracle_sso(self, username=None, password=None):
        if username is not None:
            username_input = self.get_element_by_id("sso_username")
            username_input.send_keys(username)
        if password is not None:
            password_input = self.get_element_by_id("ssopassword")
            password_input.send_keys(password + Keys.RETURN)
        if username is None or password is None:
            logging.info(
                "Please type in the login details and continue within "
                f"{self._default_wait_time} seconds."
            )
        self.driver_default_wait.until(EC.url_changes(
            constants.urls['oracle']['single_sign_on']
        ))

    def _get_html_row_xpath(
        self, row_num, html_table_tbody_xpath
    ):
        # XPath is 1-indexed and the first row is the header, so we start at
        # the 2nd tr.
        return f"{html_table_tbody_xpath}/tr[{row_num + 2}]"

    def _get_list_of_html_inputs(
        self, current_html_row_xpath
    ):
        return self.get_elements_by_xpath(current_html_row_xpath + "//input")

    def _row_data_generator(self, row):
        row_len = len(row)
        current_col = 0
        while current_col < row_len:
            yield row[current_col]
            current_col += 1

    @log_wrap(before_msg="Filling out HTML row")
    def _fill_html_row(
        self, html_inputs_list, csv_row_data
    ):
        for html_input_num, html_input in enumerate(html_inputs_list):
            # Get the data from the csv.
            cell_data = None
            if (html_input_num < constants.timecard['num_cols_before_time']):
                # The html and csv cols are still matching here.
                cell_data = next(csv_row_data)
            # The total csv columns and total html inputs don't match, so we
            # have to ignore the html input for hours.
            elif self._is_on_hours_html_input(html_input_num) is False:
                data_to_be_checked = next(csv_row_data)
                if data_to_be_checked in (None, ""):
                    continue  # Empty cell, so continue
                else:  # Not an empty cell
                    parsed_data = self._parse_time(data_to_be_checked)
                    if parsed_data is not None:
                        cell_data = self._convert_time_format(parsed_data)
                    else:  # Could not parse data
                        continue
            else:  # self._is_on_hours_html_input(html_input_num) is True
                continue

            # Fill input with cell_data.
            while True:
                # Ensures the keys are sent. Sometimes they dont send due to
                # the javascript running on the page.
                html_input.clear()
                html_input.send_keys(cell_data)
                # Mandatory sleep after inputting data for the Project field,
                # else there may be pop-ups when filling in the Task field.
                if html_input_num == 0:
                    # Trigger javascript by clicking away from current input.
                    html_inputs_list[1].click()
                    time.sleep(
                        constants.timecard['sleep_time']['after_project_field']
                    )
                if html_input.get_attribute("value") != cell_data:
                    time.sleep(1)
                else:  # Input value matches the cell_data
                    break

    def _is_on_hours_html_input(self, html_input_num):
        # Every third input is the input for hours.
        return (
            (html_input_num - constants.timecard['num_cols_before_time'])
            % 3 == 2
        )

    def _parse_time(self, data):
        parsed_data = None
        # Accept these formats.
        for time_format in ["%H:%M", "%I:%M:%S %p", "%I:%M %p", "%X"]:
            try:
                parsed_data = datetime.strptime(
                    data, time_format
                )
                break
            except (TypeError, ValueError):
                pass
        return parsed_data

    def _convert_time_format(self, data):
        return data.strftime("%H:%M")

    @log_wrap(before_msg="Adding HTML row")
    def _add_html_row(self, html_table_tbody_xpath, current_row_num):
        while True:
            add_row_button = self.get_element_by_xpath(
                html_table_tbody_xpath
                + "//button[contains(., 'Add Another Row')]"
            )
            add_row_button.click()
            time.sleep(
                constants.timecard['sleep_time']['after_adding_html_row']
            )
            # Wait until a new HTML row is added.
            if len(
                self._get_list_of_html_inputs(self._get_html_row_xpath(
                    current_row_num, html_table_tbody_xpath
                ))
            ) > 0:
                break
