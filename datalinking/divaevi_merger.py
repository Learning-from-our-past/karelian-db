import pandas as pd
import os
import glob
import pickle
import pprint


def get_divaevi_data():
    """ 1. get_divaevi_data()  
    #kaikki operaatiot dvv raaálle datalle 
    #return valmis yhdistää muotoo

    * lukee kaikki dvv tiedostot muistiin
    * siivousoperaatiot (splittaa syntymapaiva,kuolinpaiva  AAAABBCC -> AAAA BB CC)
    * yhdistä hetun pohjalta kaikki tarvittavat (esim SUKU ja LAPSEN_ASUIN_B) erilliset .csv tiedostot yhdeksi (MUISTIIN) 
    *  SUKU_LAPSIB merge  """

    if os.path.exists("./Divaevi/data/") == False:
        os.makedirs("./Divaevi/data/")

    # path = "./Divaevi/real_data/"   #testing for real data
    path = "./Divaevi/data/"  # testing for pseudo data
    excel_files = glob.glob(os.path.join(path, "*.xlsx"))

    if len(excel_files) == 0:
        raise Exception("No excel files available in this directory")

    df_list = [pd.read_excel(sheet) for sheet in excel_files]

    for df in df_list:
        df["link_kaira_id"] = df["ID-tunnus"].str.replace("1_", "siirtokarjalaiset_1_")
        df["link_kaira_id"] = df["link_kaira_id"].str.replace("P_0", "P")
    return df_list



    


def rename_divaevi(df_list):
    """ Renaming columns to match Mikarelia """
    for i in range(len(df_list)):
        df_list[i] = df_list[i].rename(
            columns={
                "Syntymä-päivä": "birth",
                "Syntymä-\nvuosi": "birthYear", "Suku-\npuoli": "sex",
                "Kuolinpäivä": "deathYear", "Äidin-\nkieli": "primaryLanguage",
                "Kotikunnan\nnimi": "birthResidence", "Koti-\nkunta": "birthResidenceId",
                "Tutkhenk nykyinen siviilisääty": "maritalStatus",
                "Päättymis-päivä": "maritalStatusExpiry",
                "Päätt-tapa": "maritalStatusExpiryType",
                "Puoliso ulkohenkilö": "spouseExternalPerson",
                "Puolison-ID": "spouseId",
                "Alkupäivä": "maritalStatusStart",
                "Sukul-\nsuhde": "familyRelation", "Asumisen\nalkupv": "residencyStart",
                "Asumisen\nloppupv": "residencyEnd", "Sukulaisen\nsyntymäpv": "relativeBirth",
                "Sukulaisen\nkuolinpv": "relativeDeath", "Asuminen": "residency"
            })
    return df_list


def split_by_column(df_list):
    "Split year, month and day to separate columns"

    list_of_splittable_columns = ["deathYear", "birth", "maritalStatusStart",
                                  "maritalStatusExpiry", "relativeBirth", "residencyEnd",
                                  "residencyStart", "relativeDeath"]

    for i in range(len(df_list)):
        for j in df_list[i].columns:
            if j in list_of_splittable_columns:
                df_list[i][j] = df_list[i][j].fillna(0)
                df_list[i]['col'] = df_list[i][j].astype(str)
                if 0 in df_list[i]['col'].str[6]:
                    df_list[i][j+"Day"] = df_list[i]['col'].str[7:8]
                else:
                    df_list[i][j+"Day"] = df_list[i]['col'].str[6:8]
                if 0 in df_list[i]['col'].str[4]:
                    df_list[i][j+"Month"] = df_list[i]['col'].str[5:6]
                else:
                    df_list[i][j+"Month"] = df_list[i]['col'].str[4:6]
                df_list[i][j+"Year"] = df_list[i]['col'].str[0:4]
                df_list[i][j+"Day"] = df_list[i][j+"Day"].apply(pd.to_numeric)
                df_list[i][j+"Month"] = df_list[i][j+"Month"].apply(pd.to_numeric)
                df_list[i][j+"Year"] = df_list[i][j+"Year"].apply(pd.to_numeric)
                df_list[i].drop('col', axis=1, inplace=True)
    


    return df_list


