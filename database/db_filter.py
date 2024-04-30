import sqlite3
import re

def get_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM data")
    data = cursor.fetchall()
    conn.close()
    
    return data

def filter_data(data, is_movie, title_filter=None, year_filter=None):
    filtered_data = data
    
    # Apply title filter if provided
    if title_filter:
        # Use regular expression to search for title matches ignoring case
        filtered_data = filter(lambda x: re.search(title_filter, x[1], re.IGNORECASE), filtered_data)

    # Apply year filter if provided
    if year_filter:
        if is_movie:
            # Define pattern to extract year from movie release date (MM/DD/YYYY)
            year_filter_pattern = r'(\d{2})/\d{2}/(\d{4})'
            # Filter data based on year extracted from release date
            filtered_data = filter(lambda x: re.match(year_filter_pattern, x[3]).group(2) == year_filter, filtered_data)
        else:
            # Use regular expression to search for year matches ignoring case
            filtered_data = filter(lambda x: re.search(year_filter, x[3], re.IGNORECASE), filtered_data)

    return list(filtered_data)
