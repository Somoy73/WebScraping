# WebScraping
A collection of Scripts and Notebooks that I used to scrape different websites for fun errm Educational purposes. Some notebooks may contain EDA (Explanatory Data Analysis) and other things as well.

Contents:

**1.1: Majestic-Million**

In this script - the code reads a list of the websites from the majestic million dataset [https://majestic.com/reports/majestic-million] and stores all the tags present in the websites' landing pages. The script can be further enhanced to read additional data as well.

The key implementation of this script is that - scraping 100s of thousands website can take time. However, with efficient multiprocessing the time it takes can be decreased significantly. That's exactly what the script does.

*Libraries Used for Scraping: Selenium, BeautifulSoup4*
