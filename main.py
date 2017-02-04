import json
from models.db_models import *
from populate import populate_person

database.connect()

def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data

def populate_db(data):

    for idx, person in enumerate(data):
        populate_person(person)
        print("Added ", person["FirstNames"], person["Surname"], idx+1, '/', len(data))

    database.commit()
    database.close()



if __name__ == "__main__":
    data = load_json("./json/testset.json")
    populate_db(data)


