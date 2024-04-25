# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    """
    MovieItem class used to store information about srapped movie/series
    """
    title = scrapy.Field()
    genres = scrapy.Field()
    runtime = scrapy.Field()
    user_score = scrapy.Field()
    description = scrapy.Field()
    director = scrapy.Field()
    release_date = scrapy.Field()
    url = scrapy.Field()
