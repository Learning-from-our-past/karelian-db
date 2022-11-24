import pandas as pd
import os
import glob
import pickle
import pprint
import re


def get_divaevi_data():
    """
    Loads all of the excel files from local repository
    named ./Divaevi/data/ and creates the local repository if it doesn´t exist.

    return: list of dataframes

    """

    if os.path.exists('./Divaevi/kopiot') == False:
        os.makedirs('./Divaevi/kopiot')

    path = './Divaevi/kopiot'
    excel_files = glob.glob(os.path.join(path, '*.xlsx'))

    if len(excel_files) == 0:
        raise Exception('No excel files available in this directory')

    df_list = [pd.read_excel(sheet) for sheet in excel_files]

    return df_list


def preprocess_divaevi_data(df_list):
    """
    Preprocesses divaevi data so it can be merged with mikarelia data

    param df_list: list of the dvv, acquired from get_divaevi_data()

    return: list of dataframes
    """
    for df in df_list:
        df['link_kaira_id'] = df['ID-tunnus'].str.replace(
            '1_', 'siirtokarjalaiset_1_')
        df['link_kaira_id'] = df['link_kaira_id'].str.replace('P_0', 'P')

    return df_list


preprocess_divaevi_data(get_divaevi_data())


def rename_divaevi(df_list):
    """
    renames all of the available columns from dvv data

    param df_list: list of the dvv data, acquired from preprocess_divaevi_data()

    return: list of dataframes
    """

    for i in range(len(df_list)):
        df_list[i] = df_list[i].rename(
            columns={
                'Syntymä-päivä': 'birth', 'Suku-\npuoli': 'sex',
                'Kuolinpäivä': 'death', 'Äidin-\nkieli': 'primaryLanguage',
                'Kotikunnan\nnimi': 'domicile', 'Koti-\nkunta': 'domicileId',
                'Syntymäkotikunnan nimi': 'birthResidence',
                'Tutkhenk nykyinen siviilisääty': 'maritalStatus',
                'Päättymis-päivä': 'maritalStatusEnd',
                'Päätt-tapa': 'maritalStatusEndType',
                'Puoliso ulkohenkilö': 'spouseExternalPerson',
                'Puolison-ID': 'spouseId',
                'Alkupäivä': 'maritalStatusStart',
                'Sukul-\nsuhde': 'familyRelation', 'Asumisen\nalkupv': 'residencyStart',
                'Asumisen\nloppupv': 'residencyEnd', 'Sukulaisen\nsyntymäpv': 'relativeBirth',
                'Sukulaisen\nkuolinpv': 'relativeDeath', 'Asuminen': 'residency'
            })
    return df_list



def split_by_column(df_list):
    """
    Split year, month and day to separate columns

    param df_list: list of the dvv data, acquired from rename_divaevi()

    return: list of dataframes

    """

    list_of_splittable_columns = ['death', 'birth', 'maritalStatusStart',
                                  'maritalStatusEnd', 'relativeBirth', 'residencyEnd',
                                  'residencyStart', 'relativeDeath']

    for i in range(len(df_list)):
        for j in df_list[i].columns:

            if j in list_of_splittable_columns:
                df_list[i][j] = df_list[i][j].fillna(0)
                df_list[i]['col'] = df_list[i][j].astype(str)
                if 0 or '0' in df_list[i]['col'].str[6]:
                    df_list[i][j+'Day'] = df_list[i]['col'].str[7]
                else:
                    df_list[i][j+'Day'] = df_list[i]['col'].str[6:8]
                if 0 or '0' in df_list[i]['col'].str[4]:
                    df_list[i][j+'Month'] = df_list[i]['col'].str[5]
                else:
                    df_list[i][j+'Month'] = df_list[i]['col'].str[4:6]
                df_list[i][j+'Year'] = df_list[i]['col'].str[0:4]
                df_list[i][j+'Day'] = df_list[i][j+'Day'].apply(pd.to_numeric)
                df_list[i][j+'Month'] = df_list[i][j +
                                                   'Month'].apply(pd.to_numeric)
                df_list[i][j+'Year'] = df_list[i][j +
                                                  'Year'].apply(pd.to_numeric)
                df_list[i].drop('col', axis=1, inplace=True)

    return df_list


def merge_residency_with_relatives(df_list):
    """
    Merges residency history dataframe with relative history dataframe by SSN

    param df_list: list of the dvv data

    return: list of dataframes

    """
    combined_df_list = list()
    combined_df = pd.DataFrame()
    for i in range(len(df_list)):
        for j in df_list[i].columns:
            if j == 'Henkilötunnus':
                for h in range(len(df_list)):
                    for k in df_list[h].columns:
                        if k == 'Välihenkilö 1':
                            df_list[i]
                            combined_df = pd.merge(
                                df_list[i], df_list[h], on='link_kaira_id', how='inner')
                            combined_df_list.append(combined_df)

    return combined_df_list


