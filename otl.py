from __future__ import annotations

import constants
import selenium_extras.additional_expected_conditions as AdditionalEC
from selenium_extras.additional_exceptions import (
    IncorrectLoginDetails, MaxTriesReached, SubtaskNotFound
)
from selenium_extras.wrapper import Browser
from utils import log_wrap

import csv
from datetime import datetime
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Any, Iterator, List, Optional


class OracleTimeAndLabor(Browser):
    """Creates a new hourly timecard using a csv file as reference.

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
            Webdriver with the driver_wait_time amount as its timeout.
    """

    def __init__(
        self,
        browser: str,
        driver_path: Optional[str] = None,
        default_wait_time: int = 60,
        sso_username: Optional[str] = None,
        sso_password: Optional[str] = None
    ) -> None:
        super().__init__(browser, driver_path, default_wait_time)
        self._default_wait_time: int = default_wait_time
        self._sso_username: Optional[str] = sso_username
        self._sso_password: Optional[str] = sso_password

    @log_wrap(before_msg="Opening the Oracle E-Business Suite website")
    def open_oracle_ebusiness_suite(
        self,
        current_try: int = 1,
        max_tries: int = constants.max_tries['open_oracle_ebusiness_suite']
    ) -> None:
        """Opens the Oracle E-Business Suite website."""
        ebusiness_url: str = constants.urls['oracle']['ebusiness']
        sso_url: str = constants.urls['oracle']['single_sign_on']
        self.driver.get(ebusiness_url)
        expected_urls: List[str] = [
            ebusiness_url,
            sso_url
        ]
        self.driver_default_wait.until(AdditionalEC.url_is_one_of(
            expected_urls
        ))
        if self.driver.current_url == ebusiness_url:
            pass  # Goal of this function reached.
        elif self.driver.current_url == sso_url:
            self._login_oracle_sso(self._sso_username, self._sso_password)
            ebusiness_no_query_parameters_url: str =  \
                constants.urls['oracle']['ebusiness_no_query_parameters']
            sso_hiccup_url: str =  \
                constants.urls['oracle']['single_sign_on_hiccup']
            expected_urls = [
                ebusiness_url,
                ebusiness_no_query_parameters_url,
                sso_url,
                sso_hiccup_url
            ]
            self.driver_default_wait.until(
                AdditionalEC.any_of(
                    AdditionalEC.url_is_one_of(expected_urls),
                    EC.url_contains(ebusiness_no_query_parameters_url)
                )
            )
            if (
                self.driver.current_url == ebusiness_url
                or self.driver.current_url == ebusiness_no_query_parameters_url
                or ebusiness_no_query_parameters_url in self.driver.current_url
            ):
                pass  # Goal of this function reached.
            elif current_try < max_tries:
                # Retry.
                self.open_oracle_ebusiness_suite(current_try+1)
            elif current_try >= max_tries:
                raise MaxTriesReached(
                    "Too many attempts to open the Oracle E-Business Suite "
                    "have been made."
                )

    @log_wrap(before_msg="Navigating to recent timecards")
    def navigate_to_recent_timecards(self) -> None:
        """Navigates to Recent Timecards."""
        overtime_eligible_otl_link: Any = self.get_element_by_link_text(
            "US OTL - Emps Eligible for Overtime (Project Accounting)"
        )
        overtime_eligible_otl_link.click()
        recent_timecards_link: Any = self.get_element_by_link_text(
            "Recent Timecards"
        )
        recent_timecards_link.click()
        self.driver_default_wait.until(AdditionalEC.any_of(
            EC.url_contains(constants.urls['oracle']['timecards_partial']),
            EC.url_contains(constants.urls['oracle']['timecards_alt_partial'])
        ))

    @log_wrap(before_msg="Creating a new timecard")
    def create_new_timecard(self) -> None:
        """Creates a new timecard."""
        create_timecard_button: Any = self.get_element_by_id(
            "Hxccreatetcbutton"
        )
        create_timecard_button.click()
        self.driver_default_wait.until(AdditionalEC.any_of(
            EC.url_contains(constants.urls['oracle']['timecards_partial']),
            EC.url_contains(constants.urls['oracle']['timecards_alt_partial'])
        ))

    @log_wrap(
        before_msg="Begin filling out timecard",
        after_msg="Finished filling out timecard"
    )
    def fill_in_timecard_details(self, timecard_path: str) -> None:
        """Fills out the timecard with details from the csv file."""
        with open(timecard_path) as timecard_file:
            csv_reader: Iterator[List[str]] = csv.reader(timecard_file)
            # Discard the first row since it should only contain the header.
            next(csv_reader)
            # This is the timecard site's table tbody XPath.
            html_table_tbody_xpath: str =  \
                constants.timecard['html']['table_tbody_xpath']
            html_row_num: int = 0
            for csv_row_num, csv_row in enumerate(
                csv_reader
            ):  # type: int, List[str]
                current_html_row_inputs_list: List[Any] =  \
                    self._get_list_of_html_inputs(
                        self._get_html_row_xpath(
                            html_row_num, html_table_tbody_xpath
                        )
                    )
                if self._is_time_entered(csv_row):
                    if len(current_html_row_inputs_list) == 0:
                        self._add_html_row(
                            html_table_tbody_xpath, html_row_num
                        )
                        current_html_row_inputs_list =   \
                            self._get_list_of_html_inputs(
                                self._get_html_row_xpath(
                                    html_row_num, html_table_tbody_xpath
                                )
                            )
                    self._fill_html_row(
                        html_inputs_list=current_html_row_inputs_list,
                        csv_row_data=self._row_data_generator(csv_row)
                    )
                    html_row_num += 1

    @log_wrap(before_msg="Logging into Oracle Single Sign On")
    def _login_oracle_sso(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """Logs into Oracle Single Sign On."""
        if username is not None:
            username_input: Any = self.get_element_by_id("sso_username")
            username_input.send_keys(username)
        if password is not None:
            password_input: Any = self.get_element_by_id("ssopassword")
            password_input.send_keys(password + Keys.RETURN)
        if username is None or password is None:
            logging.info(
                "Please type in the login details and continue within "
                f"{self._default_wait_time} seconds."
            )
        self.driver_default_wait.until(EC.url_changes(
            constants.urls['oracle']['single_sign_on']
        ))
        if (
            self.driver.current_url
            == constants.urls['oracle']['single_sign_on_hiccup']
        ):
            self.driver_default_wait.until(EC.url_changes(
                constants.urls['oracle']['single_sign_on_hiccup']
            ))
            if (
                self.driver.current_url
                == constants.urls['oracle']['single_sign_on']
            ):
                raise IncorrectLoginDetails(
                    "Invalid login. Please check your username and password."
                )

    def _get_html_row_xpath(
        self, html_row_num: int, html_table_tbody_xpath: str
    ) -> str:
        """Gets the timecard website's XPath for the HTML rows"""
        # XPath is 1-indexed and the first row is the header, so we start at
        # the 2nd tr.
        return f"{html_table_tbody_xpath}/tr[{html_row_num + 2}]"

    def _get_list_of_html_inputs(
        self, current_html_row_xpath: str
    ) -> List[Any]:
        """Gets a list of inputs from the provided xpath."""
        return self.get_elements_by_xpath(current_html_row_xpath + "//input")

    def _row_data_generator(self, csv_row: List[str]) -> Iterator[str]:
        """Iterates through the data within a row."""
        row_len: int = len(csv_row)
        current_col: int = 0
        while current_col < row_len:
            yield csv_row[current_col]
            current_col += 1

    def _is_time_entered(self, csv_row: List[str]) -> bool:
        """Checks if there are any time entries within a csv row."""
        row_len: int = len(csv_row)
        is_time_entered: bool = False
        for i in range(constants.timecard['num_cols_before_time'], row_len):
            if csv_row[i] not in (None, ""):
                is_time_entered = True
                break
        return is_time_entered

    @log_wrap(before_msg="Filling out HTML row")
    def _fill_html_row(
        self, html_inputs_list: List[Any], csv_row_data: Iterator[str]
    ) -> None:
        """Fills a row on the timecard website with data from the csv."""
        for html_input_num, html_input in enumerate(
            html_inputs_list
        ):  # type: int, Any
            # Get the data from the csv.
            cell_data: Optional[str] = None
            if (html_input_num < constants.timecard['num_cols_before_time']):
                # The html and csv cols are still matching here.
                cell_data = next(csv_row_data)
            # The total csv columns and total html inputs don't match, so we
            # have to ignore the html input for hours.
            elif self._is_on_hours_html_input(html_input_num) is False:
                data_to_be_checked: str = next(csv_row_data)
                if data_to_be_checked in (None, ""):
                    continue  # Empty cell, so continue
                else:  # Not an empty cell
                    parsed_data: Optional[datetime] = self._parse_time(
                        data_to_be_checked
                    )
                    if parsed_data is not None:
                        cell_data = self._convert_into_time_format(parsed_data)
                    else:  # Could not parse data
                        continue
            else:  # self._is_on_hours_html_input(html_input_num) is True
                continue

            # Fill input with cell_data.
            is_entry_success: bool = False
            for current_wait_time in range(
                0,
                self._default_wait_time,
                constants.timecard['sleep_time']['wait_for_data_entry']
            ):
                # Ensures the keys are sent, even with the website's heavy
                # javascript validation.
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
                if (
                    html_input.get_attribute("value") != cell_data
                ):
                    time.sleep(
                        constants.timecard['sleep_time']['wait_for_data_entry']
                    )
                else:  # Input value matches the cell_data
                    is_entry_success = True
                    break
            if is_entry_success is False:
                raise TimeoutError(
                    "Default wait time exceeded for data entry."
                )

    def _is_on_hours_html_input(self, html_input_num: int) -> bool:
        """Checks if the html_input[html_input_num] is an input for hours."""
        # Every third input is the input for hours.
        return (
            (html_input_num - constants.timecard['num_cols_before_time'])
            % 3 == 2
        )

    def _parse_time(self, data: str) -> Optional[datetime]:
        """Converts string into a datetime object."""
        parsed_data: Optional[datetime] = None
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

    def _convert_into_time_format(self, data: datetime) -> str:
        """Converts datetime object to the website's accepted time format."""
        return data.strftime("%H:%M")

    @log_wrap(before_msg="Adding HTML row")
    def _add_html_row(
        self, html_table_tbody_xpath: str, current_html_row_num: int
    ) -> None:
        """Requests additional rows for input on the timecard website."""
        add_row_button: Any = self.get_element_by_xpath(
            html_table_tbody_xpath
            + "//button[contains(., 'Add Another Row')]"
        )
        # Wait a bit before clicking in case other things are still loading.
        time.sleep(
            constants.timecard['sleep_time']['before_adding_html_row']
        )
        add_row_button.click()
        # Wait until a new HTML row is added.
        current_add_row_wait_time: int = 0
        add_row_button_click_counter: int = 1
        while len(
            self._get_list_of_html_inputs(self._get_html_row_xpath(
                current_html_row_num, html_table_tbody_xpath
            ))
        ) == 0:
            self._raise_error_if_invalid_subtask()
            time.sleep(
                constants.timecard['sleep_time']['after_adding_html_row']
            )
            current_add_row_wait_time +=  \
                constants.timecard['sleep_time']['after_adding_html_row']
            # Click the button once more halfway through waiting just in case.
            if (
                add_row_button_click_counter == 1
                and current_add_row_wait_time > self._default_wait_time * 0.5
            ):
                add_row_button.click()
                add_row_button_click_counter += 1
            if current_add_row_wait_time > self._default_wait_time:
                raise TimeoutError(
                    "Default wait time exceeded for adding HTML row."
                )

    def _raise_error_if_invalid_subtask(self) -> None:
        if (
            len(
                self.get_elements_by_xpath(
                    "//h1[contains(text(), 'Error')]"
                )
            ) > 0
            and len(self.get_elements_by_link_text("Task")) > 0
            and len(
                self.get_elements_by_xpath(
                    "//div[contains(text(), 'Select a valid value.')]"
                )
            ) > 0
        ):
            raise SubtaskNotFound(
                "Please check if the offending subtask exists."
            )
