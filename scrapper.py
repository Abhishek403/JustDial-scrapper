from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from threading import Thread, local
import time
import csv
import concurrent.futures

# driver = None

executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
threshold = 100

local_data = local()
local_data.calls = 0
local_data.proxy = ''
local_data.file_name = ''
local_data.city = ''

previous_city = raw_input('Enter Previous City, If any: ')
previous_categories = raw_input('Enter Previous Categories, If any: ')
previous_page = raw_input('Enter Previous Page, If any: ')

filename = 'out3.csv'
headers = {'categories', 'name', 'phone', 'address', 'ratings', 'votes', 'year'}
current_cat = raw_input('Enter category: ')
city_file_name = raw_input('Enter city_file: ')


cities = {  # 'https://www.justdial.com/Ahmedabad',
    'https://www.justdial.com/Bangalore'
    # 'https://www.justdial.com/Chandigarh',
    # 'https://www.justdial.com/Chennai',
    # 'https://www.justdial.com/Coimbatore',
    # 'https://www.justdial.com/Delhi',
    # 'https://www.justdial.com/Goa',
    # 'https://www.justdial.com/Gurgaon',
    # 'https://www.justdial.com/Hyderabad',
    # 'https://www.justdial.com/Indore',
    # 'https://www.justdial.com/Jaipur',
    # 'https://www.justdial.com/Kolkata',
    # 'https://www.justdial.com/Mumbai',
    # 'https://www.justdial.com/Noida',
    # 'https://www.justdial.com/Pune'
}


def wait(web_opening_time=3):
    time.sleep(web_opening_time)


# def web_driver_load(dr):
#     global driver
#     driver = webdriver.Chrome()


def web_driver_quit(driver):
    driver.quit()


def open_web_page(url, driver):
    driver.get(url)
    local_data.calls = local_data.calls + 1
    wait(1)


def write_headers():
    with open(filename, 'w+') as out_file:
        writer = csv.DictWriter(out_file, delimiter=',', fieldnames=headers)
        writer.writeheader()


def write_to_csv(row):
    with open(filename, 'a+') as csv_file:
        writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=headers)
        writer.writerow(row)


def search_pages_crawl(categories, link, driver, page=1):
    # if page >= 2:
    #     return
    #change_proxy(driver, local_data.proxy, driver.current_url)
    print ('Crawled ' + str(page - 1) + ' pages for cagtegories: [' + categories + '], for city: ' + local_data.city)
    if local_data.calls > threshold:
        change_proxy(driver, local_data.proxy, driver.current_url)
        local_data.calls = 0
    wait(2)
    web_obj = driver.find_elements_by_xpath("//ul[@class='rsl col-md-12 padding0']/li")
    size = len(web_obj)
    if size == 0:
        print ('Crawled ' + str(page - 1) + ' pages for cagtegories: [' + categories + '], for city: ' + local_data.city)
        return
    wait(1)
    i = 0
    while i < size:
        try:
            web_obj[i].click()
            wait(2)
            local_data.calls = local_data.calls + 1
        except Exception:
            popup_ele = driver.find_elements_by_xpath("//section[@class='jpop dn']/section/span")
            if len(popup_ele) != 0:
                driver.switch_to_alert()
                driver.find_elements_by_xpath("//section[@class='jpop dn']/section/span")[-1].click()

            web_obj[i].click()
            local_data.calls = local_data.calls + 1
        # wait(1)

        # Scroll to top of page
        driver.execute_script("window.scrollTo(0, 0);")
        #wait(1)

        name = str(driver.find_element_by_xpath("//span[@class='fn']").text)
        address = str(driver.find_element_by_xpath("//span[@id='fulladdress']").text)
        rating = driver.find_elements_by_xpath("//span[@class='value-titles']")
        num_reviews = driver.find_elements_by_xpath("//span[@class='votes']")

        phone_element = driver.find_elements_by_xpath("//a[@class='tel']")
        year_of_establishment = ""
        year_of_establishment_obj = driver.find_elements_by_xpath("//div[@class='mreinfwpr']/ul")
        if len(year_of_establishment_obj) > 0:
            year_of_establishment = str(year_of_establishment_obj[-1].find_elements_by_xpath(".//li")[0].text)

        phone_set = set()
        phone_str = ''

        for j in range(0, len(phone_element)):
            if str(phone_element[j].text):
                if str(phone_element[j].text) not in phone_set:
                    phone_str = phone_str + ', ' + str(phone_element[j].text)
                    phone_set.add(str(phone_element[j].text))

        phone_set.clear()

        data_dict = dict()
        data_dict['categories'] = categories
        data_dict['name'] = name
        data_dict['address'] = address
        data_dict['phone'] = phone_str
        if len(rating) > 0:
            data_dict['ratings'] = str(rating[0].text)
        else:
            data_dict['ratings'] = ""
        if len(num_reviews) > 0:
            data_dict['votes'] = str(num_reviews[0].text)
        else:
            data_dict['votes'] = ""
        data_dict['year'] = year_of_establishment

        write_to_csv(data_dict)

        driver.back()
        wait(1)

        # scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait(1)

        web_obj = driver.find_elements_by_xpath("//ul[@class='rsl col-md-12 padding0']/li")
        size = len(web_obj)
        i = i + 1

    # next_ele = driver.find_elements_by_xpath("//a[@rel='next']")
    # if len(next_ele) != 0:
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     retry = 3
    #     while not next_ele[0].is_displayed() and retry > 0:
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #         wait(2)
    #         retry = retry - 1

    try:
        open_web_page(link + "/page-" + str(page + 1))
        search_pages_crawl(categories, link, driver, page + 1)
    except Exception, ex:
        print ('Unable to click next element for url: ' + driver.current_url + ', error: ' + str(ex))
        return