def generateGrandChildKairaId(df_list):
    """
    Generates kairaIds for grandchildren

    param df_list: list of the dvv data

    return: list of dataframes

    """
    combined_df_list = list()
    combined_df = pd.DataFrame()
    for i in range(len(df_list)):
        for j in df_list[i].columns:
            if j == 'familyRelation':
                for h, k in enumerate(df_list[i]['familyRelation']):
                    df_list[i]['Henkilötunnus'][h] = 'dbeaver_lapsilink_kaira_id+=1'
                    if k == 7:
                        df_list[i]['Sukulaisen\nhenkilötunnus'][h] = 'Lapsenlapsi_GC_+=1_link_kaira_id'
                        df_list[i]['Välihenkilö 1'][h] = 'dbeaver_lapsilink_kaira_id+=1'
                    elif k == 2:

                        df_list[i]['Sukulaisen\nhenkilötunnus'][h] = 'dbeaver_lapsilink_kaira_id+=1'

    return df_list


def combine_all_files(df_list):
    """
    Combines list of dataframes to one single file

    param df_list: list of the dvv data

    return: list of dataframes

    """
    combined_df_list = list()
    combined_df = pd.DataFrame()
    for i in range(len(df_list)):
        combined_df = df_list[i-1].combine_first(df_list[i])
        combined_df_list.append(combined_df)
    return combined_df_list


def preprocess_mikarelia_link_kaira_id(path_df_csv):
    """
    Turns csv file into dataframe

    param path_df_csv: path of the mikarelia .csv data location

    return: list of dictionaries
    """
    df = pd.read_csv(path_df_csv)
    df['link_kaira_id'] = df['kairaId']
    return df


preprocess_mikarelia_link_kaira_id(
    r'C:\Users\bohme\OneDrive\Desktop\Karjalaisprojekti\Divaevi\data\_Person__whole.csv')


def combine_mikarelia_kaira(df_list_dvv, df_list_mikarelia):
    """
    Merges list of dataframes from dvv with mikarelia dataframe to one single file

    param df_list_dvv: list of the dvv data
    param df_list_mikarelia: list of the mikarelia data

    return: list of dictionaries
    """
    combined_df_list = []
    for i in range(len(df_list_dvv)):
        for j in df_list_dvv[i].columns:
            for k in df_list_mikarelia.columns:
                if j == 'link_kaira_id' and k == 'link_kaira_id':

                    combined_df = pd.merge(
                        df_list_mikarelia[j], df_list_dvv[i], on='link_kaira_id', how='inner')
                    combined_df = combined_df.filter(
                        [
                            'link_kaira_id',
                            'birthDay', 'birthMonth', 'birthYear',
                            'deathDay', 'deathMonth', 'deathYear',
                            'residencyStartDay', 'residencyStartMonth', 'residencyStartYear',
                            'residencyEndDay', 'residencyEndMonth', 'residencyEndYear', 
                            'birthResidence', 'domicile',
                            'sex', 'primaryLanguage',
                            'maritalStatus', 'maritalStatusEndType', 
                            'maritalStatusStartDay','maritalStatusStartMonth','maritalStatusStartYear',
                            'maritalStatusEndDay','maritalStatusEndMonth','maritalStatusEndYear',
                            'familyRelation',
                            'relativeBirthDay','relativeBirthMonth','relativeBirthYear',
                            'relativeDeathDay','relativeDeathMonth','relativeDeathYear'])
                    combined_df.to_csv(
                        r'C:\Users\bohme\OneDrive\Desktop\Karjalaisprojekti\TULOKSET_5_TUTKHENK_ASUINHIST.csv')
                    combined_df = combined_df.to_dict('records')
                    combined_df_list.append(combined_df)

    return combined_df_list


def divaevi_to_pickle(combined_df_list):
    """
    Serializes list of dictionaries to pickle file

    param combined_df_list: list of the dictionaries, acquired from combine_mikarelia_kaira()

    return: pickled object
    """
    filename = 'merged'
    outfile = open(filename, 'wb')
    pickle.dump(combined_df_list, outfile)
    outfile.close()


divaevi_to_pickle(combine_mikarelia_kaira(split_by_column(rename_divaevi(preprocess_divaevi_data(get_divaevi_data()))),
                                          preprocess_mikarelia_link_kaira_id(r'C:\Users\bohme\OneDrive\Desktop\Karjalaisprojekti\Divaevi\data\_Person__whole.csv')))


def divaevi_from_pickle(filename):
    """
    Reads the pickled representation of the object

    param filename: pickled representation of the object 

    return: list of dictionaries
    """
    infile = open(filename, 'rb')
    new_dict = pickle.load(infile)
    infile.close()
    pprint.pprint(new_dict)


divaevi_from_pickle('merged')
