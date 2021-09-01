import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time


def scrape_js_content(url):
    """
    :param url: string
    Scrape Java scripted page.
    """
    try:
        session = HTMLSession()
        response = session.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
    finally:
        session.close()

    return response.content


def process_page(soup):
    """
    :param:
    :return:
    """
    freelancers = soup.findAll('div', {'class': "up-card-section up-card-hover"})
    data = list()

    for freelancer in freelancers:

        name = freelancer.find('div', {'class': 'identity-name'}).text.strip()
        talent_title = freelancer.find('p', {'class': 'my-0 freelancer-title'}).text.strip()
        country = freelancer.find('span', {'itemprop': 'country-name'}).text.strip()
        rate = freelancer.find('div', {'data-qa': 'rate'}).text.strip()
        description = freelancer.find('div', {'class': 'up-line-clamp-v2-wrapper mb-0'}).text.strip()

        try:
            earnings = freelancer.find('div', {'data-qa': 'earnings'}).text.strip()
        except:
            earnings = ""

        try:
            success = freelancer.find('span', {'class': 'up-job-success-text'}).text.strip()
        except:
            success = ''

        badges = ', '.join([_.text.strip() for _ in freelancer.findAll('div', {'class': 'up-skill-badge'})])

        data.append([name, talent_title, country, rate, earnings, success, badges, description])

    return data


if __name__ == '__main__':

    search_key_word = input("Search term: ")
    pages = int(input("How many pages to scrape (max 500): "))

    data = list()
    current_len = len(data)

    for page in range(1, pages+1):
        url = f'https://www.upwork.com/search/profiles/?page={page}&q=' + search_key_word.replace(' ', '%20')
        data += process_page(BeautifulSoup(scrape_js_content(url), 'html.parser'))

        # explicit wait times
        time.sleep(np.random.randint(30, 60))
        # check if scraper wasn't blocked
        if len(data) == current_len:
            print('scraper blocked')
            break
        else:
            current_len = len(data)

        print(f'{page}/{pages} scraped.')

        # save temp version every 10 pages
        if page % 10 == 0:
            df = pd.DataFrame(data, columns=['Name', 'Title', 'Country', 'Rate',
                                             'Earnings', 'Success', 'Badges', 'Description'])
            filename = f"data/{search_key_word.replace(' ', '_')}.csv"
            df.to_csv(filename)


    # create pandas DataFrame
    df = pd.DataFrame(data, columns=['Name', 'Title', 'Country', 'Rate',
                                     'Earnings', 'Success', 'Badges', 'Description'])
    filename = f"data/{search_key_word.replace(' ', '_')}.csv"
    df.to_csv(filename)

