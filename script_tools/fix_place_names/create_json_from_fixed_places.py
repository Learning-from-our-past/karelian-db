import json
import csv
import nltk.stem.snowball as snowball
import argparse
from tabulate import tabulate

"""
Convert csv list of fixed csv names to a json object where real place name is the key containing an object
with possible region data and list of incorrect stemmed forms of the name or conjugations. 

Alternatively by providing -r flag and existing json of place names, one can update manually set regions to
the json later to be used by Kaira when extraction place names and tagging them with region information.
"""

parser = argparse.ArgumentParser(description='Convert csv list of place names to json which groups alternative manually fixed place names under one key.')
parser.add_argument('-i', nargs='?', type=argparse.FileType('r', encoding='utf8'), help='Input file to read places from.', default=None)
parser.add_argument('-o', nargs='?', type=argparse.FileType('r+', encoding='utf8'), help='Output file to save data to. Json', default=None)
parser.add_argument('-r', action='store_true', help='Update regions. Expects only fixed_name and region info. Searches place from existing json and updates it.', default=None)
stemmer = snowball.SnowballStemmer('finnish')

def generate_json(args):
    print('Creating json file to contain the fixed names of places...')
    result_set = {}

    source_file = args['i']
    destination_file = args['o']

    with source_file as names_csv:
        reader = csv.DictReader(names_csv)

        for row in reader:
            if row['incorrect_or_ambiguous'] and not row['fixed']:
                continue

            key = stemmer.stem(row['fixed_name'])

            if key in result_set:
                result_set[key]['alternative_stemmed_names'].append(row['stemmed_name'])

                if result_set[key]['region'] is None and row['region']:
                    result_set[key]['region'] = row['region']
            else:
                result_set[key] = {
                    'fixed_name': row['fixed_name'].strip(),
                    'region': row['region'].strip() or None,
                    'country': row['country'].strip() or None,
                    'alternative_stemmed_names': [
                        row['stemmed_name']
                    ]
                }

        with destination_file as result_json:
            json.dump(result_set, result_json, indent=2, ensure_ascii=False)

def update_regions(args):
    print('Updating region data from provided csv to json format...')
    source_file = args['i']
    destination_file = args['o']

    statistics = {
        'updated_region_count': 0,
        'places_not_in_json_count': 0,
    }

    updated_place_names = []
    places_not_in_json = []

    existing_places = json.load(destination_file)
    places_in_csv = csv.DictReader(source_file)

    # Create a hash map which has as a key different writing styles of place names
    # which refer to correct data entry for those place names
    existing_places_index = {}
    for key, item in existing_places.items():
        existing_places_index[key] = item
        for name in item['alternative_stemmed_names']:
            existing_places_index[name] = item

    for row in places_in_csv:
        key = stemmer.stem(row['fixed_name'])

        if key in existing_places_index:
            existing_places_index[key]['region'] = row['region']
            statistics['updated_region_count'] += 1
            updated_place_names.append(existing_places_index[key]['fixed_name'])
        else:
            # Full search by using alternative forms
            statistics['places_not_in_json_count'] += 1
            places_not_in_json.append((row['fixed_name'], key))

    # Save changes to the json
    destination_file.seek(0)
    json.dump(existing_places, destination_file, indent=2, ensure_ascii=False)
    destination_file.truncate()

    print(statistics['updated_region_count'])
    print('Json updated. Statistics:\n')

    headers = ['Stat', 'Count']
    print(tabulate(statistics.items(), headers=headers), '\n')

    print('Places not in the json:')
    print(places_not_in_json)

    source_file.close()
    destination_file.close()



if __name__ == '__main__':
    args = vars(parser.parse_args())

    if args['r'] is False:
        generate_json(args)
    else:
        update_regions(args)

