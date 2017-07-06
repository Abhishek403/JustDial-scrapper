# JustDial-scrapper
Given input first level category, file containing cities. This will scrap relevant listings.

1) cities.py: this python script will scrap all the cities in which Just dial operates.
2) scrapper.py: The main script to scrap listings data such as Name, Phone, categories etc
                It will take an input file having columna name as city.
                If some error occurred, and you want to retry from that point, then fill the previous category, previous city                 and crawled pages so far field in console. The relevant data will be printed, when a page is crawled.
