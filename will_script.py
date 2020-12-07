import time
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
from difflib import SequenceMatcher
from requests_html import HTMLSession
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver

class palace_bot:
    
    def __init__(self):
        self.base_url = base_url = 'https://shop.palaceskateboards.com'
        self.new_items_url = f'{base_url}/collections/new'
        self.desired_item = 'PALASKA KNIT'
        self.desired_item_colour = 'CREAM'
        self.basket = []
        self.item_urls = []

    def find_products_in_new(self):
        session = HTMLSession()

        # the products are loaded on different pages, we are grabbing page 1-5 and finding all the products within these pages
        for num in range(1,6):
        	temp_url = f'{self.new_items_url}?page={num}'
        	temp_resp = session.get(temp_url)
        	temp_products = temp_resp.html.find('.product-grid-item.clearfix')
        	for prod in temp_products:
        		if prod: # added this check because if a page does not contain any products, the item will be empty and therefore cause an error below
        			product_name = prod.find('.title', first=True).text
        			if SequenceMatcher(None, product_name, self.desired_item).ratio() > 0.7 and product_name.split()[-1] == self.desired_item_colour:
        				self.basket.append(prod)
                
    def fetch_desired_item_urls_from_basket(self):
        for product in self.basket:
            product_url = self.basket[0].find('.product-link', first=True)
            product_url_formatted = product_url.xpath('//a/@href', first=True)
            self.item_urls.append(f'{self.base_url}{product_url_formatted}')
            
    def execute_selenium_bot(self):
        #Open up the browser, adjust options to hide the botness --> Adding cookies will also be good
        option = webdriver.ChromeOptions()
        option.add_argument('--disable-blink-features=AutomationControlled')
        option.add_argument('start-maximized')
        option.add_experimental_option("detach", True)
        option.add_experimental_option("excludeSwitches", ["enable-automation"])
        option.add_experimental_option('useAutomationExtension', False)
        agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        option.add_argument(f"user-agent={agent}")
        driver = webdriver.Chrome(executable_path="/Users/tom/Documents/Python/chromedriver", options=option)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # if there are no products matching our search critera, terminate the program
        if not self.item_urls:
        	print('No items matching search criteria')
        	sys.exit(0)

        #Get the first item URL
        driver.get(self.item_urls[0])
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//select[@name='id']/option[text()='Large']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Add to Cart']"))).click()

        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.XPATH, "//span[@class='cart-count']"), str(len(self.item_urls)))) # check the amount of items in the cart is equal to the amount in our list
        driver.get(f'{self.base_url}/cart')
        
        #Go to cart --> Takes a split second for items to appear. This is the old method but may be needed in the future
        # time.sleep(.5)
        # driver.get(f'{self.base_url}/cart')

        #Agree with T&Cs and proceed
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='terms-checkbox']")))
        driver.execute_script("arguments[0].click();", driver.find_element_by_xpath("//input[@id='terms-checkbox']"))
        driver.find_element_by_id('checkout').click()

        #Delivery info
        driver.find_element_by_id('checkout_email').send_keys("test@test.com")
        driver.find_element_by_id('checkout_shipping_address_first_name').send_keys("John")
        driver.find_element_by_id('checkout_shipping_address_last_name').send_keys("Doe")
        driver.find_element_by_id('checkout_shipping_address_address1').send_keys("1 Palace Road")
        driver.find_element_by_id('checkout_shipping_address_city').send_keys("London")
        driver.find_element_by_id('checkout_shipping_address_zip').send_keys("BR1 1AA")
        driver.find_element_by_id('checkout_shipping_address_phone').send_keys("0123456789")

        #Click on captcha
        iframes = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(iframes[1])
        driver.find_element_by_id('recaptcha-anchor').click()

        time.sleep(5) #Captcha solving time (want to get rid off this)
        driver.switch_to.default_content()
        driver.find_element_by_id('continue_button').click()

        time.sleep(2) #Having to sleep because code below isn't working
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type=submit and @id='continue_button']")))

        # #Card information    
        iframes = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(iframes[1])
        driver.find_element_by_id('number').send_keys("1234 1234 1234")
        driver.switch_to.default_content()
        driver.switch_to.frame(iframes[2])
        driver.find_element_by_id('name').send_keys("MR JOHN DOE")
        driver.switch_to.default_content()
        driver.switch_to.frame(iframes[4])
        driver.find_element_by_id('expiry').send_keys("01")
        driver.find_element_by_id('expiry').send_keys("25")
        driver.switch_to.default_content()
        driver.switch_to.frame(iframes[5])
        driver.find_element_by_id('verification_value').send_keys("123")

        #Complete purchase
        driver.switch_to.default_content()
        driver.find_element_by_id('continue_button').click()

if __name__ == '__main__':
	pb = palace_bot()
	pb.find_products_in_new()
	pb.fetch_desired_item_urls_from_basket()
	pb.execute_selenium_bot()