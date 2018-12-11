import geotext
import requests
import Constants
import re
from geopy.geocoders import Nominatim
import spacy
import json


class DataCollector(object):

    @staticmethod
    def collect_data_from_source(url):
        final_json = {"type": "FeatureCollection",
                      "features": []}
        first_book_num = 844
        books_dict = {}
        for curr_book_num in range(first_book_num, 1000):
            txt_url = url + str(curr_book_num) + '/pg' + str(curr_book_num) + '.txt'
            image_url = Constants.img_base_url + str(curr_book_num) + '/' + str(curr_book_num) + '-h' + Constants.img_sec_url

            try:
                content = requests.get(txt_url, allow_redirects=True).text
            except Exception as e:
                print(e)
                continue

            def find_specific_word(split_by_word, inner_split):
                word_to_find = ''
                lines = content.split('\n')
                for line in lines:
                    if split_by_word in line:
                        inner_lines = line.split(inner_split)
                        word_to_find = inner_lines[1].replace('\r', '')
                        break
                return word_to_find

            geolocator = Nominatim(user_agent="specify_your_app_name_here")

            def get_address_coordinates(address: str):
                try:
                    # TODO: check importance inside raw parameter is bigger then some threshold for accuracy
                    location = geolocator.geocode(address)
                    return [location.latitude, location.longitude]
                except Exception as e:
                    return -1

            author = find_specific_word('Author', ': ')
            title = find_specific_word('Title', ': ')
            title_for_scarpping = title.replace(' ', '+')
            author_for_scrapping = author.replace(' ', '+')
            # get book data if exists
            try:
                book_json_data = requests.get(Constants.open_library_base_url + title_for_scarpping + '+by+' + author_for_scrapping, allow_redirects=True).text
            except Exception as e:
                print(e)
                continue
            book_dict_data = json.loads(book_json_data)
            release_date = book_dict_data['docs'][0]['first_publish_year']
            # reg_exp = '[A-z]*\s\d+\s[A-Z][a-z]+\s[A-z]*\d*[A-z]*'
            # addresses = re.findall(reg_exp, content)
            geo = geotext.GeoText(content)
            nlp = spacy.load('en_core_web_sm')
            doc = nlp(content)
            nlp_geo_results = []
            for ent in doc.ents:
                if ent.label_ == 'GPE':
                    nlp_geo_results.append(ent.text)
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
            # used_countries = set()
            # country_city_pairs = []
            # for city_tup in cities_idx:
            #     city_name = city_tup[0]
            #     city_idx = city_tup[1]
            #     chosen_country_tup = None
            #     for country_tup in country_idx:
            #         if country_tup[1] < city_idx and(chosen_country_tup is None or country_tup[1] > chosen_country_tup[1]):
            #             chosen_country_tup = country_tup
            #     if chosen_country_tup is not None:
            #         used_countries.add(chosen_country_tup[0])
            #         country_city_pairs.append((chosen_country_tup[0], city_name))

            country_city_sets = set(nlp_geo_results)
            coord_dict = {}
            for country_city_tup in country_city_sets:
                coords = get_address_coordinates(country_city_tup)
                if coords != -1:
                    coord_dict[country_city_tup] = coords

            # create json format
            # TODO: fix locations list with duplicates
            final_json['features'].append(convert_data_to_json(id=curr_book_num,
                                                               location_coord_list=list(coord_dict.values()),
                                                               title=title,
                                                               author=author, books_data_dict=book_dict_data,
                                                               cover_url=image_url))

        with open(Constants.json_file_path, 'w') as fp:
            json.dump(final_json, fp)


def convert_data_to_json(id, location_coord_list, title, author, books_data_dict, cover_url):
    json_dict = {'type': 'Feature',
                 'properties': {'id': id,
                                'title': title,
                                'cover_url': cover_url,
                                'genre': 'None',
                                'release_year': books_data_dict['docs'][0]['first_publish_year'],
                                'lang': books_data_dict['docs'][0]['language'],
                                'author': author,
                                'illustrator': None,
                                'category': None,
                                'line': location_coord_list
                                },
                 'geometry': {'type': "MultiPoint",
                              "coordinates": location_coord_list
                              }
                 }
    return json_dict


def main():
    DataCollector.collect_data_from_source(Constants.main_url)


if __name__ == '__main__':
    main()