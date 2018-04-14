from datalinking.utils.db_utils import DbConnectionUtil
from datalinking.data_cleaner import KatihaDataCleaner
from datalinking.data_fetcher import KatihaDataFetcher
from datalinking.data_cleaner import MiKARELIADataCleaner
from datalinking.data_fetcher import MiKARELIADataFetcher
from datalinking.event_id_combiner import EventIdCombiner
from datalinking.family_creator import FamilyCreator
from datalinking.data_formatter import DataFormatter
from datalinking.data_linker import MiKARELIA2KatihaLinker
import pickle
from os import path


def get_katiha_data():
    print('Fetching Katiha data...')
    katiha_fetcher = KatihaDataFetcher(KatihaDataCleaner())
    with DbConnectionUtil('katiha'):
        katiha_data = katiha_fetcher.fetch_people()
    return katiha_data


def get_mikarelia_data():
    print('Fetching MiKARELIA data...')
    mikarelia_fetcher = MiKARELIADataFetcher(MiKARELIADataCleaner())
    with DbConnectionUtil('mikarelia'):
        mikarelia_data = mikarelia_fetcher.fetch_people()
    return mikarelia_data


def get_link_data(mikarelia_data, katiha_data):
    print('Linking data...')
    linker = MiKARELIA2KatihaLinker(from_data=mikarelia_data, to_data=katiha_data)
    return linker.find_links()


def add_family_data(katiha_data, link_data):
    print('Adding family data...')
    combiner = EventIdCombiner()
    combiner.create_family_id_maps(katiha_data)
    family_creator = FamilyCreator(combiner.families, combiner.db_id2family_id, katiha_data)
    family_creator.create_families(link_data)
    return family_creator.families, family_creator.kaira_id2family_id


def get_linked_katiha_data_with_families(katiha_data, link_data):
    linked_families, kaira_id2family_id = add_family_data(katiha_data, link_data)
    data_formatter = DataFormatter(kaira_id2family_id, linked_families, katiha_data)
    return data_formatter.get_katiha_people_with_kaira_and_family_ids(link_data)


def run_data_linking(output_path):
    katiha_data = get_katiha_data()
    mikarelia_data = get_mikarelia_data()
    link_data = get_link_data(mikarelia_data, katiha_data)
    linked_katiha_people = get_linked_katiha_data_with_families(katiha_data, link_data)

    filename = 'linked_katiha_data.pkl'
    file_path = path.join(output_path, filename)
    with open(file_path, mode='wb') as output_file:
        pickle.dump(linked_katiha_people, output_file)
    print('Success! Wrote linked data to {}'.format(file_path))
