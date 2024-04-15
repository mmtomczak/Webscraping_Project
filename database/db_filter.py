import sqlite3
import re

def get_data():
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    data = cursor.fetchall()
    conn.close()
    return data

def filter_data(data, is_movie, title_filter=None, year_filter=None):
    filtered_data = data
    
    if title_filter:
        filtered_data = filter(lambda x: re.search(title_filter, x[1], re.IGNORECASE), filtered_data)

    if year_filter:
        if is_movie:
            year_filter_pattern = r'(\d{2})/\d{2}/(\d{4})'
            filtered_data = filter(lambda x: re.match(year_filter_pattern, x[3]).group(2) == year_filter, filtered_data)
        else:
            filtered_data = filter(lambda x: re.search(year_filter, x[3], re.IGNORECASE), filtered_data)

    return list(filtered_data)


