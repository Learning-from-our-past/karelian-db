python main.py material/siirtokarjalaiset_I.json 
python main.py material/siirtokarjalaiset_II.json 
python main.py material/siirtokarjalaiset_III.json 
python main.py material/siirtokarjalaiset_IV.json 

python -m script_tools.mark_ambiguous_region_places_in_db

echo 'All done!'