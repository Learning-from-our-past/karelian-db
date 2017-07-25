import csv


class CsvRecordOfPopulation:

    def __init__(self, file_name):
        self._file = open(file_name, 'w', encoding='utf8')
        self._field_names = ['kairaId', 'firstNames', 'lastNames', 'sourceText']
        self._writer = csv.DictWriter(self._file, fieldnames=self._field_names)
        self._writer.writeheader()

    def add_primary_person(self, person):
        self._writer.writerow({'kairaId': person['kairaId']['results'],
                               'firstNames': person['name']['results']['firstNames'],
                               'lastNames': person['name']['results']['surname'],
                               'sourceText': person['personMetadata']['results']['originalText']})

    def add_child(self, primary_person, child):
        self._writer.writerow({'kairaId': child['kairaId'],
                               'firstNames': child['name'],
                               'lastNames': primary_person['name']['results']['surname'],
                               'sourceText': ''})

    def add_spouse(self, primary_person, spouse):
        self._writer.writerow({'kairaId': spouse['kairaId'],
                               'firstNames': spouse['spouseName'],
                               'lastNames':  primary_person['name']['results']['surname'],
                               'sourceText': primary_person['personMetadata']['results']['originalText']})

    def save_to_file(self):
        self._file.close()