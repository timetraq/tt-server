"""
Test the registration process with a browser
"""
from unittest import TestCase

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from ...core.lib.db import UserDatabaseConnectivity
from ..lib.browser import prepare_test, cleanup


class RegistrationWebTest(TestCase):
    """
    Test all facets of the registration process
    """

    @classmethod
    def clear_database(cls):
        """
        Clear the database before and after use
        """
        collection = cls.mongo.collection
        for user in ['UnittestExistingTestUser', 'UnittestNonExistingTestUser']:
            test_user = collection.find_one({
                'username': user,
            })
            if test_user:
                collection.remove(test_user)

    @classmethod
    def setUpClass(cls):
        """
        Setup test data, browser and server
        """
        cls.mongo = UserDatabaseConnectivity()
        cls.clear_database()
        test_user = {
            'username': 'UnittestExistingTestUser',
            'salt': '000',
            'password': '000',
            'enabled': False,
        }
        cls.mongo.collection.save(test_user)
        cls.config = dict()
        cls.webdriver = None
        prepare_test(cls)
        # cls.webdriver.maximize_window()
        cls.base_url = 'http://{:s}:{:d}/static/index.xhtml'.format(cls.config['bind_ip'], cls.config['bind_port'])

    @classmethod
    def tearDownClass(cls):
        """
        Disconnect from mongo and cleanup browser, server, etc.
        """
        cls.clear_database()
        del cls.mongo
        cleanup(cls)

    def setUp(self):
        """
        Force a page refresh between tests
        """
        self.webdriver.refresh()
        self.webdriver.implicitly_wait(5)

    def tearDown(self):
        """
        Throw test user out of database
        """
        collection = self.mongo.collection
        test_user = collection.find_one({
            'username': 'UnittestNonExistingTestUser',
        })
        if test_user:
            collection.remove(test_user)

    def __util_get_reg_button(self):
        """
        Get the registration form button
        """
        self.webdriver.get(self.base_url)
        self.webdriver.implicitly_wait(5)
        button = self.webdriver.find_element_by_xpath('//xhtml:button[@data-formaction="registrationForm"]')
        return button

    def __util_open_dialog(self):
        """
        Open the registration dialog
        """
        button = self.__util_get_reg_button()
        button.click()
        self.webdriver.implicitly_wait(5)

    def test_find_button(self):
        """
        Is the button there?
        """
        self.assertIsNotNone(self.__util_get_reg_button())

    def test_open_dialog(self):
        """
        Can we open the dialog?
        """
        dialog_xpath = '//xhtml:div[contains(@class, "bootstrap-dialog")]'
        # Test that there is no dialog open at the moment
        self.assertRaises(NoSuchElementException, self.webdriver.find_element_by_xpath, dialog_xpath)
        self.__util_open_dialog()
        dialog = self.webdriver.find_element_by_xpath(dialog_xpath)
        self.assertIsNotNone(dialog)

    def __util_get_form_and_username_field(self, reopen=True):
        """
        Find the form and the username field
        """
        if reopen:
            self.__util_open_dialog()
        form = self.webdriver.find_element_by_xpath(
            '//xhtml:div[contains(@class, "bootstrap-dialog") and contains(@class, "modal") and @id]'
            '//xhtml:div[@class="bootstrap-dialog-body"]'
            '//xhtml:form[@id="formlib_registration"]'
        )
        username_field = form.find_element_by_name('username')
        return form, username_field

    def test_enter_existing_username(self):
        """
        Test with an already existing username
        """
        form, username_field = self.__util_get_form_and_username_field()
        username_field.click()
        username_field.send_keys('UnittestExistingTestUser')
        username_field.send_keys(Keys.ENTER)
        self.webdriver.implicitly_wait(2)
        error_msg = form.find_element_by_xpath(
            '//xhtml:div[@data-fieldref="formlib_registration_username" and @role="alert"]'
        )
        self.assertTrue(error_msg.text.endswith('username_not_available'))

    @staticmethod
    def util_get_password_fields(form):
        """
        Find the two password fields in the form
        """
        pwd_field_1 = form.find_element_by_name('password1')
        pwd_field_2 = form.find_element_by_name('password2')
        return pwd_field_1, pwd_field_2

    def __util_enter_non_existing_username(self, username_field):
        """
        Enter a username that works
        """
        if username_field.is_enabled():
            username_field.click()
            username_field.send_keys('UnittestNonExistingTestUser')
            username_field.send_keys(Keys.ENTER)
            self.webdriver.implicitly_wait(2)

    def __util_test_single_pwd_error_message(self, form):
        """
        Check if there is only a single pwd error message
        """
        self.webdriver.implicitly_wait(2)
        error_message = form.find_element_by_xpath(
            '//xhtml:div[@data-fieldref="formlib_registration_password1" and @role="alert"]'
        )
        self.assertEqual('Password invalid', error_message.text)
        self.assertRaises(
            NoSuchElementException,
            form.find_element_by_xpath,
            '//xhtml:div[@data-fieldref="formlib_registration_password2" and @role="alert"]'
        )

    def test_non_exist_uname_pwd1_too_short(self):
        """
        Test with a too short password in password 1
        """
        form, username_field = self.__util_get_form_and_username_field()
        self.__util_enter_non_existing_username(username_field)
        pwd1, dummy = RegistrationWebTest.util_get_password_fields(form)
        pwd1.click()
        pwd1.send_keys('123')
        pwd1.send_keys(Keys.ENTER)
        self.__util_test_single_pwd_error_message(form)

    def test_non_exist_uname_pwd1_pwd2_too_short_but_eq(self):
        """
        Test with two passwords equal, but to short
        """
        form, username_field = self.__util_get_form_and_username_field()
        self.__util_enter_non_existing_username(username_field)
        pwd1, pwd2 = RegistrationWebTest.util_get_password_fields(form)
        for pwd in [pwd1, pwd2]:
            pwd.click()
            pwd.send_keys('123')
        pwd2.send_keys(Keys.ENTER)
        self.__util_test_single_pwd_error_message(form)

    def test_non_exist_uname_w_val_pwd1_a_inval_repeat(self):
        """
        Test with long enough passwords, but not equal
        """
        form, username_field = self.__util_get_form_and_username_field()
        self.__util_enter_non_existing_username(username_field)
        pwd1, pwd2 = RegistrationWebTest.util_get_password_fields(form)
        pwd1.click()
        pwd1.send_keys('test1234')
        pwd1.send_keys(Keys.ENTER)
        pwd2.send_keys('test1235')
        pwd2.send_keys(Keys.ENTER)
        self.assertRaises(
            NoSuchElementException,
            form.find_element_by_xpath,
            '//xhtml:div[@data-fieldref="formlib_registration_password1" and @role="alert"]'
        )
        error_message = form.find_element_by_xpath(
            '//xhtml:div[@data-fieldref="formlib_registration_password2" and @role="alert"]'
        )
        self.assertEqual('Passwords do not match', error_message.text)

    def test_full_registration_flow(self):
        """
        Test the registration flow completely
        """
        form, username_field = self.__util_get_form_and_username_field()
        self.__util_enter_non_existing_username(username_field)
        pwd1, pwd2 = RegistrationWebTest.util_get_password_fields(form)
        for pwd in [pwd1, pwd2]:
            pwd.click()
            pwd.send_keys('test1234')
            pwd.send_keys(Keys.ENTER)
        self.webdriver.implicitly_wait(5)
        for field in ['password1', 'password2']:
            self.assertRaises(
                NoSuchElementException,
                form.find_element_by_xpath,
                '//xhtml:div[@data-fieldref="formlib_registration_{:s}" and @role="alert"]'.format(field)
            )
        success_message = form.find_element_by_xpath(
            '//xhtml:div[contains(@class, "alert") and contains(@class, "alert-success") and @role="alert"]'
        )
        self.assertEqual('Registration successful', success_message.text)
        form.find_element_by_xpath(
            '//xhtml:button[contains(@class, "btn") and contains(@class, "btn-default")]'
        )
