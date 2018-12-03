import geotext
import requests
import Constants
from newspaper import fulltext
import pyap
import re
import googlemaps


class DataCollector(object):
    @staticmethod
    def collect_data_from_source(url):
        first_book_num = 844
        gmaps = googlemaps.Client(key='AIzaSyDaNo8TFfI8cdfDHxGlX_t0HOHxNq3wkPY')
        books_dict = {}

        for curr_book_num in range(first_book_num, 1000):
            txt_url = url + str(curr_book_num) + '/pg' + str(curr_book_num) + '.txt'
            image_url = Constants.img_base_url + str(curr_book_num) + '/' + str(curr_book_num) + '-h' + Constants.img_sec_url

            try:
                content = requests.get(txt_url, allow_redirects=True).text
            except Exception as e:
                print(e)
                continue

            # TODO: add author title and date parsing

            reg_exp = '[A-z]*\s\d+\s[A-Z][a-z]+\s[A-z]*'
            addresses = re.findall(reg_exp, content)
            geo = geotext.GeoText(content)
            countries = set(geo.countries)
            cities = set(geo.cities)
            content = content.replace('\r', '')
            content = content.replace('\n', '')

            splitted_text = content.split(' ')

            # find countries indexes in text
            country_idx = []
            for country in countries:
                splitted_country = country.split(' ')
                for inner_word in splitted_country:
                    indexes = [i for i, x in enumerate(splitted_text) if x == inner_word]
                    for idx in indexes:
                        country_idx.append((country, idx))
            sorted(country_idx, key=lambda x: x[1])

            # find cities indexes in text
            cities_idx = []
            for city in cities:
                splitted_city = city.split(' ')
                for inner_word in splitted_city:
                    indexes = [i for i, x in enumerate(splitted_text) if x == inner_word]
                    for idx in indexes:
                        cities_idx.append((city, idx))
            sorted(cities_idx, key=lambda x: x[1])

            # create city country tuples
            used_countries = set()
            city_country_pairs = []
            for city_tup in cities_idx:
                city_name = city_tup[0]
                city_idx = city_tup[1]
                chosen_country_tup = None
                for country_tup in country_idx:
                    if country_tup[1] < city_idx and(chosen_country_tup is None or country_tup[1] > chosen_country_tup[1]):
                        chosen_country_tup = country_tup
                if chosen_country_tup is not None:
                    used_countries.add(chosen_country_tup[0])
                    city_country_pairs.append((chosen_country_tup[0], city_name))

            print(countries.difference(used_countries))

            # Geocoding an address
            # geocode_result = gmaps.geocode('London')

            print('regualr expressions:')
            print(addresses)
            print('countries:')
            print(countries)
            print('cities:')
            print(cities)


def main():
    DataCollector.collect_data_from_source(Constants.main_url)


if __name__ == '__main__':
    main()