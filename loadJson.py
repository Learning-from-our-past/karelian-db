import json
from db_manager import DbManager

def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data

def populate_db(data):
    db = DbManager()

    for person in data:
        db.insert_person(person)
        print("Added ", person["FirstNames"], person["Surname"])
    db.commit()
    db.close()



if __name__ == "__main__":
    data = load_json("./json/testset.json")
    populate_db(data)