def select_categories(categories, driver, cat_selected=False, crawl_all_cat=False):
    to_loop = len(driver.find_elements_by_xpath("//span[@class='poplr-catgy col-xs-12']")) != 0
    current_url = driver.current_url
    if not to_loop:
        if len(previous_city) > 0:
            if local_data.city == previous_city and categories == previous_categories:
                open_web_page(current_url + '/page-' + str(int(previous_page) + 1), driver)
                search_pages_crawl(categories, current_url + '/page-' + str(int(previous_page) + 1), driver, int(previous_page) + 1)
                return
        search_pages_crawl(categories, current_url, driver, 1)
        return

    web_obj = driver.find_elements_by_xpath("//ul[@class='mm-listview']")[0].find_elements_by_xpath(".//li/a")
    if not cat_selected and not crawl_all_cat:
        for i in range(0, len(web_obj)):
            ct = str(web_obj[i].text)
            if ct.lower().replace(" ", "") == current_cat.lower().replace(" ", ""):
                web_obj[i].send_keys(Keys.RETURN)
                local_data.calls = local_data.calls + 1
                cat_selected = True
                select_categories(categories + ', ' + ct, driver, cat_selected=cat_selected,
                                  crawl_all_cat=crawl_all_cat)
                return
        print 'Unable to Find Given Category!'
        return

    for i in range(0, len(web_obj)):
        open_web_page(current_url, driver)
        web_obj = driver.find_elements_by_xpath("//ul[@class='mm-listview']")[0].find_elements_by_xpath(".//li/a")
        ct = str(web_obj[i].text)
        web_obj[i].send_keys(Keys.RETURN)
        local_data.calls = local_data.calls + 1
        select_categories(categories + ', ' + ct, driver, cat_selected=cat_selected, crawl_all_cat=crawl_all_cat)


def check_internet_connectivity(driver):
    open_web_page(url='https://www.justdial.com/', driver=driver)
    if len(driver.find_elements_by_xpath("//input[@id='city']")) == 0:
        return False
    return True


def change_proxy(driver, current_proxy, old_url):
    open_web_page(url='chrome-extension://pooljnboifbodgifngpppfklhifechoe/proxy.html', driver=driver)
    driver.find_element_by_xpath("//select[@id='country_id']").find_element_by_xpath(".//option[@value='IN']").click()
    wait(1)
    driver.find_element_by_xpath("//a[@id='search']").click()
    wait(1)
    proxy_lists = driver.find_elements_by_xpath("//a[@class='proxylist']")
    length = len(proxy_lists)
    proxy = ''
    for i in range(0, length):
        if str(proxy_lists[i].text) != local_data.proxy:
            proxy = str(proxy_lists[i].text)
            proxy_lists[i].click()
            wait(1)
            if check_internet_connectivity(driver):
                local_data.proxy = proxy
                open_web_page(old_url, driver)
                return
            open_web_page(url='chrome-extension://pooljnboifbodgifngpppfklhifechoe/proxy.html', driver=driver)
            driver.find_element_by_xpath("//select[@id='country_id']").find_element_by_xpath(
                ".//option[@value='IN']").click()
            wait(1)
            driver.find_element_by_xpath("//a[@id='search']").click()
            wait(1)
            proxy_lists = driver.find_elements_by_xpath("//a[@class='proxylist']")

    print ('Unable to set Proxy, retry after some time')
    raise ValueError('Unable to set Proxy, retry after some time')


