import selenium.common.exceptions
from flask import Flask, request, render_template, session, redirect, url_for, flash

from beautifulsoup4.bs4_scrapers import movie_or_tv, get_genres
from scrapy.crawler import CrawlerProcess
from moviescraper.moviescraper.spiders.moviespider import MoviesSpider
from database.db_filter import get_data, filter_data
from twisted.internet.error import ReactorNotRestartable

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'secretkey'

# Create crawl process for web scraping
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'ITEM_PIPELINES': {'moviescraper.moviescraper.pipelines.MoviescraperPipeline': 300},
    'LOG_FORMAT': '%(levelname)s: %(message)s',
    'LOG_LEVEL': 'INFO'
})

# Route for selecting movie or TV show type
@app.route('/', methods=['GET', 'POST'])
def type():
    # Get dictionary of types and their links
    types_links_dict = movie_or_tv()
    
    # If form submitted, store selected type in session and redirect to genres page
    if request.method == 'POST':
        session['selected_type'] = request.form.get('type')
        return redirect(url_for('genres'))
    
    # Render template with types for selection
    return render_template('type.html', types_links_dict=types_links_dict)

# Route for selecting genres
@app.route('/genres', methods=['GET', 'POST'])
def genres():
    selected_type = session.get('selected_type')
    genres = get_genres(selected_type)
    
    # If form submitted, store selected genres in session and redirect to scraping page
    if request.method == 'POST':
        session['selected_genre'] = request.form.getlist('genre')
        return redirect(url_for('scraping'))
    
    # Render template with genres for selection
    return render_template('genres.html', genres=genres)

# Route for web scraping
@app.route('/scraping', methods=['GET', 'POST'])
def scraping():
    selected_type = session.get('selected_type')
    selected_genre = session.get('selected_genre')
    category = 1 if selected_type == '/movie?language=en' else 2
    
    # Initiate web scraping process
    try:
        process.crawl(MoviesSpider, category=category, num_pages=4, genre=selected_genre)
        process.start()
    except ReactorNotRestartable:
        flash("Scrapy does not allow to run the spider multiple times - restart the project to scrape different data")
        return redirect(url_for('browse'))
    except selenium.common.exceptions.TimeoutException:
        flash("Page dynamic content navigation exception - restart the project")
        return redirect(url_for('browse'))
    
    # Redirect to browse page after scraping
    return redirect(url_for('browse'))

# Route for browsing scraped data
@app.route('/browse', methods=['GET', 'POST'])
def browse():
    # Get filters from query parameters
    title_filter = request.args.get('title', None)
    year_filter = request.args.get('year', None)
    
    # Retrieve data from the database
    data = get_data()
    
    # Determine if selected type is movie or TV show
    is_movie = session.get('selected_type') == '/movie?language=en'
    
    # Filter data based on filters and selected type
    filtered_data = filter_data(data, is_movie, title_filter, year_filter)
    
    # Render template with filtered data
    return render_template('browse.html', data=filtered_data, is_movie=is_movie)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
