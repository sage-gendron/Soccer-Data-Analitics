# scraper.py
"""
author: Sage Gendron


Some other options to scrape:
- https://burmancoffee.com/green-coffee-beans/
- https://happymugcoffee.com/collections/green-coffee
- https://www.roastmasters.com/green_coffee.html
- https://royalcoffee.com/offerings/?pa_position=spot
- https://millcityroasters.com/product-category/green-coffee/
"""
from Scraper import Scraper
from selenium.webdriver.common.by import By
import time


class SMScraper(Scraper):
    def __init__(self, data_loc, site, url):
        super().__init__(data_loc, site, url)

    def insert_data(self, link, title, description, oa_score, process, cupping_notes, cupping_csv, flavor_csv):

        if title not in self.data:
            self.data[title] = {
                'site': self.site,
                'link': link,
                'description': description,
                'overall_score': oa_score,
                'process': process,
                'cupping_notes': cupping_notes
            }

            if cupping_csv:
                cupping_doc = {}
                for cat in cupping_csv.split(','):
                    cat_split = cat.split(':')
                    cupping_doc[cat_split[0]] = cat_split[1]
                self.data[title]['cupping'] = cupping_doc

            if flavor_csv:
                flavor_doc = {}
                for cat in flavor_csv.split(','):
                    cat_split = cat.split(':')
                    flavor_doc[cat_split[0]] = cat_split[1]
                self.data[title]['flavors'] = flavor_doc


if __name__ == '__main__':

    # current coffees as of 12/4/22
    url_current = 'https://www.sweetmarias.com/green-coffee.html?product_list_limit=all&sm_status=1'
    # archived coffees for reference as of 12/4/22
    url_archive = 'https://www.sweetmarias.com/green-coffee.html?product_list_limit=all&sm_status=2'

    scraper = SMScraper(
        data_loc='/Users/Sage/PycharmProjects/Data-Projects/Coffee FlavorsxOrigin/data/coffee_data.json',
        site='SM',
        url=url_current
    )

    for link in scraper.links:

        print(link)
        if not link.split('.')[-2][-4:].isdigit() or link in scraper.visited:
            continue

        time.sleep(3)

        scraper.scrape(link)
        scraper.wait(2)

        # look for the title and short description from the webpage, if not found, skip the page
        title = scraper.find_text(By.XPATH, '/html/body/div/main/div/div/div/div/div/h1/span')
        description = scraper.find_text(By.XPATH, '/html/body/div/main/div/div/div/div/div/div/p')
        print(title)

        if title is None or description is None:
            continue

        total_score = scraper.find_text(By.CLASS_NAME, 'score-value')

        cupping_notes = scraper.find_text(By.XPATH, '/html/body/div/main/div/div/div/div/div/div/div/div/div/div'
                                                    '/div/p')

        process_method = scraper.find_text(By.XPATH, '/html/body/div/main/div/div/div/div/div/div/div/div/div/div'
                                                     '/div/ul/li/span')

        charts = scraper.find_list(By.CLASS_NAME, 'forix-chartjs')

        cupping = flavor = None
        if charts is not None:
            for chart in charts:
                if cupping and flavor:
                    break
                if chart.get_attribute('data-chart-id') == 'cupping-chart':
                    cupping = chart.get_attribute('data-chart-value')
                elif chart.get_attribute('data-chart-id') == 'flavor-chart':
                    flavor = chart.get_attribute('data-chart-value')

        scraper.insert_data(link, title, description, total_score, process_method, cupping_notes, cupping, flavor)

    scraper.stop_driver()

    scraper.save_data()