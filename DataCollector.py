import requests
import Constants
from geopy.geocoders import Nominatim
import spacy
import json
import time
from DBInit import DBInit
from DBHandler import DBHandler
import random
from collections import Counter
from geopy.exc import GeocoderTimedOut
from geopy.extra.rate_limiter import RateLimiter


COVER_IDS = set()
MAX_CORD_ADDITION = 0.003
counter_list = []
MAX_TIME_FOR_LOC_RESPONSE = 600


class DataCollector(object):

    @staticmethod
    def find_specific_word(split_by_word, inner_split, content):
        word_to_find = ''
        lines = content.split('\n')
        for line in lines:
            if split_by_word in line:
                inner_lines = line.split(inner_split)
                word_to_find = inner_lines[1].replace('\r', '')
                break
        return word_to_find

    @staticmethod
    def get_address_coordinates(address: str):
        geolocator = Nominatim(user_agent="hi_try_things")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2)

        try:
            location = geocode(address, timeout=MAX_TIME_FOR_LOC_RESPONSE)
        except GeocoderTimedOut as e:
            print("Error: geocode failed with timeout error on input" + str(address))
            return -1
        if location is None:
            return -1

        curr_importance = location.raw['importance']

        if curr_importance > Constants.importance_threshold and address not in Constants.black_list:
            return [location.longitude, location.latitude]
        else:
            return -1

    @staticmethod
    def run_nlp_engine(content):
        nlp = spacy.load('en_core_web_sm')
        try:
            doc = nlp(content)
        except ValueError as ve:
            print(ve)
            return None
        nlp_geo_results = []
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                nlp_geo_results.append(ent.text)
        return nlp_geo_results

    @staticmethod
    def create_json_from_db(db_handler, json_path):
        all_books = db_handler.get_all_books()
        base_dict = {"type": "FeatureCollection",
                     "features": []}

        for row in all_books:
            books_dict = {'type': 'Feature',
                          'properties': {'id': int(row[0]),
                                         'title': row[1],
                                         'cover_url': row[2],
                                         'release_year': row[3],
                                         'lang': row[4],
                                         'author': row[5],
                                         'author_key': row[6],
                                         'illustrator': row[7],
                                         'category': row[8],
                                         'line': row[9],
                                         },
                          'geometry': {'type': "MultiPoint",
                                       "coordinates": row[9]
                                       }
                          }

            base_dict["features"].append(books_dict)
        with open(json_path, 'w') as fp:
            json.dump(base_dict, fp)
            print("saved json file.")

    @staticmethod
    def collect_data_from_source(url, db_handler):

        try:
            with open(Constants.json_file_path, "r") as read_file:
                if not Constants.initialize_json:
                    final_json = json.load(read_file)
                else:
                    final_json = {"type": "FeatureCollection",
                                  "features": []}
        except Exception as e:
            final_json = {"type": "FeatureCollection",
                          "features": []}

        db_curr_idx = [tup[0] for tup in db_handler.get_all_ids()]

        for curr_book_num in range(Constants.lower_bound, Constants.upper_bound):

            if str(curr_book_num) in db_curr_idx:
                continue

            print("started fetching book number: " + str(curr_book_num))
            starting_time = time.time()

            txt_url = url + str(curr_book_num) + '/pg' + str(curr_book_num) + '.txt'
            new_txt_url = Constants.img_base_url + str(curr_book_num) + '/' + str(curr_book_num) + '-0.txt'
            try:
                response = requests.get(txt_url, allow_redirects=True)
                # second try
                if not response.ok:
                    response = requests.get(new_txt_url, allow_redirects=True)
                # continue to the next book
                if not response.ok:
                    print('failed fetching - unable to get data from gutenberg')
                    continue

                content = response.text
                author = DataCollector.find_specific_word('Author', ': ', content)
                title = DataCollector.find_specific_word('Title', ': ', content).split('(')[0]
                illustrator = DataCollector.find_specific_word('Illustrator', ': ', content)

            except Exception as e:
                print('failed getting response from gutenberg')
                continue

            title_for_scarpping = title.replace(' ', '%20')
            author_for_scrapping = author.replace(' ', '%20')
            # get book data if exists
            try:
                book_json_data = requests.get(Constants.open_library_base_url + title_for_scarpping + '%20' + author_for_scrapping, allow_redirects=True).text
                book_dict_data = json.loads(book_json_data)
                main_content = content.split('***')[2]

                # checks if open library data is valid
                if len(book_dict_data['docs']) == 0:
                    print('failed fetching - open library data was empty')
                    continue
            except Exception as e:
                print(e)
                continue

            main_content = main_content.replace('\r', ' ')
            main_content = main_content.replace('\n', ' ')

            new_main = main_content
            first_run = True
            while new_main != main_content or first_run:
                first_run = False
                main_content = new_main
                new_main = main_content.replace('  ', ' ')

            nlp_geo_results = DataCollector.run_nlp_engine(main_content)

            if nlp_geo_results is None:
                print('failed fetching - nlp algorithm failed')
                continue

            country_city_sets = set(nlp_geo_results)
            coord_dict = {}
            #  (in each up-down and left-right) to every position before putting it in the list.
            for country_city_tup in country_city_sets:
                coords = DataCollector.get_address_coordinates(country_city_tup)
                if coords != -1:
                    coord_dict[country_city_tup] = coords

            # create json format
            try:
                random_addition = random.uniform(0, MAX_CORD_ADDITION)
                location_coord_list = list(coord_dict.values())
                for loc_tuple in location_coord_list:
                    loc_tuple[0] += random_addition
                    loc_tuple[1] += random_addition
                inner_json = DataCollector.convert_data_to_json(id=curr_book_num,
                                                                location_coord_list=location_coord_list,
                                                                title=title,
                                                                author=author,
                                                                illustrator=illustrator,
                                                                books_data_dict=book_dict_data,
                                                                db_handler=db_handler,
                                                                )
                if inner_json is not None:
                    final_json['features'].append(inner_json)
            except Exception as e:
                print("failed extracting: " + str(e))
                continue
            finish_time = time.time()
            print("finished fetching, took: " + str((finish_time - starting_time)))
            # print(coord_dict.keys())

        with open(Constants.json_file_path, 'w') as fp:
            json.dump(final_json, fp)
            print("saved json file.")

    @staticmethod
    def convert_data_to_json(id, location_coord_list, title, author, illustrator, books_data_dict,
                             db_handler):
        cover_value = "%" #important to leave "%" on not found
        author_key = ""
        release_year = ""
        lang = ""
        category = "Other"
        try:
            if books_data_dict['docs']:
                release_year = str(books_data_dict['docs'][0]['first_publish_year'])

                lang = books_data_dict['docs'][0]['language'] if 'language' in books_data_dict['docs'][0].keys() else ''
                category_list = books_data_dict['docs'][0]['subject'] if 'subject' in books_data_dict['docs'][0].keys() else []

                for legit_category in Constants.optional_categories_list:
                    if legit_category in category_list:
                        category = legit_category
                        break
                if author == "":
                    author = books_data_dict['docs'][0]['author_name'][0]
                cover_value = "%"

                if 'author_key' in books_data_dict['docs'][0].keys() and \
                        len(books_data_dict['docs'][0]['author_key']) > 0:
                    author_key = str(books_data_dict['docs'][0]['author_key'][0])

                if 'cover_i' in books_data_dict['docs'][0].keys() and books_data_dict['docs'][0]['cover_i']:
                    cover_value = str(books_data_dict['docs'][0]['cover_i'])

        except KeyError as ke:
            print("Error occurred: " + str(ke))
        json_dict = {'type': 'Feature',
                     'properties': {'id': id,
                                    'title': title,
                                    'cover_url': cover_value,
                                    'release_year': release_year,
                                    'lang': lang,
                                    'author': author,
                                    'author_key': author_key,
                                    'illustrator': illustrator,
                                    'category': category,
                                    'line': location_coord_list,
                                    },
                     'geometry': {'type': "MultiPoint",
                                  "coordinates": location_coord_list
                                  }
                     }
        # return none if missing important values
        if author == "" or release_year == "" or title == "" or \
                len(location_coord_list) == 0 or (cover_value != "%" and cover_value in COVER_IDS):
            print('author: ' + author)
            print('release_year: ' + release_year)
            print('title: ' + title)
            print('location_coord_list: ' + str(location_coord_list))
            print('cover_value: ' + str(cover_value))

            return None

        if cover_value != "%":
            COVER_IDS.add(cover_value)

        args_to_db = list(json_dict['properties'].values())
        args_to_db = tuple([str(arg) for arg in args_to_db])
        try:
            db_handler.insert_to_books(args_to_db)
        except Exception as e:
            print(e)
            print('update value')
            db_handler.update_books_by_name(title, args_to_db[2:])

        return json_dict

    @staticmethod
    def combine_json_files(json_path_1, json_path_2, new_json_path):
        with open(json_path_1, "r") as read_file_1:
            json_1 = json.load(read_file_1)
        with open(json_path_2, "r") as read_file_2:
            json_2= json.load(read_file_2)

        new_json = {"type": "FeatureCollection",
                    "features": []}
        new_features_list = json_1['features']
        new_features_list.extend(json_2['features'])
        new_json['features'] = new_features_list

        with open(new_json_path, 'w') as fp:
            json.dump(new_json, fp)


def main():
    if Constants.init_db:
        DBInit.create_books_db(Constants.db_path)
    db_handler = DBHandler(Constants.db_path)
    # DataCollector.create_json_from_db(db_handler=db_handler, json_path='db_json.json')
    # DataCollector.create_json_from_db(db_handler=db_handler, json_path='db_json2.json')

    # DataCollector.combine_json_files('db_json.json', 'db_json2.json', 'final_json.json')
    DataCollector.collect_data_from_source(Constants.main_url, db_handler)


if __name__ == '__main__':
    main()
