from scrapy.crawler import CrawlerProcess
from moviescraper.moviescraper.spiders.moviespider import MoviesSpider

# Create crawl process
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'ITEM_PIPELINES': {'moviescraper.moviescraper.pipelines.MoviescraperPipeline': 300}
})

# category=1 -> movies
# category=2 -> series
process.crawl(MoviesSpider, category=1, num_pages=2, genre=["Action", "Drama"])
process.start() # the script will block here until the crawling is finished
