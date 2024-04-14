# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
import time


class MoviescraperPipeline:
    def __init__(self):
        """
        MoviescraperPipeline initializer
        """
        # connect to the database to get the connection and cursor objects
        self.conn = sqlite3.connect("database/database.db", check_same_thread=False)
        self.cur = self.conn.cursor()

    def open_spider(self, spider):
        """
        Runs when spider is opened. Used to clear table that will be used by spider.
        Args:
            spider: spider
        """
        # remove all rows from the table
        self.cur.execute("DELETE FROM data")
        # reset id column sequence to start from 1
        self.cur.execute(f"DELETE FROM sqlite_sequence WHERE name='data'")
        self.conn.commit()
        time.sleep(1)

    def process_item(self, item, spider):
        """
        Inserts the MovieItem object data into the database
        Args:
            item (MovieItem): MovieItem object with data
            spider: spider

        Returns:
            debug string
        """
        # select the table that will be used to insert data
        # insert new data into the table
        self.cur.execute(
            f'INSERT INTO data (title, user_score, release_date, url, genres, runtime, description, director) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (item["title"], item["user_score"], item["release_date"], item["url"], item["genres"], item["runtime"], item["description"], item["director"])
        )
        self.conn.commit()

    def close_spider(self, spider):
        """
        Executed when spider is closed. Used to close database connection
        Args:
            spider: spider
        """
        self.cur.close()
        self.conn.close()
