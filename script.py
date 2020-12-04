#!/usr/bin/env python3

import requests
import json
from requests_html import HTMLSession

data = {}
url = 'https://shop.palaceskateboards.com/collections/new'
products_to_buy = ['ONE 2 ONE REVERSIBLE JACKET BLACK']
basket = []
product_urls = []
size='small' # change this to your required size

def get_customer_details():
	print('Fetching details from config file')
	global data
	with open('config.json') as json_file:
		data = json.load(json_file)


if __name__ == '__main__':
	print('Starting bot service')
	get_customer_details()

	try:
		session = HTMLSession()
		response = session.get(url)
		all_products = response.html.find('.product-info')
		for product in all_products:
			product_title = (product.find('.title', first=True).text)
			if product_title in products_to_buy: # may need to work on this since the title may differ from expected product info
				basket.append(product)

		# we need to get the urls for each of our products
		for product in basket:
			product_url_element = (product.find('.product-link', first=True))
			temp_url = (product_url_element.xpath('//a/@href',first=True))
			temp_concat_url = '{}{}'.format(url,temp_url)
			product_urls.append(temp_concat_url)
			print(temp_concat_url)

		# add to basket
		for product_url in product_urls:
			temp_product = session.get(product_url)
			sizes = temp_product.html.find('#product-select') # size selection must be hidden within js - may need selenium to actually pick the size
	except requests.exceptions.RequestException as e:
		print(e)
