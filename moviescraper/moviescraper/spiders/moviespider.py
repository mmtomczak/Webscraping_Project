import scrapy
from moviescraper.moviescraper.items import MovieItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import datetime


class MoviesSpider(scrapy.Spider):
    name = "moviespider"
    allowed_domains = ["www.themoviedb.org"]
    start_urls = ["https://www.themoviedb.org"]

    def __init__(self, category: int = 1, num_pages: int = 25):
        """
        MoviesSpider object initializer

        Args:
            category (int): category to be scraped (1-movies, 2-series)
            num_pages (int): number of pages to be scraped (20 items per page)
        """
        super().__init__()
        # set browser options
        self.options = Options()
        # define user agent (necessary due to the --headless option)
        user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        self.options.add_argument(f'user-agent={user_agent}')
        # run in invisible window
        self.options.add_argument("--headless=new")
        # select page language
        self.options.add_argument("--lang=en")
        self.driver = webdriver.Chrome(options=self.options)
        self.is_movie = True if category == 1 else False
        self.category = category
        self.num_pages = num_pages

    def parse(self, response):
        """
        Parses response
        Args:
            response: page response

        Yields:
            scrapy.Request to url to the selected category page and callback to parse_page method
        """
        # run page in Selenium
        self.driver.get(response.url)
        # find and click dropdown menu for given category
        self.driver.find_element(
            By.XPATH,
            f"//ul[contains(@class, 'dropdown_menu') and contains(@class, 'navigation')]/li[{self.category}]"
        ).click()
        # find link to the top-rated page for given category
        url = self.driver.find_element(
            By.XPATH,
            "//div[@class='k-animation-container']/ul/li[4]/a"
        ).get_attribute('href')
        # add page number to the link (to use pagination instead of dynamically loaded content on scroll)
        url += "?page=1"
        # close driver
        self.driver.close()
        for i in range(1, self.num_pages):
            yield scrapy.Request(url,
                                 callback=self.parse_page,
                                 cb_kwargs={"page_num": i})
            # move to the next page url
            url = url.replace(f"page={i}", f"page={i+1}")

    def parse_page(self, response, page_num: int):
        """
        Parses category page

        Args:
            response: page response
            page_num (int): current page number

        Yields:
            MovieItem object
        """
        # initialize driver for page
        page_driver = webdriver.Chrome(options=self.options)
        page_driver.get(response.url)
        # find all movies/series
        items = page_driver.find_elements(
            By.XPATH,
            f"//div[contains(@class, 'media_items') and contains(@class, 'results')]/div[@id='page_{page_num}']"
            f"/div[contains(@class, 'card') and contains(@class, 'style_1') and not(contains(@class, 'filler'))]"
        )
        for item in items:
            # get content div
            content = item.find_element(By.XPATH, "./div[@class='content']")
            # initialize new MovieItem object to store movie/series data
            movie_item = MovieItem()
            # set all movie_items fields
            movie_item["type"] = "movie" if self.is_movie else "series"
            movie_item["title"] = content.find_element(
                By.XPATH,
                "./h2/a"
            ).get_attribute('title')
            movie_item["user_score"] = int(content.find_element(
                By.XPATH,
                "./div[contains(@class, 'consensus') and contains(@class, 'tight')]/div[@class='outer_ring']/div"
            ).get_attribute("data-percent"))
            # parse release date from 'mmm dd, YYYY' to 'dd/mm/YYYY' format
            movie_item["release_date"] = datetime.datetime.strptime(
                content.find_element(By.XPATH, "./p").text,
                "%b %d, %Y").strftime("%d/%m/%Y")
            # get movie page url
            movie_item["url"] = content.find_element(
                By.XPATH,
                "./h2/a"
            ).get_attribute("href")
            yield movie_item
        self.log(f"Page {page_num} finished")
        # close the driver
        page_driver.close()
