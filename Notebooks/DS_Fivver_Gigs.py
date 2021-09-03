from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup
import pandas as pd
import time


class FiverrScraper(object):
    """
    Custom Selenium web driver for scraping Fiverr.com gigs
    """

    def __init__(self):
        # Create a browser
        self.driver = Firefox(executable_path="geckodriver.exe")
        self.driver.get("https://www.fiverr.com/?source=top_nav")
        # does Fiverr permit scraping page
        self.status = False
        # continue scrolling search results
        self.scroll = True

    def apply_search(self, search_term='data science'):
        """
        Search Fiverr gigs
        :param search_term: string
        """
        self.driver.find_elements_by_xpath(".//input[@type='search']")[1].send_keys(search_term, Keys.ENTER)
        time.sleep(3)
        no_results = self.driver.find_element_by_class_name('number-of-results').text
        print(no_results)

    def check_status(self):
        """
        Check if access is denied
        """
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        if soup.title.text == 'Your Access To This Website Has Been Blocked':
            self.status = True
            print("Please manually click the button.")
            time.sleep(5)
            self.check_status()
        else:
            self.status = False

    def check_popup(self):
        """
        test for sign-up pop up
        """
        pop_up = self.driver.find_elements_by_class_name('sign-up-form')
        action = ActionChains(self.driver)
        if len(pop_up) > 0:
            action.move_to_element_with_offset(pop_up[0], 700, 0)
            action.click()
            action.perform()

    def scroll_down(self):
        """
        scroll down to the bottom of the page
        """
        js_script = "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return " \
                    "lenOfPage; "
        page_len = self.driver.execute_script(js_script)
        scroll = True
        while scroll:
            least_c = page_len
            page_len = self.driver.execute_script(js_script)
            if least_c == page_len:
                scroll = False

    def click_r_arrow(self):
        """
        Click next arrow if available
        """
        arrows = self.driver.find_elements_by_class_name('pagination-arrows')
        if len(arrows) == 2:
            try:
                arrows[-1].click()
            except:
                self.scroll = False

            # except NoSuchElementException:
            #     self.scroll = False
            # else:
            #     pass

        else:
            self.scroll = False


"""
Helper Functions
"""


def gig_names(response):
    """
    :param response: bs4 html source code
    :return: list, gig names and URls
    """
    # get seller information
    gigs = response.findAll('div', {'class': 'gig-card-layout'})

    info = list()

    for gig in gigs:
        seller_url = "https://www.fiverr.com" + gig.h3.a['href']
        seller_name = gig.find('div', {'class': 'seller-name'}).text
        info.append([seller_name, seller_url])

    return info


def get_txt(element):
    if len(element) >= 1:
        return element[0].text
    else:
        return ''


def seller_info(soup):
    gig_name = soup.h1.text
    seller_lvl = soup.findAll('div', {'class': 'seller-level'})
    one_liner = soup.findAll('p', {'class': 'one-liner'})
    review_score = soup.findAll('b', {'class': 'rating-score'})
    review_count = soup.findAll('span', {'class': 'ratings-count'})

    # package prices
    packages = soup.findAll('div', {'class': 'gig-page-packages-table'})
    if len(packages) > 0:
        prices = [_.text for _ in packages[0].findAll('p', {'class': 'price-label'})]
    else:
        prices = soup.find('div', {'class': 'package-content'}).findAll('span', {'class': 'price'})
        prices = [get_txt(prices), "", ""]

    return [gig_name, get_txt(seller_lvl), get_txt(one_liner), get_txt(review_score), get_txt(review_count)] + prices


if __name__ == '__main__':

    # initiate web driver
    driver = FiverrScraper()
    # ask for keyword
    search_key_word = input("Search term: ")

    # check for detection
    driver.check_status()

    # search for keyword
    driver.apply_search(search_key_word)

    # check for pop-ups and detection
    time.sleep(5)
    driver.check_status()
    driver.check_popup()

    # list for storing gigs info
    data = list()

    # scroll through pages
    while driver.scroll:
        data += gig_names(BeautifulSoup(driver.driver.page_source, "lxml"))
        driver.scroll_down()
        driver.click_r_arrow()
        time.sleep(2)
        driver.check_status()

    # save data
    df_gigs = pd.DataFrame(data, columns=['Seller_name', "Gig_URL"])
    # clean list for storing gigs info
    data = list()

    for idx in df_gigs.index[:6]:
        gig_url = df_gigs.loc[idx, 'Gig_URL']
        driver.driver.get(gig_url)
        time.sleep(2)
        driver.check_status()
        soup = BeautifulSoup(driver.driver.page_source, "lxml")
        data.append([df_gigs.loc[idx, 'Seller_name']] + seller_info(soup))

        # quit driver
    driver.driver.quit()

