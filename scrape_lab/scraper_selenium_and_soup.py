import requests
from bs4 import BeautifulSoup
import json
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from time import sleep
import re


def get_number_of_tracks(soup):
    try:
        meta_song_count = soup.find('meta', {'name': 'music:song_count'})
        song_count = int(meta_song_count.attrs["content"])
        return song_count
    except TypeError:
        print('Could not find valid number of tracks')


def is_last_element_visible(soup, song_count):
    test_locator = '#main .JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2) > div:nth-child(1)'
    test_element = soup.select(test_locator)
    locator = '#main .JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2) > div:nth-child({})'.format(song_count)
    element = soup.select(locator)
    if len(element) == 0:
        return False
    return True


def scroll_with_selenium(driver, actions, click = True):
    if click:
        locator = 'contentSpacing'
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME,locator))).click()

    print('\nscrolling now')
    for i in range(10):
        actions.key_down(Keys.ARROW_DOWN)
    actions.perform()
    sleep(2)

    return
    #actions.key_up(Keys.ARROW_DOWN)
    #test_extract = soup.find('div', {"aria-rowindex": "5"})
    #html_content = test_extract.prettify(formatter='html').replace("\n", "").replace(" ", '')
    #element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME,locator)))
    #actions.move_to_element(html_content).perform()
    #div = driver.execute_script("document.getElementsByClassName('main-view-container__scroll-node-child')")
    #scrollTop = driver.execute_script("document.getElementsByClassName('os-viewport os-viewport-native-scrollbars-invisible')[1].scrollTop")
    #windowHeight = driver.execute_script("document.getElementsByClassName('os-viewport os-viewport-native-scrollbars-invisible')[1].clientHeight")
    #scrollHeight = div.scrollHeight
    #sleep(3)
    #div_element = driver.find_element(By.CLASS_NAME,"os-viewport os-viewport-native-scrollbars-invisible")
    #driver.execute_script("window.scrollTo(0, window.innerHeight);")
    #sleep(3)


# experimenting with selenium
def selenium_setup(URL):
    options = ChromeOptions()
    options.headless = False
    driver = Chrome(executable_path='/Users/julienlook/Documents/Coding/spotify_downloader/chromedriver', options=options)
    driver.get(url=URL)
    driver.maximize_window()
    actions = ActionChains(driver)

    # load soup
    sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    song_count = get_number_of_tracks(soup)

    # experimenting with scroll behavior
    scroll_with_selenium(driver, actions)

    # check if last track is visible by HTML 
    while not is_last_element_visible(soup, song_count):
        scroll_with_selenium(driver, actions, click = False)

        # reinitialize soup
        # TODO: get a proper sleep time to see if elements really loaded
        sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print('still in loop')


    driver.quit()



# experimenting with soup
def print_scripts(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, features='lxml')
    res = soup.find_all('script')
    json_object = json.loads(res.contents[0])
    print(json_object)






def extract_head_meta_information(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    test_element = soup.find_all('meta', {'name': 'music:song'})[0]
    test_extract = test_element.attrs['content']
    return test_extract


def extract_information_from_song_url(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    track_elements = soup.find_all('title')[0].contents[0].split(('- song and lyrics by'))
    song_name = track_elements[0].strip()
    artist_name = re.sub( '\|', '',re.sub( 'Spotify', '', track_elements[1])).strip()
    return (song_name, artist_name)



def my_tag_selector(tag):
	# We only accept "a" tags with a titlelink class
	return tag.name == "a" and tag.has_attr("class") and "t_yrXoUO3qGsJS4Y6iXX" in tag.get("class")


# experimenting with selenium + BS
def selenium_soup(URL):
    options = ChromeOptions()
    options.headless = True
    driver = Chrome(executable_path='/Users/julienlook/Documents/Coding/spotify_downloader/chromedriver', options=options)
    driver.get(url=URL)
    sleep(3)
    # add a try statement here in case the webpage hasn't been loaded yet

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #song_elements = soup.find_all('a', {"data-testid": "internal-track-link"})
    #song_elements = soup.find_all('div', {"class": "iCQtmPqY0QvkumAOuCjr"}, limit=None)
    #soup.select('data-testid="tracklist-row" > tr[style*="height:18px;"]')


    #main > div > div.Root__top-container > div.Root__main-view > div.main-view-container > div.os-host.os-host-foreign.os-theme-spotify.os-host-resize-disabled.os-host-scrollbar-horizontal-hidden.main-view-container__scroll-node.os-host-transition.os-host-overflow.os-host-overflow-y > div.os-padding > div > div > div.main-view-container__scroll-node-child > main > div > section > div.rezqw3Q4OEPB1m4rmwfw > div.contentSpacing > div.ShMHCGsT93epRGdxJp2w.Ss6hr6HYpN4wjHJ9GHmi > div.JUa6JJNj7R_Y3i4P8YUX 
    #print('Number of Songs: ', len(song_elements))
    #test_element = soup.select('.main .JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2) > div:nth-child(1)')
    test_element = soup.select('#main .JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2) > div:nth-child(1)')
    
    # problem loading the whole site as the loaded frame doesn't go further than 1008px
    #main .JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2) > div:nth-child(29) > div
    #main .JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2) > div:nth-child(34)
    #main .JUa6JJNj7R_Y3i4P8YUX > div:nth-child(2) > div:nth-child(44)


    print(test_element)
    #print(len(soup.find_all(my_tag_selector)))
    for song_element in song_elements:
        song_content = song_element.contents[0].contents[0]
        print(song_content)

    print('Number of Songs: ', len(song_elements))
    artist_element = soup.find('span', {"class": "Type__TypeElement-sc-goli3j-0 dvSMET rq2VQ5mb9SDAFWbBIUIn standalone-ellipsis-one-line"})
    artist_content = artist_element.contents[0].contents[0]
    driver.quit()



URL = "https://open.spotify.com/playlist/1QzMPmOyuxetr3Mbw4vBb8"
#URL = 'https://quotes.toscrape.com/'
#URL = 'https://www.youtube.com/watch?v=j0z4FweCy4M'
#URL = 'https://angular.io/tutorial'
#selenium_soup(URL)
selenium_setup(URL)


