import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class ll_ATS(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 5) # wait 5 seconds for home page


    def test_ll(self):
        user = "testuser"
        pwd = "test9876"

        driver = self.driver
        driver.maximize_window()
        driver.get("http://127.0.0.1:8000/admin")

        elem = driver.find_element(By.ID,"id_username")
        elem.send_keys(user)
        elem = driver.find_element(By.ID,"id_password")
        elem.send_keys(pwd)
        time.sleep(3)
        elem.send_keys(Keys.RETURN)
        driver.get("http://127.0.0.1:8000")
        time.sleep(3)

        try:
            elements = driver.find_elements(By.XPATH, "//button[normalize-space()='Log out']")

            if elements:
                assert True
            else:
                raise NoSuchElementException

        except NoSuchElementException:
            self.fail("User not logged in - ensure user is an Admin user")

        driver.get("http://127.0.0.1:8000/request")
        time.sleep(3)

        try:
            elements = driver.find_elements(By.XPATH, "//button[normalize-space()='Submit Request']")

            if elements:
                assert True
            else:
                raise NoSuchElementException

        except NoSuchElementException:
            self.fail("Submit Request button was not found on the request page")

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(warnings='ignore')