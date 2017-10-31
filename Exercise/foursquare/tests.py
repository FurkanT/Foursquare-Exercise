from django.test import TestCase
from selenium import webdriver
import unittest
from django.core.exceptions import ObjectDoesNotExist
import names


class TestAllFeatures(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox(executable_path=r'C:\Users\Tufan Tükek\Desktop\geckodriver.exe')
        self.browser.get('http://localhost:8000')

    def test_home(self):
        self.assertIn('Ultimate Client', self.browser.title)

    def test_searching(self):
        self.browser.find_element_by_name("food").send_keys("pizza")
        self.browser.find_element_by_name("location").send_keys("istanbul")
        self.browser.find_element_by_name("submit").click()
        results = self.browser.find_element_by_class_name("results")
        assert len(results.size) > 0

    def test_four_pages(self):
        self.browser.find_element_by_name("food").send_keys("pizza")
        self.browser.find_element_by_name("location").send_keys("istanbul")
        self.browser.find_element_by_name("submit").click()
        self.browser.implicitly_wait(2)
        self.browser.find_element_by_name("next-page").click()
        self.browser.find_element_by_name("next-page").click()
        self.browser.find_element_by_name("next-page").click()
        self.browser.find_element_by_name("next-page").click()
        results = self.browser.find_element_by_class_name("results")
        assert len(results.size) > 0

    def test_clicking_recent_search(self):
        self.browser.find_element_by_name("recent-search").click()
        results = self.browser.find_element_by_class_name("results")
        assert len(results.size) > 0

    def test_user_registration(self):
        username = names.get_first_name()
        print(username)
        self.browser.find_element_by_name("signup").click()
        self.browser.find_element_by_name("username").send_keys(username)
        self.browser.find_element_by_name("email").send_keys(username+"@email.com")
        self.browser.find_element_by_name("date_of_birth").send_keys("02/04/1995")
        self.browser.find_element_by_name("password1").send_keys("qweasdqwe")
        self.browser.find_element_by_name("password2").send_keys("qweasdqwe")
        self.browser.find_element_by_name("submit").click()
        self.assertIn(username, self.browser.find_element_by_name("welcome-text").text)
        self.browser.find_element_by_name("logout").click()
        self.browser.find_element_by_name("login").click()
        self.browser.find_element_by_name("username").send_keys(username)
        self.browser.find_element_by_name("password").send_keys("qweasdqwe")
        self.browser.find_element_by_name("submit").click()
        self.browser.implicitly_wait(3)
        self.assertEqual("logout", self.browser.find_element_by_name("logout").text)

    def test_no_results(self):
        self.browser.find_element_by_name("food").send_keys("as")
        self.browser.find_element_by_name("location").send_keys("as")
        self.browser.find_element_by_name("submit").click()
        self.assertIn("no result", self.browser.find_element_by_name("no-results").text)

    def test_change_email(self):
        email = names.get_last_name()+"@hotmail.com"
        self.browser.find_element_by_name("login").click()
        self.browser.find_element_by_name("username").send_keys("osman")
        self.browser.find_element_by_name("password").send_keys("qwerty123")
        self.browser.find_element_by_name("submit").click()
        self.browser.find_element_by_name("change-email").click()
        self.browser.find_element_by_name("new_email").send_keys(email)
        self.browser.find_element_by_name("email-change-submit").click()
        self.browser.find_element_by_class_name("success")

    def tearDown(self):
        self.browser.quit()


if __name__ == '__main__':
    unittest.main()



 # def test_change_password(self):
    #     old_password = "qwerty123"
    #     new_password = names.get_last_name()
    #     self.browser.find_element_by_name("login").click()
    #     self.browser.find_element_by_name("username").send_keys("osman")
    #     self.browser.find_element_by_name("old_password").send_keys(old_password)
    #     self.browser.find_element_by_name("new_password1").send_keys(new_password)
    #     self.browser.find_element_by_name("new_password2").send_keys(new_password)
    #
