from typing import Union

import scrapy
import selenium.common.exceptions
from scrapy import Spider
from twisted.internet.defer import Deferred

from moviescraper.moviescraper.items import MovieItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import requests
import re


class MoviesSpider(scrapy.Spider):
    name = "moviespider"
    allowed_domains = ["www.themoviedb.org"]
    start_urls = ["https://www.themoviedb.org"]

    def __init__(self, category: int = 1, num_pages: int = 25, genre: str = ""):
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
        self.options.add_argument("--start-maximized")
        # run in invisible window
        self.options.add_argument("--headless=new")
        # select page language
        self.options.add_argument("--lang=en")
        self.options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(options=self.options)
        self.is_movie = True if category == 1 else False
        self.category = category
        self.num_pages = num_pages
        self.genre = genre

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
        actions = ActionChains(self.driver)
        cookies_accept_xpath = "/html/body/div[9]/div[2]/div/div[1]/div/div[2]/div/button[3]"
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
            (By.XPATH, cookies_accept_xpath)
        ))
        cookies = self.driver.find_element(By.XPATH, cookies_accept_xpath)
        actions.move_to_element(cookies).click().perform()
        # find and click dropdown menu for given category
        categories = self.driver.find_element(
            By.XPATH,
            f"//ul[contains(@class, 'dropdown_menu') and contains(@class, 'navigation')]/li[{self.category}]"
        )
        actions.move_to_element(categories).click().perform()
        # find link to the top-rated page for given category
        top_movies_xpath = "//div[@class='k-animation-container']/ul/li[4]/a"
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
            (By.XPATH, top_movies_xpath)
        ))
        url = self.driver.find_element(
            By.XPATH,
            top_movies_xpath
        )
        if self.genre:
            actions.move_to_element(url).click().perform()
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
                (By.XPATH, "//ul[@id='with_genres']/li/a")
            ))
            for genre in self.genre:
                genre_xpath = f"//ul[@id='with_genres']/li/a[contains(text(), '{genre}')]"
                genre = self.driver.find_element(By.XPATH, genre_xpath)
                actions.move_to_element(genre).click().perform()
            search_btn_xpath = "//p[@class='load_more']/a[contains(@class, 'no_click') and contains(@class, 'load_more')]"
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable(
                (By.XPATH, search_btn_xpath)
            ))
            self.driver.execute_script("window.scrollBy(0, 50);")
            search_btn = self.driver.find_element(By.XPATH, search_btn_xpath)
            actions.move_to_element(search_btn).click().perform()

        load_more_btn_xpath = "//p[@class='load_more']/a[contains(@class, 'no_click') and contains(@class, 'load_more')]"
        load_more_btn = self.driver.find_element(By.XPATH, load_more_btn_xpath)
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        self.driver.execute_script("arguments[0].click();", load_more_btn)

        loaded_content_xpath = "/html/body/div[1]/main/section/div/div/div/div[2]/div[2]/div/section/div/div[2]"
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
            (By.XPATH, loaded_content_xpath)
        ))

        for i in range(1, self.num_pages + 1):
            page_urls = self.get_urls(page_num=i)
            for url in page_urls:
                yield scrapy.Request(url,
                                     callback=self.parse_page)
            # move to the next page url
            self.log(f"Scrapped page {i}")
            self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")

    def parse_page(self, response):
        """
        Parses category page

        Args:
            response: page response

        Yields:
            MovieItem object
        """
        movie_item = MovieItem()

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        soup = BeautifulSoup(requests.get(response.url + "?language=en",headers=headers).text, "html.parser")

        movie_item["title"] = soup.select(f".title")[0].select("h2")[0].select("a")[0].text
        if self.category == 1:
            movie_item["runtime"] = soup.select("span.runtime")[0].text.strip()
            release_date = soup.select("span.release")[0].text.strip()
        else:
            movie_item["runtime"] = ""
            release_date = soup.select("span.release_date.tag")[0].text.strip()
        release_date = re.sub("([ (A-Za-z)])", "", release_date)
        movie_item["release_date"] = release_date
        movie_item["genres"] = ", ". join([item.text for item in soup.select("span.genres")[0].findAll('a')])
        movie_item["user_score"] = int(soup.select("div.user_score_chart")[0].attrs["data-percent"])
        movie_item["description"] = soup.select("div.overview")[0].select("p")[0].text
        try:
            movie_item["director"] = ", ".join([item.select('p')[0].text for item in soup.select("ol.people.no_image")[0].select("li") if "Director" or "Creator" in item.select("p.character")[0].text])
        except IndexError:
            movie_item["director"] = ""
        movie_item["url"] = response.url
        yield movie_item

    def get_urls(self, page_num):
        urls = []
        content_xpath = f"//div[contains(@class, 'media_items') and contains(@class, 'results')]/div[@id='page_{page_num}']/div[contains(@class, 'card') and contains(@class, 'style_1') and not(contains(@class, 'filler'))]"
        items = self.driver.find_elements(
            By.XPATH,
            content_xpath
        )
        for item in items:
            content = item.find_element(By.XPATH, "./div[@class='content']")
            urls.append(content.find_element(By.XPATH, "./h2/a").get_attribute("href"))
        return urls

    def closed(self, reason):
        self.driver.close()

