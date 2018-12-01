import geotext
import requests
import Constants
from newspaper import fulltext
import pyap
import re


class DataCollector(object):
    @staticmethod
    def collect_data_from_source(url):
        first_book_num = 844
        for curr_book_num in range(first_book_num, 1000):
            txt_url = url + str(curr_book_num) + '/pg' + str(curr_book_num) + '.txt'
            try:
                content = requests.get(txt_url, allow_redirects=True).text
            except Exception as e:
                print(e)
                continue
            addresses = pyap.parse(content, country='UK')
            print(addresses)


def main():
    DataCollector.collect_data_from_source(Constants.main_url)


if __name__ == '__main__':
    main()