import nltk.stem.snowball as snowball

from common.siirtokarjalaistentie_models import *

db_connection.init_database()
db_connection.connect()
database = db_connection.get_database()

q = (Place.select()
     .where(Place.stemmed == None)
     .order_by(Place.name))

count = len(q)
stemmer = snowball.SnowballStemmer('finnish')
for place_entry in q:
    result = stemmer.stem(place_entry.name)
    print(place_entry.name, result)
    place_entry.stemmed = result
    place_entry.save()
    database.commit()
