import requests
from bs4 import BeautifulSoup

# Base URL for the website
base_url = 'https://www.themoviedb.org/'

# Language parameter for English
eng = '?language=en'

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Function to determine whether the user is interested in movies or TV shows
def movie_or_tv():
    # Send a GET request to the base URL
    response = requests.get(f'{base_url}{eng}', headers=headers)
    
    # Parse the HTML content of the response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all elements with class 'dropdown_menu'
    types = soup.find_all(class_='dropdown_menu')
    
    if types:
        # Extract text and links for the first two items
        types_list = [a.text for type in types for a in type.find_all(class_='no_click')]
        types_list = types_list[:2]
        links_list = [a['href'] for type in types for a in type.find_all(class_='no_click')]
        links_list = links_list[:2]
        
        # Create a dictionary mapping type to its link
        types_links_dict = {type_text: link for type_text, link in zip(types_list, links_list)}
    else:
        print("Can't find elements with class_='dropdown_menu'.")  # Print message if no elements found
    
    return types_links_dict

# Function to get genres based on the selected type (movie or TV show)
def get_genres(selected_type):
    url = f'{base_url}{selected_type}'
    
    # Send a GET request to the URL
    response = requests.get(url, headers=headers)
    
    # Parse the HTML content of the response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all elements with id 'with_genres'
    genres = soup.find_all(id='with_genres')
    
    if genres:
        # Extract genre names
        genres_list = [a.text for genre in genres for a in genre.find_all(class_='no_click')]
        return genres_list
    else:
        return []  # Return an empty list if no genres found
