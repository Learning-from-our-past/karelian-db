import csv
import ntpath


class CsvRecordOfPopulation:

    def __init__(self, file_name):
        self._file_name = ntpath.basename(file_name)

        self._person_file = open(file_name + '_persons.csv', 'w', encoding='utf8')
        self._source_text_file = open(file_name + '_source_texts.csv', 'w', encoding='utf8')

        self._person_field_names = ['kairaId', 'firstNames', 'lastNames', 'sourceTextId']
        self._source_text_field_names = ['sourceTextId', 'sourceText']

        self._person_writer = csv.DictWriter(self._person_file, fieldnames=self._person_field_names)
        self._person_writer.writeheader()

        self._source_text_writer = csv.DictWriter(self._source_text_file, fieldnames=self._source_text_field_names)
        self._source_text_writer.writeheader()
        self._source_texts = {}

        self._source_text_id_counter = 1

    def _get_source_text_id(self):
        self._source_text_id_counter += 1
        return self._file_name + '_' + str(self._source_text_id_counter)

    def _add_source_text(self, text):
        if text in self._source_texts:
            return self._source_texts[text]
        else:
            text_id = self._get_source_text_id()
            self._source_texts[text] = text_id

            return text_id

    def add_primary_person(self, person):
        source_text_id = self._add_source_text(person['personMetadata']['results']['originalText'])

        self._person_writer.writerow({'kairaId': person['kairaId']['results'],
                               'firstNames': person['name']['results']['firstNames'],
                               'lastNames': person['name']['results']['surname'],
                               'sourceTextId': source_text_id})

        return source_text_id

    def add_child(self, primary_person, child):
        source_text_id = self._add_source_text(primary_person['personMetadata']['results']['originalText'])

        self._person_writer.writerow({'kairaId': child['kairaId'],
                               'firstNames': child['name'],
                               'lastNames': primary_person['name']['results']['surname'],
                               'sourceTextId': source_text_id})

        return source_text_id

    def add_spouse(self, primary_person, spouse):
        source_text_id = self._add_source_text(primary_person['personMetadata']['results']['originalText'])

        self._person_writer.writerow({'kairaId': spouse['kairaId'],
                               'firstNames': spouse['spouseName'],
                               'lastNames':  primary_person['name']['results']['surname'],
                               'sourceTextId': source_text_id})

        return source_text_id

    def save_to_file(self):
        self._source_texts = [{'sourceTextId': text_id, 'sourceText': text} for text, text_id in self._source_texts.items()]
        self._source_text_writer.writerows(self._source_texts)

        self._person_file.close()
        self._person_file.close()
