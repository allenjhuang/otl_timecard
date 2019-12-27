from __future__ import annotations

from selenium_extras.additional_exceptions import BrowserNotExpected

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from typing import Any, List, Optional, Tuple


class Browser():
    """Abstracted Selenium functionality for simpler use.

    Parameters
    ----------
        browser : str
            Valid options are: "chrome", "edge", "firefox", "ie"
        driver_path : str, optional
            File path to webdriver. Will look in PATH if not set.
        default_wait_time : int, optional
            Default amount of time in seconds to wait when locating elements
            before timing out.

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
        default_wait_time: int = 60
    ) -> None:
        self.driver: Any = self._get_driver(browser, driver_path)
        self.driver_default_wait: WebDriverWait = WebDriverWait(
            driver=self.driver, timeout=default_wait_time
        )

    def _get_driver(
        self, browser: str, driver_path: Optional[str] = None
    ) -> Any:
        lowercased_browser: str = browser.lower()
        driver: Any = None
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
        else:
            raise BrowserNotExpected(
                "Valid browser options are \"chrome\", \"edge\", \"firefox\", "
                "and \"ie\"."
            )
        return driver

    def go_to(self, url: str) -> None:
        """Goes to the url specified."""
        self.driver.get(url)

    def get(self, url: str) -> None:
        """Goes to the url specified."""
        self.driver.get(url)

    def get_element(
        self,
        locator: Tuple[Any, str],
        wait_time: Optional[int] = None
    ) -> Any:
        """Gets the element that matches the locator."""
        if wait_time is None:
            element: Any = self.driver_default_wait.until(
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

    def get_element_by_id(
        self, id: str, wait_time: Optional[int] = None
    ) -> Any:
        """Gets the element that has the specified id."""
        if wait_time is None:
            element: Any = self.driver_default_wait.until(
                EC.visibility_of_element_located(
                    (By.ID, id)
                )
            )
        elif wait_time == 0:
            element = self.driver.find_element_by_id(
                id
            )
        else:
            element = WebDriverWait(
                driver=self.driver, timeout=wait_time
            ).until(
                EC.visibility_of_element_located(
                    (By.ID, id)
                )
            )
        return element

    def get_element_by_link_text(
        self, link_text: str, wait_time: Optional[int] = None
    ) -> Any:
        """Gets the element that contains the specified link text."""
        if wait_time is None:
            element: Any = self.driver_default_wait.until(
                EC.visibility_of_element_located(
                    (By.LINK_TEXT, link_text)
                )
            )
        elif wait_time == 0:
            element = self.driver.find_element_by_link_text(
                link_text
            )
        else:
            element = WebDriverWait(
                driver=self.driver, timeout=wait_time
            ).until(
                EC.visibility_of_element_located(
                    (By.LINK_TEXT, link_text)
                )
            )
        return element

    def get_element_by_xpath(
        self, xpath: str, wait_time: Optional[int] = None
    ) -> Any:
        """Gets the element that has the specified XPath."""
        if wait_time is None:
            element: Any = self.driver_default_wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, xpath)
                )
            )
        elif wait_time == 0:
            element = self.driver.find_element_by_xpath(
                xpath
            )
        else:
            element = WebDriverWait(
                driver=self.driver, timeout=wait_time
            ).until(
                EC.visibility_of_element_located(
                    (By.XPATH, xpath)
                )
            )
        return element

    def get_elements(self, locator: Tuple[Any, str]) -> List[Any]:
        """Gets a list of the elements that match the locator."""
        return self.driver.find_elements(
            locator
        )

    def get_elements_by_xpath(self, xpath: str) -> List[Any]:
        """Gets a list of the elements in the specified XPath."""
        return self.driver.find_elements_by_xpath(
            xpath
        )

    def scroll_into_view(self, element: Any) -> None:
        """Scrolls the current view until the specified element is visible."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView();", element
        )

    def close(self) -> None:
        self.driver.close()
