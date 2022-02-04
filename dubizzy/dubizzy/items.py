# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags

def format_price(price):

    return (''.join(price)).strip()

# def filter_items(item):

#     return None if item == '' else item


class DubizzyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = format_price)
    bedrooms = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    bathrooms = scrapy.Field(input_processor = MapCompose(remove_tags),  output_processor =  TakeFirst())
    area = scrapy.Field(input_processor = MapCompose(remove_tags),  output_processor =  TakeFirst())

    location = scrapy.Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    amenities = scrapy.Field(input_processor = MapCompose(remove_tags), )

    details = scrapy.Field()

    # details