def set_proxy(driver):
    open_web_page(url='chrome-extension://pooljnboifbodgifngpppfklhifechoe/proxy.html', driver=driver)
    driver.find_element_by_xpath("//select[@id='country_id']").find_element_by_xpath(".//option[@value='IN']").click()
    wait(1)
    driver.find_element_by_xpath("//a[@id='search']").click()
    wait(1)
    proxy_lists = driver.find_elements_by_xpath("//a[@class='proxylist']")
    lent = len(proxy_lists)
    proxy = ''
    for i in range(1, lent):
        proxy = str(proxy_lists[i].text)
        proxy_lists[i].click()
        wait(1)
        if check_internet_connectivity(driver):
            local_data.proxy = proxy
            return
        open_web_page(url='chrome-extension://pooljnboifbodgifngpppfklhifechoe/proxy.html', driver=driver)
        driver.find_element_by_xpath("//select[@id='country_id']").find_element_by_xpath(
            ".//option[@value='IN']").click()
        wait(1)
        driver.find_element_by_xpath("//a[@id='search']").click()
        wait(1)
        proxy_lists = driver.find_elements_by_xpath("//a[@class='proxylist']")

    print ('Unable to set Proxy, retry after some time')
    raise ValueError('Unable to set Proxy, retry after some time')


def start(city):
    write_headers()
    local_data.calls = 0
    local_data.proxy = ''
    local_data.city = city
    local_data.file_name = city + '-out.out'
    options = webdriver.ChromeOptions()
    options.add_extension('/Users/abhishekdas/Documents/JustDialScrap/src/1.5_0.crx')
    driver = webdriver.Chrome(chrome_options=options)
    set_proxy(driver)
    #open_web_page(url='https://www.justdial.com/', driver=driver)
    web_obj = driver.find_element_by_xpath("//input[@id='city']")
    for j in range(0, 15):
        web_obj.send_keys(Keys.BACK_SPACE)

    web_obj.send_keys(city)
    wait(2)
    driver.find_elements_by_xpath("//span[@class='city-drop dn']/ul/li/a")[0].click()

    web_obj = driver.find_element_by_xpath("//a[@id='ContextualHotkey_6']")
    web_obj.send_keys(Keys.RETURN)
    wait(1)

    # Apparels-Clothing-FootWear
    driver.find_elements_by_xpath("//ul[@class='mm-listview mm-lstex']/li/a")[9].send_keys(Keys.RETURN)

    # Input Category
    categories = ''
    if len(current_cat) > 0:
        select_categories(categories, driver)
    else:
        select_categories(categories, driver, crawl_all_cat=True)

    web_driver_quit(driver)


if __name__ == "__main__":
    # pool = Pool(5)
    futures = []
    with open(city_file_name, 'rb') as csvFile:
        reader = csv.DictReader(csvFile, delimiter=',')
        for r in reader:
            start(r['city'])
            #executor.submit(start, (str(r['city']),))

    #executor.shutdown(True)
            # for future in concurrent.futures.as_completed(futures):



            # for url in cities:
            #
            #     open_web_page(url=url)
            #     web_obj = driver.find_element_by_xpath("//a[@id='ContextualHotkey_6']")
            #     web_obj.send_keys(Keys.RETURN)
            #     wait(1)
            #
            #     # Apparels-Clothing-FootWear
            #     driver.find_elements_by_xpath("//ul[@class='mm-listview mm-lstex']/li/a")[9].send_keys(Keys.RETURN)
            #
            #     # Input Category
            #
            #
            #     categories = ''
            #     select_categories(categories)

            # to_loop = len(driver.find_elements_by_xpath("//span[@class='poplr-catgy col-xs-12']")) != 0
            #
            # if to_loop:
            #     web_obj = driver.find_elements_by_xpath("//ul[@class='mm-listview']")[0].find_elements_by_xpath(".//li/a")
            #     for i in range(0, len(web_obj)):
            #         inner_web_obj = web_obj.find_elements_by_xpath(".//li/a")
            #         categories.append()
