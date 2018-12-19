main_url = 'https://www.gutenberg.org/cache/epub/'
img_base_url = 'https://www.gutenberg.org/files/'
img_sec_url = '/images/cover.jpg'
cover_address = 'https://covers.openlibrary.org/w/id/' + '' + '-M.jpg'
open_library_base_url = 'http://openlibrary.org/search.json?q='
importance_threshold = 0.5
black_list = ['OR', 'I.', 'XV', 'Corn', 'Spartans:--"I', 'Sun', 'Pain', 'Philosopher', 'Gyara',
              'Hercules', 'XI', 'Gyaros', 'Empire', 'LV', 'Victory', 'Providence', 'Freedom',
              'Thou', 'Sauce', 'so;’', 'Station', 'Desert', 'Peto', 'Staffordshire', 'Theatre',
              'Whitehall', 'Wapping', 'Painter', 'Don Diego', 'Hero', 'Bounty', 'up.’', 'Reading', 'Pug',
              'St. So-and-So', 'Bang', 'monster.’', 'Opera', 'Port', 'pipe!’', 'NEWTON', 'Pit', 'City', 'White',
              'bill.’', 'Green', 'Strand', 'Temple', 'the City', 'Black', '—City', 'Muslin', 'XXII', 'Tree', 'XV', 'Codes', 'North', 'South', 'West', 'East', 'Spring', 'Bah', 'Solomon']
initialize_json = True
version = '1.0'
lower_bound = 860
upper_bound = 900
json_file_path = "books_" + str(lower_bound) + "_" + str(upper_bound) + "_version_" + version + ".json"
