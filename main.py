import json
from models.db_connection import db_connection
from populate import populate_person

def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data

def populate_db(data):
    database.set_autocommit(False)
    database.begin()
    try:
        for idx, person in enumerate(data):
            populate_person(person)
            print("Added ", person['name']['results']["firstNames"], person['name']['results']["surname"], idx+1, '/', len(data))

        database.commit()
    except Exception:
        print('rollback')
        database.rollback()

    database.set_autocommit(True)
    database.close()



if __name__ == "__main__":
    db_connection.init_database()
    db_connection.connect()
    database = db_connection.get_database()

    data = load_json("./json/testset.json")
    populate_db(data)


