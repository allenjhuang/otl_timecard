'''
DESCRIPTION
    otl_timecard.py - Uses Selenium and a reference timecard.csv file to fill out the Oracle overtime-eligible timecard.
    Use only if you agree that the creator of this script will not be responsible for late timecard submissions, any loss of data, or any damage to your computer.
INSTRUCTIONS
    For the first time:
    1. Download the Mozilla geckodriver from "https://github.com/mozilla/geckodriver/releases".
    2. Move the geckodriver into the same directory as this script.
    3. Create a "timecard.csv" file with the following header row:
        Project, Task, Type, Work_Location_Country, Work_Location_State_Province, Sat_Start, Sat_Stop, Sun_Start, Sun_Stop, Mon_Start, Mon_Stop, Tue_Start, Tue_Stop, Wed_Start, Wed_Stop, Thu_Start, Thu_Stop, Fri_Start, Fri_Stop
    4. Fill out the timecard.csv rows with your timecard data. Project, Task, Type, Work_Location_Country, and Work_Location_State_Province MUST be filled out exactly as they would be on the timecard website. If editing the timecard.csv file with Excel or LibreCalc, make sure that they don't autocorrect any words, special characters, etc.
    5. Install python3.
    6. Open up the command line and type in "python3 -m pip install --user selenium pandas".
    7. If already within the same directory, run the script with "python3 otl_timecard.py", otherwise navigate to the script directory first.
Last updated 6/21/19
'''

import datetime
import os
import pandas
import platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
try:
    from user_login import sso_username
    from user_login import sso_password
except Exception:
    pass
import sys
import time

# TODO: Remove the pandas module and replace with the csv module, since pandas is overkill for what is needed. Code will need to be updated and checked.

# Global variables
COLS_BEFORE_TIME = 5  # Project, Task, Type, Work_Location_Country, Work_Location_State_Province
NUMBER_OF_ROWS_BEFORE_ADD = 6  # The number of HTML rows available to fill with timecard information before needing to add more rows.
WAIT_TIME = 60  # The amount of time in seconds that the web driver will wait before timing out.


def current_time():
    return datetime.datetime.now().strftime('%H:%M:%S')


def set_driver(driver_location):
    print(current_time() + " driver_location = " + str(driver_location))
    driver = webdriver.Firefox(executable_path=driver_location)
    return driver


# By default, the driver name is different depending on the operating system.
platform = platform.system()
if (platform in ["Linux", "Darwin"]):
    try:
        driver = set_driver("./geckodriver")  # Current working directory.
    except Exception:
        driver = set_driver(os.path.join(os.getcwd(), "geckodriver"))  # Current working directory.
        # driver = set_driver(os.path.join(os.path.realpath(sys.path[0]), "geckodriver"))  # Script directory.
elif (platform == "Windows"):
    try:
        driver = set_driver(".\\geckodriver.exe")
    except Exception:
        driver = set_driver(os.path.join(os.getcwd(), "geckodriver.exe"))  # Current working directory.
        # driver = set_driver(os.path.join(os.path.realpath(sys.path[0]), "geckodriver.exe"))  # Script directory.

wait = WebDriverWait(driver, WAIT_TIME)  # Define maximum Selenium wait times.


# TODO: Use argparse to enable an optional flag to open test timecard or not and an optional flag to create a timecard.csv template.
def main():
    authentication_sso_page()
    nav_to_timecard()
    # open_test_timecard()
    fill_timecard()


def authentication_sso_page():
    print(current_time() + " authentication_sso_page()")
    # Go to this URL.
    url = "https://global-ebusiness.oraclecorp.com/OA_HTML/OA.jsp?OAFunc=OAHOMEPAGE"
    driver.get(url)

    # ASSUMPTION: Page is redirected to the Single Sign On screen.
    # Wait until username input is visible and then assign it to the variable, element.
    element = wait.until(EC.visibility_of_element_located((By.ID, "sso_username")))
    # Enter the username.
    try:
        element.send_keys(sso_username)
    except Exception:
        print(current_time() + " Please type in the username.")
    # Enter the password.
    element = wait.until(EC.visibility_of_element_located((By.ID, "ssopassword")))
    try:
        element.send_keys(sso_password + Keys.RETURN)
    except Exception:
        print(current_time() + " Please type in the password and login within " + str(WAIT_TIME) + " seconds.")

    # ASSUMPTION: Page is redirected to one of the following URLs.
    wait.until(lambda driver: (driver.current_url == "https://login.oracle.com/oam/server/sso/auth_cred_submit") or ("https://global-ebusiness.oraclecorp.com/OA_HTML/OA.jsp" in driver.current_url))
    if (driver.current_url != url):
        # Just try going to the SSA page again.
        driver.get(url)


