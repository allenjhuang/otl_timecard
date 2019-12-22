from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Browser():
    """Abstracted Selenium functionality for simpler use.

    Attributes
    ----------
        driver : selenium.webdriver object
            The webdriver object will differ depending on the browser used.
        driver_default_wait : selenium.webdriver.support.ui.WebDriverWait
    """

    def __init__(self, browser, driver_path=None, default_wait_time=30):
        """
        Parameters
        ----------
            browser : str
                Valid options are: "chrome", "edge", "firefox", "ie"
            driver_path : str, optional
                File path to webdriver. Will look in PATH if not set.
            default_wait_time : int, optional
                Default amount of time in seconds to wait when locating
                elements before timing out.
        """
        self.driver = self._get_driver(browser, driver_path)
        self.driver_default_wait = WebDriverWait(
            driver=self.driver, timeout=default_wait_time
        )

    def _get_driver(self, browser, driver_path):
        lowercased_browser = browser.lower()
        if lowercased_browser == "chrome":
            driver = webdriver.Chrome() if driver_path is None else  \
                webdriver.Chrome(executable_path=driver_path)
        elif lowercased_browser in ("edge", "msedge"):
            driver = webdriver.Edge() if driver_path is None else  \
                webdriver.Edge(executable_path=driver_path)
        elif lowercased_browser == "firefox":
            driver = webdriver.Firefox() if driver_path is None else  \
                webdriver.Firefox(executable_path=driver_path)
        elif lowercased_browser in (
            "ie", "internetexplorer", "internet_explorer", "internet explorer"
        ):
            driver = webdriver.Ie() if driver_path is None else  \
                webdriver.Ie(executable_path=driver_path)
        return driver

    def go_to(self, url):
        self.driver.get(url)

    def get(self, url):
        self.driver.get(url)

    def get_element(self, locator, wait_time=None):
        if wait_time is None:
            element = self.driver_default_wait.until(
                EC.visibility_of_element_located(
                    locator
                )
            )
        elif wait_time == 0:
            element = self.driver.find_element(
                locator
            )
        else:
            element = WebDriverWait(
                driver=self.driver, timeout=wait_time
            ).until(
                EC.visibility_of_element_located(
                    locator
                )
            )
        return element

    def get_elements(self, locator):
        return self.driver.find_elements(
            locator
        )

    def wait(self, wait_time, until_condition):
        WebDriverWait(self.driver, wait_time).until(until_condition)

    def scroll_into_view(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView();", element
        )

    def close(self):
        self.driver.close()
