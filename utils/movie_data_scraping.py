from requests_html import HTMLSession
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import re
import time
from bs4 import BeautifulSoup as bs
import random
import numpy as np
import pandas as pd

def get_all_movie_links(language: str):
    
    def get_num_titles(url: str):
        
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0',
            ]

        session = HTMLSession(browser_args=["--no-sandbox", '--user-agent=' + random.choice(user_agents)])
        response = session.get(url)
        print(url)

        if response.status_code != 200:
            print(response.status_code, url)
        
        soup = bs(response.content, 'lxml')
            
        try:
            text = soup.select_one('div.desc span').text

            if text == 'No Results.':
                return 0, url
            
            num_search = re.search('of (.*) titles', text)
            if num_search:
                num = int(num_search.group(1).replace(',',''))
                print(f'{num} titles found\n')      
            else:
                num_search = re.search('(.*) titles', text)
                num = int(num_search.group(1))
                print(f'{num} titles found\n') 
            return num, url
        except Exception as e:
            print(e)
            pass
        return 0, url
    
    def movie_links(count = 250, rating = 4.5, votes = 100): 
        t1 = time.time()
        urls = []
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = (executor.submit(get_num_titles, f'https://www.imdb.com/search/title/?title_type=feature&release_date={year}-01-01,{year}-12-31&user_rating={rating},&num_votes={votes},&primary_language={language}&count={count}') for year in range(1914,2024))
            for future in concurrent.futures.as_completed(futures):
                ntitles, base_url = future.result()
                urls += [base_url + '&start=' + str(i) for i in range(1, ntitles, count)]
        t2 = time.time()
        print(t2-t1)
        return urls

    return movie_links()

def get_all_movie_info(links: list, language):

    def get_movies_info(url: str, language = language):
        # t1 = time.time()
        user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0',
        ]

        session = HTMLSession(browser_args=["--no-sandbox", '--user-agent=' + random.choice(user_agents)])
        response = session.get(url)

        if response.status_code != 200:
            print(response.status_code, url)

        response.html.arender(wait = 2, sleep=2)
        soup = bs(response.content, 'lxml')
        current_page = []
        try:
            elements = soup.select('div.lister-item')
            # movie_cast_info = {}
            for element in elements:
                movie_info = {}
                # image link
                try:
                    image_link = element.select_one('div.lister-item-image a').find('img','loadlate').get('loadlate')
                    movie_info['poster'] = image_link
                except Exception:
                    movie_info['poster'] = np.nan

                # imdb id
                try:
                    pattern = re.compile(r'tt\d*')
                    page = element.select_one('div.lister-item-content h3.lister-item-header a').get_attribute_list('href')[0]
                    movie_info['imdb-id'] = pattern.search(page).group()
                except Exception:
                    movie_info['imdb_id'] = np.nan

                # movie title
                try:
                    movie_info['title'] = element.select_one('div.lister-item-content h3.lister-item-header a').text.strip().replace('\n','')
                except Exception:
                    movie_info['title'] = np.nan

                # release year
                try:
                    pattern = re.compile(r'\d{4}')
                    year = element.select_one('div.lister-item-content h3.lister-item-header span.lister-item-year').text
                    movie_info['release-year'] = pattern.search(year).group()
                except Exception:
                    movie_info['release-year'] = np.nan

                # runtime
                try:
                    pattern = re.compile(r'\d*')
                    runtime = element.select_one('div.lister-item-content p.text-muted span.runtime').text
                    movie_info['runtime'] = float(pattern.search(runtime).group())
                except:
                    movie_info['runtime'] = np.nan

                # genres
                try:
                    movie_info['genre'] = element.select_one('div.lister-item-content p.text-muted span.genre').text.strip().replace('\n','')
                except:
                    movie_info['genre'] = np.nan

                # imdb rating
                try: 
                    movie_info['imdb-rating'] = float(element.select_one('div.lister-item-content div.ratings-bar div.ratings-imdb-rating').text.strip().replace('\n',''))
                except Exception:
                    movie_info['imdb-rating'] = np.nan

                # metascore
                try: 
                    pattern = re.compile(r'\d{1,}')
                    score = element.select_one('div.lister-item-content div.ratings-bar div.ratings-metascore').text
                    movie_info['metascore'] = pattern.search(score).group()
                except Exception:
                    movie_info['metascore'] = np.nan

                # movie plot
                try:
                    movie_info['overview'] = element.select('div.lister-item-content p.text-muted')[1].text.strip().replace('\n','')
                except:
                    movie_info['overview'] = np.nan

                # imdb votes
                try:
                    pattern = re.compile(r'\d{1,}')
                    votes = element.select_one('div.lister-item-content p.sort-num_votes-visible').text.replace(',','')
                    movie_info['votes'] = pattern.search(votes).group()
                except Exception:
                    movie_info['votes'] = np.nan

                # directors and cast
                try:
                    directors = []
                    cast = []
                    stop_tag = element.find('p',class_='').select_one('span.ghost')
                    if stop_tag:
                        ds= stop_tag.find_previous_siblings('a')
                        for tag in ds:
                            director = {}
                            pattern = re.compile(r'nm\d*')
                            director['id'] = pattern.search(tag['href']).group()
                            director['name'] = tag.text
                            directors.append(director)
                        
                        c = stop_tag.find_next_siblings('a')
                        cast = []
                        for tag in c:
                            actor = {}
                            pattern = re.compile(r'nm\d*')
                            actor['id'] = pattern.search(tag['href']).group()
                            actor['name'] = tag.text
                            cast.append(actor)
                    else:
                        tag = element.find('p', class_='')
                        if 'Stars' in tag.text:
                            for item in tag.select('a'):
                                actor = {}
                                pattern = re.compile(r'nm\d*')
                                actor['id'] = pattern.search(tag['href']).group()
                                actor['name'] = tag.text
                                cast.append(actor)
                        elif 'Directors' in tag.text:
                            for tag in ds:
                                director = {}
                                pattern = re.compile(r'nm\d*')
                                director['id'] = pattern.search(tag['href']).group()
                                director['name'] = tag.text
                                directors.append(director)
                except Exception as e:
                    pass
                finally:
                    movie_info['directors'] = directors
                    movie_info['cast'] = cast
                    
                movie_info['language'] = language
                current_page.append(movie_info)
        except Exception as e:
            print(e)
            pass
        
        # t2 = time.time()
        return current_page
       
    def executor(links: list):
            movie_list = []
            t1 = time.time()
            with ThreadPoolExecutor(max_workers=32) as executor:
                futures = (executor.submit(get_movies_info, link) for link in links)
                for future in concurrent.futures.as_completed(futures):
                    movie_list += future.result()
                    if len(movie_list)%500 == 0:
                        print(len(movie_list))
            t2 = time.time()
            print(t2-t1)

            return movie_list
    
    return executor(links)

if __name__ == '__main__' :
    languages = {   'english' : 'en',
                    'french' : 'fr',
                    'tamil' : 'ta', 
                    'italian':'it', 
                    'malayalam' : 'ml', 
                    'hindi' : 'hi', 
                    'korean' : 'ko', 
                    'japanese': 'ja', 
                    'german' : 'de',
                    'spanish' : 'es',
                    'danish' : 'da',
                    'chinese' : 'cmn'
                }
    
    for language, code in languages.items():
        links = get_all_movie_links(code)
        movies = get_all_movie_info(links, code)
        df = pd.DataFrame(movies)
        df.to_csv(f'ScrapedData/{language}.csv', index = False)

