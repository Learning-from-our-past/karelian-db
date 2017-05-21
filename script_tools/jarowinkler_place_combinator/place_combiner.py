import jellyfish
import csv

"""
This is a helper script which takes in a csv containing raw place data from db which was created
after running name_fixer.py to it. Name fixer fixed names of the places which had same stemmed name in the db and
produced places with duplicate names:

    Alastaro    - Alastar -> Alastaro
    Alastarossa - Alastar -> Alastaro

Then csv file was produced with following query to get rid of the duplicate rows:

select DISTINCT ON ("stemmedName", "region") "stemmedName", "region", *
from siirtokarjalaisten_tie."Place";

Now this resulting csv might have combined Places with exactly same stemmed name, but this
naive stemming is not enough for Finnish. Therefore try to further combine places with almost
same stemmedName by using Jaro-Winkler distance. This should combine places whose stemmedName's end
part is slightly different (like it would be in some cases of conjugated place names).

Resulting csv-file then contains list of Place names from the db. This list can then be used in Kaira
to figure out real place name for conjugated place names by doing a Jaro-Winkler search to the list
and picking the closest match.
"""

def combine_places(csv_file_path):
    places_csv = open(csv_file_path, encoding='utf8')
    reader = list(csv.DictReader(places_csv))

    results = []
    jw_threshold = 0.97

    for place in reader:
        matches = []
        for p in reader:
            diff = jellyfish.jaro_winkler(p['stemmedName'], place['stemmedName'])

            if not 'used' in p and diff >= jw_threshold:
                matches.append(p)
                p['used'] = True

        if len(matches) > 1:
            regions = list((p['region'] for p in matches))
            if len(set(regions)) == 1:

                # check if there is coordinates for some of the matches, if there is, prioritize them
                # they are more likely to be real place names
                matches_with_coordinates = [p for p in matches if p['longitude']]

                if len(matches_with_coordinates) > 0:
                    matches = matches_with_coordinates
                # we can combine results since they have same region entries
                # Choose shorter name from multiple ones
                shortest = min(matches, key=lambda place: len(place['stemmedName']))
                names = [n['name'] for n in matches]
                print(shortest['name'], names)
                results.append(shortest)
            else:
                # Add all different region combinations to the results set
                place['used'] = True
                results.append(place)

        else:
            results = results + matches

    return results


if __name__ == '__main__':
    results = combine_places('raw_places.csv')

    with open('combined_places.csv', 'w', encoding='utf8') as f:
        writer = csv.DictWriter(f, ('id', 'used', 'name', 'region', 'stemmedName', 'extractedName', 'latitude', 'longitude'))
        writer.writeheader()
        writer.writerows(results)
        f.close()