def nav_to_timecard():
    print(current_time() + " nav_to_timecard()")
    # Navigate towards Recent Timecards.
    element = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "US OTL - Emps Eligible for Overtime (Project Accounting)")))
    element.click()
    element = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "Recent Timecards")))
    element.click()
    # Create new timecard.
    element = wait.until(EC.visibility_of_element_located((By.ID, "Hxccreatetcbutton")))
    element.click()


def fill_timecard():  # TODO: Would like to refactor the code to be a bit more readable someday. Maybe consider moving the nested functions out to the global scope.
    print(current_time() + " fill_timecard()")
    def fill_details(csv, html_rows_xpath, csv_start, csv_end):
        print(current_time() + " fill_details(csv, html_rows_xpath, csv_start, csv_end)")
        # Loop through rows.
        for row in range(csv_start, csv_end):
            list_of_inputs = driver.find_elements_by_xpath(html_rows_xpath + "[" + str(row + 2) + "]//input")  # XPath is 1-indexed and the first row is the header, so we add 2.
            csv_col = -1  # Need a counter here since the total csv columns and total html inputs don't match - we are ignoring the html input for hours.
            # Loop through columns.
            for html_col in range(len(list_of_inputs)):
                # Set the cell_data to send to the HTML input.
                if (html_col < COLS_BEFORE_TIME):
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

    def add_html_row(html_rows_xpath, csv_end, times):  # TODO: Looks like the site adds 6 rows with one click now. Should probably remove the multiple button clicks, though it doesn't hurt.
        print(current_time() + " add_html_row(html_rows_xpath, csv_end, times)")
        # Add html rows n amount of times.
        for n in range(times):  # FIXME: Looks like the Linux version of the webdriver struggles to find the "Add Another Row" button sometimes here.
            element = wait.until(EC.visibility_of_element_located((By.XPATH, html_rows_xpath + "//button[contains(., 'Add Another Row')]")))
            element.click()
            wait.until(EC.visibility_of_element_located((By.XPATH, html_rows_xpath + "[" + str(csv_end + n + 2) + "]")))  # Wait until a new HTML row is added. FIXME: Doesn't seem to be working as expected. The print statement on the next line appears to execute before the new HTML row is found. Maybe check and compare the length of the list of html rows before and after instead.
            print(current_time() + " HTML row added.")
        print(current_time() + " Finished adding " + str(times) + " HTML rows.")

    # Begin process.
    # Parse the .csv file.
    try:
        csv = pandas.read_csv(os.path.join(os.path.realpath(sys.path[0]), "timecard.csv"))  # Script directory.
    except Exception:
        csv = pandas.read_csv(os.path.join(os.getcwd(), "timecard.csv"))  # Current working directory.
    html_rows_xpath = "//span[@id='Hxctimecard']/table[2]//table[2]/tbody/tr[5]/td/table/tbody/tr[5]/td[2]/table/tbody/tr"  # The rows for the timecard website, not the .csv file.
    len_of_csv = len(csv)  # The number of rows for the .csv file.

    csv_start = 0  # Start processing on this row.
    csv_end = NUMBER_OF_ROWS_BEFORE_ADD  # End processing on this row.
    while (True):
        fill_details(csv=csv, html_rows_xpath=html_rows_xpath, csv_start=csv_start, csv_end=csv_end)
        print(current_time() + " csv_start = " + str(csv_start))
        print(current_time() + " csv_end = " + str(csv_end))
        add_html_row(html_rows_xpath=html_rows_xpath, csv_end=csv_end, times=NUMBER_OF_ROWS_BEFORE_ADD)  # Click "Add Another Row" a number of times to match the .csv file rows.
        csv_start += NUMBER_OF_ROWS_BEFORE_ADD
        csv_end += NUMBER_OF_ROWS_BEFORE_ADD
        print(current_time() + " csv_start = " + str(csv_start))
        print(current_time() + " csv_end = " + str(csv_end))
        if (csv_end >= len_of_csv):
            fill_details(csv=csv, html_rows_xpath=html_rows_xpath, csv_start=csv_start, csv_end=len_of_csv)  # Finish off the timecard details.
            print(current_time() + " Finished filling out timecard details.")
            break


def open_test_timecard():
    print(current_time() + " open_test_timecard()")
    # Open offline page for testing.
    url = "file:///path/OTL_Entry.html"  # Saved HTML of the timecard entry page.
    driver.get(url)


if __name__ == '__main__':
    main()
