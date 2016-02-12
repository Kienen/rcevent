from selenium import webdriver
from django.test import LiveServerTestCase

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

    #Billy loads the login page
    def test_login_page(self):    
        self.browser.get(self.live_server_url + '/account/login')
        self.assertTemplateUsed('login.html')

class TestEventPage(LiveServerTestCase):
    fixtures = ['sites.json']

    @classmethod
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        self.browser.get(self.live_server_url + '/account/signup')
        self.browser.find_element_by_id('id_email').send_keys('Joe@mockmyid.com')
        self.browser.find_element_by_id('id_password').send_keys('correcthorsebatterystaple')
        self.browser.find_element_by_id('id_password_confirm').send_keys('correcthorsebatterystaple\n')


    @classmethod
    def tearDown(self):  
        #self.browser.quit()
        pass

    #Joe Promoter creates an event
    def test_event_creation(self):
        self.browser.get(self.live_server_url + '/event/create')
        self.fail()
