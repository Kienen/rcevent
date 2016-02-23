from selenium import webdriver
from django.test import LiveServerTestCase
from unittest import skip
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create your tests here.
class TestHomePage(LiveServerTestCase):
    fixtures = ['sites.json']

    @classmethod
    def setUp(self):
       self.browser = webdriver.Firefox()
       self.browser.implicitly_wait(3)

    @classmethod
    def tearDown(self):  
        self.browser.quit()
        pass

    #Billy Participant loads the home page
    def test_index_page(self):
        self.browser.get(self.live_server_url)
        self.assertTemplateUsed('home.html')
        self.assertIn('Events', self.browser.title)
        

    #Billy loads the signup page
    def test_signup_page(self):    
        self.browser.get(self.live_server_url + '/account/signup')
        self.assertTemplateUsed('signup.html')

    #Billy creates an account
    def test_create_user(self):
        self.browser.get(self.live_server_url + '/account/signup')
        self.browser.find_element_by_id('id_email').send_keys('billy@mockmyid.com')
        self.browser.find_element_by_id('id_password').send_keys('correcthorsebatterystaple')
        self.browser.find_element_by_id('id_password_confirm').send_keys('correcthorsebatterystaple\n')
        self.assertIn('Confirm your email address', self.browser.title)
        self.assertTemplateUsed('email_confirmation_sent.html')

class TestLoginPage(LiveServerTestCase):
    fixtures = ['sites.json']

    @classmethod
    def setUp(self):
       self.browser = webdriver.Firefox()
       self.browser.implicitly_wait(3)

    @classmethod
    def tearDown(self):  
        self.browser.quit()
        pass

    #Billy Participant logs in
    def test_login_works(self):
        self.browser.get(self.live_server_url + '/account/login')
        self.assertTemplateUsed('login.html')
        self.browser.find_element_by_id('id_email').send_keys('testuser@dispostable.com')
        self.browser.find_element_by_id('id_password').send_keys('correcthorsebatterystaple\n')

        element = WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.ID, "account_logout"))
        )

        email= self.browser.find_elements_by_class_name("navbar-text")



class TestEventPage(LiveServerTestCase):
    fixtures = ['sites.json']

    @classmethod
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)


    @classmethod
    def tearDown(self):  
        self.browser.quit()
        self.browser.implicitly_wait(3)
        pass

    #Joe Promoter creates an event
    @skip
    def test_event_creation(self):
        self.browser.get(self.live_server_url + '/event/create')
        self.fail()