def merge_asuin_by_hetu_from_suku(df_list):
    "Merges all of the available hetu columns together"
    "IN THE FIRST BATCH ALL OF THE INFORMATION OF THE ASUINB AND ASUINA WERE CORRELATED WITH CHILDlink_kaira_id"
    "BUT NOT GRANDCHILD KAIRA ID"
    combined_df_list = list()
    combined_df = pd.DataFrame()
    for i in range(len(df_list)):
        for j in df_list[i].columns:
            if j == "Henkilötunnus":
                for h in range(len(df_list)):
                    for k in df_list[h].columns:
                        if k == "Välihenkilö 1":
                            df_list[i]
                            combined_df = pd.merge(
                                df_list[i], df_list[h], on="link_kaira_id", how="inner")
                            combined_df_list.append(combined_df)
                            # combined_df.to_excel("hetumergetesti_asuin_suku_v3.xlsx")

    return combined_df_list
# merge_asuin_by_hetu_from_suku(split_by_column(rename_divaevi(get_divaevi_data())))


def generateGrandChild_link_kaira_id_hetu(df_list):
    combined_df_list = list()
    combined_df = pd.DataFrame()
    for i in range(len(df_list)):
        for j in df_list[i].columns:
            if j == "familyRelation":
                for h, k in enumerate(df_list[i]["familyRelation"]):
                    df_list[i]["Henkilötunnus"][h] = "dbeaver_lapsilink_kaira_id+=1"
                    if k == 7:
                        df_list[i]["Sukulaisen\nhenkilötunnus"][h] = "Lapsenlapsi_GC_+=1_link_kaira_id"
                        df_list[i]["Välihenkilö 1"][h] = "dbeaver_lapsilink_kaira_id+=1"
                    elif k == 2:

                        df_list[i]["Sukulaisen\nhenkilötunnus"][h] = "dbeaver_lapsilink_kaira_id+=1"

    return df_list
# generateGrandChild_link_kaira_id_hetu(merge_asuin_by_hetu_from_suku(split_by_column(rename_divaevi(get_divaevi_data()))))


def combine_all_files(df_list):
    """Merges by Hetu and Birthyear"""
    "Denote: All of the following information in the relation sheet"
    "is for Sukulaisen henkilötunnus, and not for välihenkilö 1"
    combined_df_list = list()
    combined_df = pd.DataFrame()
    for i in range(len(df_list)):
        combined_df = df_list[i-1].combine_first(df_list[i])
        combined_df_list.append(combined_df)
    return combined_df_list



"following code is to combine mikarelia data with DVV data "
" this is done in the following way:"
"firstly we merge dbeavers child.csv:s childlink_kaira_id with SSN from DVV"


def preprocess_mikarelia_link_kaira_id(path_df_csv):
    df = pd.read_csv(path_df_csv)
    df["link_kaira_id"] = df["kairaId"]
    return df

    
preprocess_mikarelia_link_kaira_id(
    r"C:\Users\bohme\OneDrive\Desktop\Karjalaisprojekti\Divaevi\data\_Person__whole.csv")


def combine_mikarelia_kaira(df_list_dvv, df_list_mikarelia):
    combined_df_list = []
    f = 0
    for i in range(len(df_list_dvv)):
        for j in df_list_dvv[i].columns:
            for k in df_list_mikarelia.columns:
                if j == "link_kaira_id" and k == "link_kaira_id":
                    combined_df = pd.merge(
                        df_list_mikarelia[j], df_list_dvv[i], on="link_kaira_id", how="inner")
                    combined_df = combined_df.filter(
                        ['birthDay', 'birthMonth', 'birthYear', 'link_kaira_id',"residencyEndDay","residencyEndMonth","residencyEndYear"])
                    combined_df = combined_df.to_dict("records")
                    combined_df_list.append(combined_df)

    return combined_df_list


def divaevi_to_pickle(combined_df_list):
    filename = 'yhdistetty'
    outfile = open(filename, 'wb')
    pickle.dump(combined_df_list, outfile)
    outfile.close()


divaevi_to_pickle(combine_mikarelia_kaira(split_by_column(rename_divaevi(get_divaevi_data())),
                                          preprocess_mikarelia_link_kaira_id(r"C:\Users\bohme\OneDrive\Desktop\Karjalaisprojekti\Divaevi\data\_Person__whole.csv")))


def divaevi_from_pickle(filename):
    infile = open(filename, 'rb')
    new_dict = pickle.load(infile)
    infile.close()
    pprint.pprint(new_dict)


divaevi_from_pickle("yhdistetty")
