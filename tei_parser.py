import pandas as pd
import codecs
import xmltodict
import copy
import re

MIN_NUM_OF_COLUMNS = 3


def tei_parser(predicted_file_path, correct_parsed_file_path):
    base_df = pd.DataFrame({'index': [], 'base_word': [], 'origin': [], 'prefix less': [], 'morphology': [],
                            'unspecified_6': [], 'unspecified_7': [], 'unspecified_8': [], 'unspecified_9': [],
                            'unspecified_10': [], 'unspecified_11': [], 'unspecified_12': []})

    parsed_file = codecs.open(predicted_file_path, 'r', 'utf8')
    base_index = 0
    for line in parsed_file:
        splitted_line = line.split(' ')
        if len(splitted_line) > MIN_NUM_OF_COLUMNS:
            splitted_line[-1] = splitted_line[-1].replace('null', '').replace('\t', '').replace('\n', '')
            base_df.loc[base_index] = splitted_line  # adding a row
            base_index += 1
            # base_df.index = base_df.index + 1  # shifting index
            # base_df = base_df.sort_index()  # sorting by index
    print('done parsing adler file.')

    adler_pers_list = base_df.loc[base_df['unspecified_12'] == 'I_PERS']['base_word'].tolist()
    adler_loc_list = base_df.loc[base_df['unspecified_12'] == 'I_LOC']['base_word'].tolist()
    adler_org_list = base_df.loc[base_df['unspecified_12'] == 'I_ORG']['base_word'].tolist()

    xml_file = codecs.open(correct_parsed_file_path, 'r', 'utf8')
    xml_text = xml_file.read()
    wanted_place_list, wanted_org_list, wanted_person_list = parse_by_dictionary_inner(xml_text)

    print('start comparision:')

    conf_mat_dict = {'fp': 0, 'tp': 0, 'fn': 0, 'tn': 0}
    conf_mat_for_type = {'loc': copy.deepcopy(conf_mat_dict),
                         'pers': copy.deepcopy(conf_mat_dict),
                         'org': copy.deepcopy(conf_mat_dict)}

    results_dict = {'loc': {'true': wanted_place_list, 'pred': adler_loc_list},
                    'org': {'true': wanted_org_list, 'pred': adler_org_list},
                    'pers': {'true': wanted_person_list, 'pred': adler_pers_list}}
    negative_dict = {'loc': base_df.loc[base_df['unspecified_12'] != 'I_LOC']['base_word'].tolist(),
                     'org': base_df.loc[base_df['unspecified_12'] != 'I_ORG']['base_word'].tolist(),
                     'pers': base_df.loc[base_df['unspecified_12'] != 'I_PERS']['base_word'].tolist()}

    for list_key in results_dict.keys():
        true_list = results_dict[list_key]['true']
        pred_list = results_dict[list_key]['pred']
        for p_val in pred_list:
            found = False
            for t_val in true_list:
                if p_val in t_val:
                    conf_mat_for_type[list_key]['tp'] += 1
                    found = True
                    break
            if not found:
                conf_mat_for_type[list_key]['fp'] += 1

        # look for false positive for each type
        for n_val in negative_dict[list_key]:
            for real_f_val in true_list:
                if n_val in real_f_val:
                    conf_mat_for_type[list_key]['fn'] += 1
                    break

        conf_mat_for_type[list_key]['fp'] = max(0, len(pred_list) - conf_mat_for_type[list_key]['tp'])
        conf_mat_for_type[list_key]['tn'] = max(0, len(negative_dict[list_key]) - conf_mat_for_type[list_key]['fn'])

        # normalize
        conf_mat_for_type[list_key]['fn'] /= len(negative_dict[list_key])
        conf_mat_for_type[list_key]['tp'] /= len(pred_list)
        conf_mat_for_type[list_key]['fp'] /= len(pred_list)
        conf_mat_for_type[list_key]['tn'] /= len(negative_dict[list_key])

    print(conf_mat_for_type)


def parse_brute_force(xml_text):
    first_q = 'placeName'
    sec_q = 'orgName'
    third_q = 'persName'
    parsed_by_first = xml_text.split(first_q)
    parsed_by_sec = xml_text.split(sec_q)
    parsed_by_third = xml_text.split(third_q)

    parsed_by_first = [x.replace('/', '').replace('<', '').replace('>', '').replace('\n', '').replace('\r', '') for x in parsed_by_first]
    parsed_by_sec = [x.replace('/', '').replace('<', '').replace('>', '').replace('\n', '').replace('\r', '') for x in parsed_by_sec]
    parsed_by_third = [x.replace('/', '').replace('<', '').replace('>', '').replace('\n', '').replace('\r', '') for x in parsed_by_third]

    del parsed_by_first[0::2]
    del parsed_by_sec[0::2]
    del parsed_by_third[0::2]
    return parsed_by_first, parsed_by_sec, parsed_by_third


def parse_by_dictionary_lists(xml_text):
    xml_dict = xmltodict.parse(xml_text)

    place_list_of_dict = xml_dict['TEI']['teiHeader']['profileDesc']['settingDesc']['listPlace']['place']
    org_list_of_dict = xml_dict['TEI']['teiHeader']['profileDesc']['particDesc']['org']
    person_list_of_dict = xml_dict['TEI']['teiHeader']['profileDesc']['particDesc']['listPerson']['person']

    wanted_place_list = [_dict['placeName'] for _dict in place_list_of_dict]
    wanted_org_list = [_dict['name'] if 'name' in _dict.keys() else _dict['orgName'] for _dict in org_list_of_dict]
    wanted_person_list = [_dict['persName']['forename'] + '-' + _dict['persName']['surname'] for _dict in person_list_of_dict]

    return wanted_place_list, wanted_org_list, wanted_person_list


def parse_by_dictionary_inner(xml_text):

    xml_dict = xmltodict.parse(xml_text)

    place_list = []
    org_list = []
    person_list = []

    def recursive_items(dictionary, upper_tag):
        for _key, _value in dictionary.items():
            if isinstance(_value, dict) and _key != 'teiHeader':
                yield from recursive_items(_value, _key)
            else:
                if isinstance(_value, list):
                    for v in _value:
                        if isinstance(v, dict):
                            yield from recursive_items(v, _key)
                        else:
                            yield (_key, v, upper_tag)
                else:
                    yield (_key, _value, upper_tag)

    for key, value, upper_tag in recursive_items(xml_dict, None):
        if '#' not in value:
            if key == 'placeName' or upper_tag == 'placeName':
                value_list = get_splitted_value_list(value)
                place_list.extend(value_list)
            elif key == 'orgName' or upper_tag == 'orgName':
                value_list = get_splitted_value_list(value)
                org_list.extend(value_list)
            elif key == 'persName' or key == 'surName' or key == 'foreName' or upper_tag == 'persName':
                value_list = get_splitted_value_list(value)
                person_list.extend(value_list)

    return place_list, org_list, person_list


def get_splitted_value_list(value):
    value_list = re.split("[, \-!?:]+", value)
    value_list = [x for x in value_list if x != '' and x != '.' and x != ' ']
    return value_list


def main():
    predicted_file_path = 'adler_files/116_אלמגור_דן.txt'
    true_labeled_file_path = 'student_files/XML-DanAlmagor.xml'
    tei_parser(predicted_file_path, true_labeled_file_path)


if __name__ == '__main__':
    main()
