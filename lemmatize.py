from models.db_siirtokarjalaistentie_models import *
from google import google
import time
import random

db_connection.init_database()
db_connection.connect()
database = db_connection.get_database()

q = (Place.select()
     .where(Place.region == None)
     .where(Place.lemmatizated == None)
     .order_by(Place.name))

count = len(q)
for place_entry in q:
    num_page = 1
    search_results = google.search(place_entry.name, num_page)
    for result in search_results:
        place_entry.lemmatizated = result.name
        place_entry.save()
        database.commit()

        print(place_entry.name, result.name)
        break
    time.sleep(random.randint(2, 8))

