# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ShopscraperItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    selected_default_color = scrapy.Field()
    price = scrapy.Field()
    size = scrapy.Field()
