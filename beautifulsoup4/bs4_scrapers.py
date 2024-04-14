import requests
from bs4 import BeautifulSoup

base_url = 'https://www.themoviedb.org/'
eng = '?language=en'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def movie_or_tv():
    response = requests.get(f'{base_url}{eng}', headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    types = soup.find_all(class_='dropdown_menu')
    if types:
        types_list = [a.text for type in types for a in type.find_all(class_='no_click')]
        types_list = types_list[:2]
        links_list = [a['href'] for type in types for a in type.find_all(class_='no_click')]
        links_list = links_list[:2]
        types_links_dict = {type_text: link for type_text, link in zip(types_list, links_list)}
    else:
        print("Nie znaleziono elementów o class_='dropdown_menu'.")
    return types_links_dict

def get_genres(selected_type):
    url = f'{base_url}{selected_type}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    genres = soup.find_all(id='with_genres')
    if genres:
        genres_list = [a.text for genre in genres for a in genre.find_all(class_='no_click')]
        return genres_list
    else:
        return []