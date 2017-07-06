from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv
import threading
from thread import start_new_thread

#driver = None

filename = 'cities_list.csv'
headers = {'Cities'}


def wait(web_opening_time=3):
    time.sleep(web_opening_time)

#
# def web_driver_load():
#     global driver
#     driver = webdriver.Chrome()


# def web_driver_quit():
#     driver.quit()
#
#
# def open_web_page(url):
#     driver.get(url)
#     wait(2)


def write_headers():
    with open(filename, 'w+') as out_file:
        writer = csv.DictWriter(out_file, delimiter=',', fieldnames=headers)
        writer.writeheader()


def write_to_csv(dat):
    d = dict()
    d['cities'] = dat
    with open(filename, 'a+') as csv_file:
        writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=headers)
        writer.writerow(d)


def fetch_cities_th():
    for i in range(0, 9):
        p = 97 + 3*i
        t = threading.Thread(target=fetch_cities, args=(p,))
        # start_new_thread(fetch_cities, (97 + i * 3,))
        #t.daemon = True
        t.start()
        #wait()
        # t = threading.Thread(target=fetch_cities(97 + i * 3))
        # #threads.append(t)
        # t.start()


def fetch_cities(num):
    driver = webdriver.Chrome()
    driver.get(url='https://www.justdial.com/')
    wait(10)
    web_obj = driver.find_element_by_xpath("//input[@id='city']")
    for j in range(0, 15):
        web_obj.send_keys(Keys.BACK_SPACE)
    for one in range(num, num + 3):
        for two in range(97, 123):
            for three in range(97, 123):
                for j in range(0, 3):
                    web_obj.send_keys(Keys.BACK_SPACE)
                prefix = chr(one) + chr(two) + chr(three)
                web_obj.send_keys(prefix)
                wait(1)
                cities_web_obj = driver.find_elements_by_xpath("//span[@class='city-drop dn']/ul/li")
                for i in range(0, len(cities_web_obj)):
                    current_city = cities_web_obj[i].get_attribute('id')
                    if str(current_city).lower().startswith(prefix.lower()):
                        write_to_csv(str(current_city))
                        print (str(current_city))
    driver.quit()

if __name__ == "__main__":
    write_headers()
    fetch_cities_th()
    #web_driver_quit()
