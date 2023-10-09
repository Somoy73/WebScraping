import os
import multiprocessing
import csv
import time
import itertools
import logging
import datetime
import concurrent.futures
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver import EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def get_websites_from_csv(file_path, S, N):
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return [row["Domain"] for _, row in zip(range(S + N), reader)][S:]


def get_tag_counts(url: str, soup):
    failed_csv_path = "./output2/failed_websites.csv"

    try:
        # Remove script and style elements
        tags_to_remove = [
            "script",
            "style",
            "link",
            "meta",
            "head",
            "title",
            "noscript",
            "b",
            "strong",
            "i",
            "em",
            "mark",
            "small",
            "del",
            "ins",
            "sub",
            "sup",
            "span",
            "blockquote",
            "cite",
            "q",
            "abbr",
            "acronym",
            "dfn",
            "big",
            "tt",
            "code",
            "samp",
            "kbd",
            "var",
            "pre",
            "listing",
            "plaintext",
            "xmp",
            "strike",
            "s",
        ]
        for script in soup(tags_to_remove):
            script.extract()

        # Remove all child tags inside svg tags
        for svg in soup("svg"):
            for child in svg.find_all(True):
                child.decompose()

        for table_child in soup("table"):
            for child in table_child.find_all(True):
                child.decompose()

        tag_dict = {"Website": url}
        for tag in soup.find_all(True):
            if tag.name not in tag_dict:
                tag_dict[tag.name] = 1
            else:
                tag_dict[tag.name] += 1

        logging.info(f"Successfully scraped {url}")
        # print(f"Successfully scraped {url}")
        return tag_dict
    except Exception as e:
        logging.info(f"Failed to scrape {url}: {str(e)}")
        # print(f"Failed to scrape {url}: {str(e)}")
        save_failed_sites_to_csv(url, failed_csv_path)
        return {}


def save_to_csv(website_dicts, file_path):
    # print(website_dicts)
    header = sorted(set(key for dic in website_dicts for key in dic.keys()))
    with open(file_path, "w", encoding="utf-8", newline="") as output_file:
        dict_writer = csv.DictWriter(
            output_file, fieldnames=header, extrasaction="ignore"
        )
        dict_writer.writeheader()
        dict_writer.writerows(website_dicts)


def save_failed_sites_to_csv(site, file_path):
    with open(file_path, "a+", encoding="utf-8") as txt_file:
        txt_file.write(f"{site}\n")


def get_index(urls, url):
    try:
        return urls.index(url) + 1
    except ValueError:
        return 0


def load_from_csv(file_path, urls):
    website_dicts = []
    with open(file_path, "r", newline="") as csvfile:
        last_scraped = 0
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip the header
        for row in reader:
            website_dict = {header[i]: value for i, value in enumerate(row)}
            website_dicts.append(website_dict)
            # find the last scraped website by matching with the urls list
            last_scraped = max(last_scraped, get_index(urls, website_dict["Website"]))
        return website_dicts, last_scraped


def save_website_scraped_count_to_txt(websites_scraped_count):
    with open("web_scraped.txt", "w", encoding="utf-8") as file:
        file.writelines(str(websites_scraped_count) + "\n")
        logging.info("Successful scrapes:", websites_scraped_count)
    print("Successful scrapes:", websites_scraped_count)


def get_last_website_scraped_count_from_txt():
    lines = []
    with open("web_scraped.txt", "r") as file:
        lines = file.readlines()

    if len(lines) != 0:
        return int(lines[-1])
    else:
        return 0


def get_driver_options(browser_name, is_headless):
    if browser_name == "chrome":
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-in-process-stack-traces")
        options.add_extension("./ublock.crx")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if is_headless:
            options.add_argument("--headless")
        return options
    elif browser_name == "firefox":
        # profile = webdriver.FirefoxProfile()
        # profile.add_extension("./ublock.xpi")
        options = FirefoxOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.set_preference("javascript.enabled", False)
        if is_headless:
            options.add_argument("--headless")
        return options
    elif browser_name == "edge":
        options = EdgeOptions()
        if is_headless:
            options.add_argument("--headless")
        return options
    else:
        raise Exception("Invalid browser name")


def get_driver(browser_name, is_headless):
    if browser_name == "chrome":
        return webdriver.Chrome(options=get_driver_options(browser_name, is_headless))
    elif browser_name == "firefox":
        options = get_driver_options(browser_name, is_headless)
        driver = webdriver.Firefox(options=options)
        driver.install_addon("./ublock.xpi", temporary=True)
        return driver
    elif browser_name == "edge":
        return webdriver.Edge(options=get_driver_options(browser_name, is_headless))
    else:
        raise Exception("Invalid browser name")


def worker(url):
    DRIVER_NAME = "chrome"  # Adjust based on the browser you want to use
    try:
        driver = get_driver(DRIVER_NAME, is_headless=True)
        driver.set_page_load_timeout(30)
        driver.get(f"http://{url}")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        time.sleep(1)
        driver.quit()
        tag_dict = get_tag_counts(url, soup)
        return tag_dict
    except Exception as e:
        logging.error(
            f"Failed to scrape {url}, isssue stemmed from worker function {str(e)}"
        )
        # print(f"Failed to scrape {url}, isssue stemmed from worker function")
        save_failed_sites_to_csv(url, "failed_sites.csv")
        return {}


def chunked_iterable(iterable, chunk_size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, chunk_size))
        if not chunk:
            return
        yield chunk


def main():
    # Set up the logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        handlers=[logging.FileHandler("./webscraping.log"), logging.StreamHandler()],
    )

    websites_scraped = get_last_website_scraped_count_from_txt()
    S = 0  # Starting index (0-indexed, -1 to continue from last scrape)
    N = 150000  # Number of websites to scrape
    K = 16  # Save to CSV after every K websites
    CHUNK_SIZE = 4  # Adjust based on your system's capabilities
    file_path = "./majestic_million.csv"
    csv_output_path = f'./output2/output_{S + 1 if S != -1 else ""}.csv'
    total_urls = get_websites_from_csv(file_path, 0, 1000000)

    if os.path.exists(csv_output_path):
        website_dicts, last_scraped = load_from_csv(csv_output_path, total_urls)
        S = last_scraped
    else:
        website_dicts = []

    urls = total_urls[S : S + N]
    del total_urls

    logging.info(f"Starting from S:{str(S)}")
    # print("Starting from S:", S)

    for chunk in chunked_iterable(urls, CHUNK_SIZE):
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        ) as executor:
            for tag_dict in executor.map(worker, chunk):
                if tag_dict is not None:
                    website_dicts.append(tag_dict)
                    websites_scraped += 1
                if len(website_dicts) % K == 0:
                    save_to_csv(website_dicts, csv_output_path)
                    save_website_scraped_count_to_txt(websites_scraped)
                    logging.info(
                        f"Saved to CSV. Total Websites Scraped: {websites_scraped}"
                    )

    save_to_csv(website_dicts, csv_output_path)  # Save the final result
    save_website_scraped_count_to_txt(websites_scraped)

    return


if __name__ == "__main__":
    main()
