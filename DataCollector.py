import geotext
import requests
import Constants
from geopy.geocoders import Nominatim
import spacy
import json
import time


class DataCollector(object):

    @staticmethod
    def collect_data_from_source(url):
        final_json = {"type": "FeatureCollection",
                      "features": []}

        first_book_num = 858
        try:
            with open(Constants.json_file_path, "r") as read_file:
                final_json = json.load(read_file)
        except Exception as e:
            final_json = {'features': []}

        for curr_book_num in range(first_book_num, 859):

            if curr_book_num in final_json.keys():
                continue

            print("started fetching book number: " + str(curr_book_num))
            starting_time = time.time()
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
                    return [location.longitude,location.latitude]
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

            # split content main text
            main_content = content.split('***')[2]
            main_content = main_content.replace('\r', ' ')
            main_content = main_content.replace('\n', ' ')

            new_main = main_content
            first_run = True
            while new_main != main_content or first_run:
                first_run = False
                main_content = new_main
                new_main = main_content.replace('  ', ' ')

            book_dict_data = json.loads(book_json_data)
            geo = geotext.GeoText(main_content)
            nlp = spacy.load('en_core_web_sm')
            doc = nlp(main_content)
            nlp_geo_results = []
            for ent in doc.ents:
                if ent.label_ == 'GPE' and ' ' not in ent.text:
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

            finish_time = time.time()
            print("finished fetching, took: " + str((finish_time - starting_time)))
        with open(Constants.json_file_path, 'w') as fp:
            json.dump(final_json, fp)
            print("saved json file.")


def convert_data_to_json(id, location_coord_list, title, author, books_data_dict, cover_url):
    try:
        cover_value = 'https://covers.openlibrary.org/w/id/'+str(books_data_dict['docs'][0]['cover_i'])+'-M.jpg'
    except KeyError as ke:
        print("Error occurred: " + str(ke))
        cover_value = "default_cover.png"
    json_dict = {'type': 'Feature',
                 'properties': {'id': id,
                                'title': title,
                                'cover_url': cover_value,
                                'genre': 'None',
                                'release_year': str(books_data_dict['docs'][0]['first_publish_year']),
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
