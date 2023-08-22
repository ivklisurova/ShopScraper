import scrapy
from scrapy import Request
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import urllib.parse
from ..items import ShopscraperItem


class ShopSpider(scrapy.Spider):
    name = 'sspider'
    allowed_domains = ['shop.mango.com']
    start_urls = ['https://shop.mango.com/gb/women/skirts-midi/midi-satin-skirt_17042020.html?c=99',
                  'https://shop.mango.com/bg-en/men/t-shirts-plain/100-linen-slim-fit-t-shirt_47095923.html?c=07']

    @staticmethod
    def get_product_code(address):
        parsed = urllib.parse.urlsplit(address)
        partial = ("{}?{}".format(parsed.path.split("/")[-1], parsed.query).split('_'))[-1]

        product_code = (''.join(element for element in partial if element.isdigit()))
        product_id = partial.split('=')[-1]
        return product_code, product_id

    def start_requests(self):
        for url in self.start_urls:
            # url = 'https://shop.mango.com/gb/women/skirts-midi/midi-satin-skirt_17042020.html?c=99'
            item_code = self.get_product_code(url)[0]
            item_id = self.get_product_code(url)[1]
            desired_capabilities = DesiredCapabilities.CHROME
            desired_capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--ignore-certificate-errors')

            driver = webdriver.Chrome(options=options)

            driver.get(url)
            time.sleep(2)

            logs = driver.get_log('performance')

            for log in logs:
                network_log = json.loads(log['message'])['message']

                if network_log['method']=='Network.responseReceived':
                    try:
                        api_url = network_log['params']['response']['url']
                        if item_code in api_url:
                            yield Request(url=api_url,
                                          callback=self.parse, meta={'item_id': item_id})
                    except KeyError:
                        pass
            driver.quit()

    def parse(self, response, **kwargs):
        item = ShopscraperItem()
        item_id = response.meta.get('item_id')
        data = json.loads(response.body)

        default_prod_idx = None
        for idx, product in enumerate(data['colors']['colors']):
            if product['id']==item_id:
                default_prod_idx = idx

        item['name'] = data['name']
        item['selected_default_color'] = data['colors']['colors'][default_prod_idx]['label']
        item['price'] = data['colors']['colors'][default_prod_idx]['price']['price']
        item['size'] = data['colors']['colors'][default_prod_idx]['sizes']

        yield item
