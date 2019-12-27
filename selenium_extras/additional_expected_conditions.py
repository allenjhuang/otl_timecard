from selenium.common.exceptions import WebDriverException


class url_is_one_of(object):
    """ An expectation for checking the current url.
    urls contain all the potential urls the current url must exactly match
    returns True when the url matches one of the urls, False otherwise
    """

    def __init__(self, urls):
        self.urls = urls

    def __call__(self, driver):
        return driver.current_url in self.urls


def any_of(*expected_conditions):
    """ An expectation that any of multiple expected conditions is true.
    Equivalent to a logical 'OR'.
    Returns results of the first matching condition, or False if none do.
    """
    def any_of_condition(driver):
        for expected_condition in expected_conditions:
            try:
                result = expected_condition(driver)
                if result:
                    return result
            except WebDriverException:
                pass
        return False
    return any_of_condition
