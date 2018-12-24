import geotext
import requests
import Constants
from geopy.geocoders import Nominatim
import spacy
import json
import time


class DataCollector(object):
    # TODO: add illustrator,category
    @staticmethod
    def collect_data_from_source(url):

        nlp = spacy.load('en_core_web_sm')

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

        json_current_ids = [inner_dict['properties']['id'] for inner_dict in final_json['features']]
        for curr_book_num in range(Constants.lower_bound, Constants.upper_bound):

            if curr_book_num in json_current_ids:
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
                    location = geolocator.geocode(address)
                    # print(address)
                    curr_importance = location.raw['importance']
                    # print(curr_importance)
                    if curr_importance > Constants.importance_threshold and address not in Constants.black_list:
                        return [location.longitude, location.latitude]
                    else:
                        return -1
                except Exception as e:
                    return -1
            try:
                author = find_specific_word('Author', ': ')
                title = find_specific_word('Title', ': ')
                illustrator = find_specific_word('Illustrator', ': ')
            except IndexError as ie:
                print('failed extracting - ' + str(ie))
                continue
            title_for_scarpping = title.replace(' ', '+')
            author_for_scrapping = author.replace(' ', '+')
            # get book data if exists
            try:
                book_json_data = requests.get(Constants.open_library_base_url + title_for_scarpping + '+by+' + author_for_scrapping, allow_redirects=True).text
                book_dict_data = json.loads(book_json_data)
                main_content = content.split('***')[2]
            except Exception as e:
                print(e)
                continue

            # split content main text
            main_content = main_content.replace('\r', ' ')
            main_content = main_content.replace('\n', ' ')

            new_main = main_content
            first_run = True
            while new_main != main_content or first_run:
                first_run = False
                main_content = new_main
                new_main = main_content.replace('  ', ' ')

            # TODO: handle big text
            try:
                doc = nlp(main_content)
            except ValueError as ve:
                print(ve)
                continue
            nlp_geo_results = []
            for ent in doc.ents:
                if ent.label_ == 'GPE':
                    nlp_geo_results.append(ent.text)

            content = content.replace('\r', '')
            content = content.replace('\n', '')

            splitted_text = content.split(' ')

            country_city_sets = set(nlp_geo_results)
            coord_dict = {}
            # TODO:: add a 0.4 kilometer random move to cities and 20 kilometer move to countries
            #  (in each up-down and left-right) to every position before putting it in the list.
            for country_city_tup in country_city_sets:
                coords = get_address_coordinates(country_city_tup)
                if coords != -1:
                    coord_dict[country_city_tup] = coords

            # create json format
            # TODO: fix locations list with duplicates
            try:
                final_json['features'].append(convert_data_to_json(id=curr_book_num,
                                                                   location_coord_list=list(coord_dict.values()),
                                                                   title=title,
                                                                   author=author,illustrator=illustrator,
                                                                   books_data_dict=book_dict_data))
            except Exception as e:
                print("failed extracting: " + str(e))
                continue
            finish_time = time.time()
            print("finished fetching, took: " + str((finish_time - starting_time)))
            # print(coord_dict.keys())
        with open(Constants.json_file_path, 'w') as fp:
            json.dump(final_json, fp)
            print("saved json file.")


def convert_data_to_json(id, location_coord_list, title, author, illustrator, books_data_dict):
    cover_value = "%" #important to leave "%" on not found
    author_key = ""
    release_year = ""
    lang = ""
    # TODO:: add subjects of book and only leave the most common subjects from a list,
    #  leave only one subject as value and not a list. one subject for book for easier filtering..

    category = ""
    try:
        if books_data_dict['docs']:
            # print(books_data_dict['docs'][0])
            cover_value = str(books_data_dict['docs'][0]['cover_i'])
            if not cover_value:
                cover_value = "%"
            author_key = str(books_data_dict['docs'][0]['author_key'][0])
            # print(author_key)
            release_year = str(books_data_dict['docs'][0]['first_publish_year'])
            lang = books_data_dict['docs'][0]['language']
            category = 'Other'
            category_list = books_data_dict['docs'][0]['subject']
            for legit_category in Constants.optional_categories_list:
                if legit_category in category_list:
                    category = legit_category
                    break
    except KeyError as ke:
        print("Error occurred: " + str(ke))
    json_dict = {'type': 'Feature',
                 'properties': {'id': id,
                                'title': title,
                                'cover_url': cover_value,
                                'genre': 'None',
                                'release_year': release_year,
                                'lang': lang,
                                'author': author,
                                'author_key': author_key,
                                'illustrator': illustrator,
                                'category': category,
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
