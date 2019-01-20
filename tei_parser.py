import pandas as pd
import codecs
import xmltodict
import copy

MIN_NUM_OF_COLUMNS = 3


def main():
    base_df = pd.DataFrame({'index': [], 'base_word': [], 'origin': [], 'prefix less': [], 'morphology': [],
                            'unspecified_6': [], 'unspecified_7': [], 'unspecified_8': [], 'unspecified_9': [],
                            'unspecified_10': [], 'unspecified_11': [], 'unspecified_12': []})

    parsed_file = codecs.open('adler_parser.txt', 'r', 'utf8')
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

    xml_file = codecs.open('ass1/Untitled1.xml', 'r', 'utf8')
    xml_text = xml_file.read()

    xml_dict = xmltodict.parse(xml_text)

    place_list_of_dict = xml_dict['TEI']['teiHeader']['profileDesc']['settingDesc']['listPlace']['place']
    org_list_of_dict = xml_dict['TEI']['teiHeader']['profileDesc']['particDesc']['org']
    person_list_of_dict = xml_dict['TEI']['teiHeader']['profileDesc']['particDesc']['listPerson']['person']

    wanted_place_list = [_dict['placeName'] for _dict in place_list_of_dict]
    wanted_org_list = [_dict['name'] if 'name' in _dict.keys() else _dict['orgName'] for _dict in org_list_of_dict]
    wanted_person_list = [_dict['persName']['forename'] + '-' + _dict['persName']['surname'] for _dict in person_list_of_dict]

    print('start comparision:')

    conf_mat_dict = {'fp': 0, 'tp': 0, 'fn': 0, 'tn': 0}
    conf_mat_for_type = {'loc': copy.deepcopy(conf_mat_dict),
                         'pers': copy.deepcopy(conf_mat_dict),
                         'org': copy.deepcopy(conf_mat_dict)}

    results_dict = {'loc': {'true': wanted_place_list, 'pred': adler_loc_list},
                    'org': {'true': wanted_org_list, 'pred': adler_org_list},
                    'pers': {'true': wanted_person_list, 'pred': adler_pers_list}}

    for list_key in results_dict.keys():
        true_list = results_dict[list_key]['true']
        pred_list = results_dict[list_key]['pred']
        for p_val in pred_list:
            found = False
            for t_val in true_list:
                if p_val in t_val:
                    conf_mat_for_type[list_key]['tp'] += 1
                    found = True
            if not found:
                conf_mat_for_type[list_key]['fp'] += 1
        conf_mat_for_type[list_key]['fn'] = len(pred_list) - conf_mat_for_type[list_key]['tp']
        conf_mat_for_type[list_key]['tn'] = base_df.shape[0] - conf_mat_for_type[list_key]['fp']

        # normalize
        conf_mat_for_type[list_key]['fn'] /= len(pred_list)
        conf_mat_for_type[list_key]['tp'] /= len(pred_list)
        conf_mat_for_type[list_key]['fp'] /= base_df.shape[0]
        conf_mat_for_type[list_key]['tn'] /= base_df.shape[0]

    print(conf_mat_for_type)


if __name__ == '__main__':
    main()
