# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    type = scrapy.Field()
    title = scrapy.Field()
    user_score = scrapy.Field()
    release_date = scrapy.Field()
    url = scrapy.Field()
