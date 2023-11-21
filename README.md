# WebScraping
A collection of Scripts and Notebooks that I used to scrape different websites for fun errm Educational purposes. Some notebooks may contain EDA (Explanatory Data Analysis) and other things as well.

Contents:

**1.1: [Majestic-Million with Multi-Processing](majestic-million-multiprocess)**

In this script - the code reads a list of the websites from the [majestic million dataset](https://majestic.com/reports/majestic-million) and stores all the tags present in the websites' landing pages. The script can be further enhanced to read additional data as well.

The key implementation of this script is that - scraping 100s of thousands website can take time. However, with efficient multiprocessing the time it takes can be decreased significantly. That's exactly what the script does.

*Libraries Used for Scraping: Selenium, BeautifulSoup4*

**1.2: [Flight Scrapper and ED](flight-scrapper)**

In this notebook - I utilized selenium-stealth and some small tricks to prevent bot detection in order to scrape 3 famous flight websites. i.e., Momondo, Kayak and Google Flights. 


The notebook contains demo of scripts to toggle and trigger different Event actions within the page using the webdriver in an iterative way. This can be a good material to practice and learn how to repetitively click buttons and wait for actions within the webpage using Selenium.

*Libraries Used for Scraping: Selenium-Stealth, Selenium, and etc.*

Additional EDA has been done within the notebook to visualize the data and suggest the user best flights to choose from a given option and criteria.
[Demo EDA of the Scraped Data](https://github.com/Somoy73/WebScraping/blob/main/flight-scrapper/eda_1.png)

*P.S: This code is meant for educational purposes only*

