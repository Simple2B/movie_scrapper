import os
from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions
# from fake_useragent import UserAgent
import random
import time
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from bs4 import BeautifulSoup
from app.config import settings


# chrome_options = Options()

'''chrome_options.add_argument('--headless')


chrome_options.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2})
chrome_options.add_experimental_option(
    "excludeSwitches", ["enable-automation"])
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

chrome_options.add_argument("--disable-setuid-sandbox")
  # this
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--dns-prefetch-disable")
chrome_options.add_argument("--shm-size=1g")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")'''


'''userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "\
            "(KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"

chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument('log-level=3')
chrome_options.add_argument('user-agent={}'.format(userAgent))
'''


def get_pages(page):
    '''
    Scrapper function. Launches Selenium webdriver, scrapes website html and writes html to file.
    '''
    from selenium.webdriver.firefox.options import Options

    # driver = webdriver.Chrome(options=chrome_options, executable_path="/home/linp/simple2b/movie_scrap/chromedriver")
    # driver.maximize_window()
    # driver.implicitly_wait(2)
    # driver.set_page_load_timeout(30)

    start_time = time.time()
    print(">>>>>>>>>>>>>> Scrapper start time: ",start_time)

    ############################################################################################
    # here load strategy may be chosen. Default is standard strategy. It is more like human.
    options = Options()
    '''options.page_load_strategy = "eager"'''

    #making random user agent for webdriver broswer
    #ua = UserAgent()
    #userAgent = ua.random
    #print(userAgent)
    #options.add_argument(f'user-agent={userAgent}')

    #charging profile. Programm is using your own browser profile. If trying to use flase
    # profile - CAPTCHA will easily notice a bot.
    #"/home/linp/.mozilla/firefox/xjlukkfp.default-release" - firefox profile path
    # with just "()" it also use your default profile
    
    #profile = webdriver.FirefoxProfile()
    #print(webdriver.FirefoxProfile())
    PROXY_HOST = "51.05.23.594"
    PROXY_PORT = "6142"
    #profile.set_preference("network.proxy.type", 1)
    #profile.set_preference("network.proxy.http", PROXY_HOST)
    #profile.set_preference("network.proxy.http_port", int(PROXY_PORT))
    #profile.set_preference("dom.webdriver.enabled", False)
    #profile.set_preference('useAutomationExtension', False)
    #options.add_argument('--no-sandbox')
    #options.add_argument('--disable-dev-shm-usage')
    #options.add_argument('--disable-infobars')
    #profile.update_preferences()
	
    #launching webdriver browserprint(os.path.abspath("text_files/Knowncyberlockers.txt"))
    driver = webdriver.Firefox(options=options, executable_path = os.path.abspath("drivers/geckodriver"))
    driver.maximize_window()
    driver.implicitly_wait(5)
    ############################################################################################

    f = open("movies.html", "w")
    time.sleep(random.uniform(1, 2))
    print("--- %s seconds ---" % (time.time() - start_time))
    driver.get(page)
    #driver.implicitly_wait(5)
    time.sleep(random.uniform(2, 3))
    print("--- %s seconds ---" % (time.time() - start_time))
    time.sleep(random.uniform(6, 7))
    
    #elem = driver.find_element_by_xpath("//*")
    #outer_html = elem.get_attribute("outerHTML")

    #ele = driver.find_element_by_xpath("//script[@type = 'text/javascript']")
    #outer_html = ele.get_attribute("innerHTML")

    #WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.TAG_NAME, "script")))
    #script = driver.find_element_by_tag_name('script')
    #outer_html = script.get_attribute("outerHTML")

    '''try:
        body = driver.find_element_by_xpath('/html/body')
        body.click()
        body.send_keys(Keys.PAGE_DOWN)
    except:
        body = driver.find_element_by_css_selector('body')
        body.click()
        body.send_keys(Keys.PAGE_DOWN)
        
    ActionChains(driver).move_to_element(body).perform()
    '''
    #outer_html = driver.execute_script("document.readyState;")
    outer_html = driver.execute_script("return document.documentElement.outerHTML;")
    #inner_html = driver.execute_script("return document.documentElement.innerHTML;")
    #xpath_html = driver.find_elements_by_xpath("//*")
    #outer_html = BeautifulSoup(driver.page_source)
    #outer_html = html.body.main.find('script').prettify()


    #print(f'------------------------------------{i}------------------------------------------')
    f.write(str(outer_html))
    f.close()

    print("Done.")
    print(">>>>>>>>>>>>>> Scrapper finished in: ", time.time() - start_time)
    driver.quit()


def scrapper(url: str):
    from selenium.webdriver.chrome.options import Options

    start_time = time.time()
    print(">>>>>>>>>>>>>> Scrapper start time: ", start_time)
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-infobars')
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(options=options, executable_path=os.path.abspath("drivers/chromedriver"))
    driver.set_page_load_timeout(20)
    time.sleep(random.uniform(1, 2))
    try:
        driver.get(url)
        time.sleep(random.uniform(7, 9))
        #WebDriverWait(driver, timeout=600).until(expected_conditions.text_to_be_present_in_element((By.TAG_NAME, "script"), "fstrea"))
        #generated_html = driver.page_source
        #soup = BeautifulSoup(generated_html, "html.parser")
        outer_html = driver.execute_script("return document.documentElement.outerHTML;")
        #inner_html = driver.execute_script("return document.documentElement.innerHTML;")
        f = open(os.path.join(settings.BASE_DIR, "scrapper/text_files/")+"movies.html", "w")
        f.write(str(outer_html))
        f.close()
    except:
        print(f"Error ocured when scrapping {url}\n")
        print(">>>>>>>>>>>>>> Scrapper finished in: ", time.time() - start_time)
        return False


    '''if company == "csx":
        links = soup.find_all("a", class_="module_link")
        while len(links) < 53:
            driver.get(url)
            generated_html = driver.page_source
            soup = BeautifulSoup(generated_html, "html.parser")
            links = soup.find_all("a", class_="module_link")
            sleep(1)'''

    print("Done.")
    print(">>>>>>>>>>>>>> Scrapper finished in: ", time.time() - start_time)
    driver.quit()
    return True


if __name__ == "__main__":
    '''f = open("movies_links.txt", "r")
    read_lockers = f.read().splitlines()
    f.close()'''
    url = "https://prmovies.com/american-siege-2021-Watch-online-on-prmovies/"
    scrapper(url)
    # get_pages(page)
