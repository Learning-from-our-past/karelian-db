import json
import csv
import nltk.stem.snowball as snowball


"""
Convert csv list of fixed csv names to a json object where real place name is the key containing an object
with possible region data and list of incorrect stemmed forms of the name or conjugations. 
"""

stemmer = snowball.SnowballStemmer('finnish')
result_set = {}

with open('./fixed_place_names.csv', encoding='utf8') as names_csv:
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

    with open('./place_names_with_alternative_forms.json', 'w', encoding='utf8') as result_json:
        json.dump(result_set, result_json, indent=2, ensure_ascii=False)




