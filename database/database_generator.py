import sqlite3


class DatabaseGenerator:
    def __init__(self, cur, db):
        """
        DatabaseGenerator object initializer. Used to recreate the database file

        Args:
            cur: database cursor object
            db: database connection object
        """
        self.cur = cur
        self.db = db

    def recreate_database(self):
        """
        Recreates the database
        """
        # drop all tables
        self.cur.execute("DROP TABLE IF EXISTS movies")
        self.cur.execute("DROP TABLE IF EXISTS series")
        self.cur.execute("DROP TABLE IF EXISTS data")
        # create tables
        self.cur.execute('''
        ''')
        self.cur.execute('''
        CREATE TABLE data(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            user_score INTEGER NOT NULL,
            release_date VARCHAR(200),
            url VARCHAR(300) NOT NULL,
            genres VARCHAR(300),
            runtime VARCHAR(200),
            description TEXT,
            director VARCHAR(200)
        )
        ''')
        self.db.commit()
