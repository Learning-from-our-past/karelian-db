"""
This is a dict of Katiha parish IDs and their equivalent places in the MiKARELIA
database. As there are so few of them, it was hand made by comparing the parish
in Katiha's parishes table to the place names in MiKARELIA's Place table.
"""

KATIHA_PARISH_ID_TO_BIRTHPLACE_NAME = {
    13: {'katiha_name': 'Antrea', 'mikarelia_name': 'Antrea'},
    61: {'katiha_name': 'Harlu', 'mikarelia_name': 'Harlu'},
    68: {'katiha_name': 'Heinjoki', 'mikarelia_name': 'Heinjoki'},
    92: {'katiha_name': 'Hiitola', 'mikarelia_name': 'Hiitola'},
    109: {'katiha_name': 'Ihantala', 'mikarelia_name': 'Ihantala'},
    116: {'katiha_name': 'Ilmee', 'mikarelia_name': 'Ilmee'},
    119: {'katiha_name': 'Impilahti', 'mikarelia_name': 'Impilahti'},
    122: {'katiha_name': 'Inkerin pakol.srk', 'mikarelia_name': 'Inkeri'},
    126: {'katiha_name': 'Jaakkima', 'mikarelia_name': 'Jaakkima'},
    132: {'katiha_name': 'Johannes', 'mikarelia_name': 'Johannes'},
    152: {'katiha_name': 'Jääski', 'mikarelia_name': 'Jääski'},
    163: {'katiha_name': 'Kanneljärvi', 'mikarelia_name': 'Kanneljärvi'},
    182: {'katiha_name': 'Kaukola', 'mikarelia_name': 'Kaukola'},
    206: {'katiha_name': 'Kirvu', 'mikarelia_name': 'Kirvu'},
    212: {'katiha_name': 'Kivennapa', 'mikarelia_name': 'Kivennapa'},
    215: {'katiha_name': 'Koivisto', 'mikarelia_name': 'Koivisto'},
    225: {'katiha_name': 'Korpiselkä', 'mikarelia_name': 'Korpiselkä'},
    245: {'katiha_name': 'Kuolemajärvi', 'mikarelia_name': 'Kuolemajärvi'},
    252: {'katiha_name': 'Kurkijoki', 'mikarelia_name': 'Kurkijoki'},
    263: {'katiha_name': 'Käkisalmen msrk', 'mikarelia_name': 'Käkisalmi'},
    264: {'katiha_name': 'Käkisalmi', 'mikarelia_name': 'Käkisalmi'},
    285: {'katiha_name': 'Lavansaari', 'mikarelia_name': 'Lavansaari'},
    309: {'katiha_name': 'Lumivaara', 'mikarelia_name': 'Lumivaara'},
    329: {'katiha_name': 'Metsäpirtti', 'mikarelia_name': 'Metsäpirtti'},
    339: {'katiha_name': 'Muolaa', 'mikarelia_name': 'Muolaa'},
    392: {'katiha_name': 'Petsamo', 'mikarelia_name': 'Petsamo'},
    427: {'katiha_name': 'Pyhäjärvi', 'mikarelia_name': 'Pyhäjärvi'},
    433: {'katiha_name': 'Pälkjärvi', 'mikarelia_name': 'Pälkjärvi'},
    449: {'katiha_name': 'Rautu', 'mikarelia_name': 'Rautu'},
    461: {'katiha_name': 'Ruskeala', 'mikarelia_name': 'Ruskeala'},
    464: {'katiha_name': 'Räisälä', 'mikarelia_name': 'Räisälä'},
    470: {'katiha_name': 'Sakkola', 'mikarelia_name': 'Sakkola'},
    471: {'katiha_name': 'Salmi (evl.)', 'mikarelia_name': 'Salmi'},
    485: {'katiha_name': 'Seiskari', 'mikarelia_name': 'Seiskari'},
    498: {'katiha_name': 'Soanlahti', 'mikarelia_name': 'Soanlahti'},
    504: {'katiha_name': 'Sortavalan msrk', 'mikarelia_name': 'Sortavala'},
    507: {'katiha_name': 'Sortavalan ksrk', 'mikarelia_name': 'Sortavala'},
    516: {'katiha_name': 'Suojärvi', 'mikarelia_name': 'Suojärvi'},
    524: {'katiha_name': 'Suursaari', 'mikarelia_name': 'Suursaari'},
    527: {'katiha_name': 'Säkkijärvi', 'mikarelia_name': 'Säkkijärvi'},
    549: {'katiha_name': 'Terijoki', 'mikarelia_name': 'Terijoki'},
    579: {'katiha_name': 'Tytärsaari', 'mikarelia_name': 'Tytärsaari'},
    592: {'katiha_name': 'Uusikirkko', 'mikarelia_name': 'Uusikirkko'},
    597: {'katiha_name': 'Vahviala', 'mikarelia_name': 'Vahviala'},
    600: {'katiha_name': 'Valkjärvi', 'mikarelia_name': 'Valkjärvi'},
    625: {'katiha_name': 'Viipurin tksrk', 'mikarelia_name': 'Viipuri'},
    627: {'katiha_name': 'Viipurin msrk', 'mikarelia_name': 'Viipuri'},
    636: {'katiha_name': 'Vuoksela', 'mikarelia_name': 'Vuoksela'},
    637: {'katiha_name': 'Vuoksenranta', 'mikarelia_name': 'Vuoksenranta'},
    660: {'katiha_name': 'Äyräpää', 'mikarelia_name': 'Äyräpää'},
    1001: {'katiha_name': 'Annantehdas (ort.)', 'mikarelia_name': 'Annantehdas'},
    1018: {'katiha_name': 'Kitelä (ort.)', 'mikarelia_name': 'Kitelä'},
    1020: {'katiha_name': 'Korpiselkä (ort.)', 'mikarelia_name': 'Korpiselkä'},
    1025: {'katiha_name': 'Kyyrölä (ort.)', 'mikarelia_name': 'Kyyrölä'},
    1026: {'katiha_name': 'Käkisalmi (ort.)', 'mikarelia_name': 'Käkisalmi'},
    1032: {'katiha_name': 'Mantsinsaari (ort.)', 'mikarelia_name': 'Mantsinsaari'},
    1036: {'katiha_name': 'Palkeala (ort.)', 'mikarelia_name': 'Palkeala'},
    1037: {'katiha_name': 'Petsamo (ort.)', 'mikarelia_name': 'Petsamo'},
    1040: {'katiha_name': 'Pitkäranta (ort.)', 'mikarelia_name': 'Pitkäranta'},
    1042: {'katiha_name': 'Raivola (ort.)', 'mikarelia_name': 'Raivola'},
    1048: {'katiha_name': 'Salmi (ort.)', 'mikarelia_name': 'Salmi'},
    1051: {'katiha_name': 'Sortavala (ort.)', 'mikarelia_name': 'Sortavala'},
    1052: {'katiha_name': 'Suistamo (ort.)', 'mikarelia_name': 'Suistamo'},
    1053: {'katiha_name': 'Suojärvi (ort.)', 'mikarelia_name': 'Suojärvi'},
    1056: {'katiha_name': 'Terijoki (ort.)', 'mikarelia_name': 'Terijoki'},
    1057: {'katiha_name': 'Tiurula (ort.)', 'mikarelia_name': 'Tiurula'},
    1061: {'katiha_name': 'Uusikirkko (ort.)', 'mikarelia_name': 'Uusikirkko'},
    1064: {'katiha_name': 'Viipuri (ort.)', 'mikarelia_name': 'Viipuri'},
    1065: {'katiha_name': 'Viipurin suom. (ort.)', 'mikarelia_name': 'Viipurin'}
}


"""
This is a dict of some common mispellings or alternate forms of place names 
that show up in the Katiha data and need to be changed to their MiKARELIA
equivalents.
"""
KATIHA_BIRTHPARISH_TO_MIKARELIA_BIRTHPLACE = {
    'rla': 'ruskeala',
    'rlaj': 'ruskeala',
    'viip.': 'viipuri',
    'wiipuri': 'viipuri',
    'wiip.': 'viipuri',
    'viipuri msrk': 'viipuri',
    'viipurin msrk.': 'viipuri',
    'j.': 'viipuri',
    'johannes': 'viipuri',
    'viipurin msrk:ssa': 'viipuri',
    'viipurin msrk': 'viipuri',
    'viipurissa': 'viipuri',
    'k:selkä': 'korpiselkä',
    'imp:ti': 'impilahti',
    '0285': 'lavansaari',           # this is clearly a parishId but it's in the birthParish
    'valkjärvellä': 'valkjärvi'     # column for some reason
}


"""
This is a dict for generalizing some MiKARELIA place names
"""
GENERALIZE_MIKARELIA_BIRTHPLACE = {
    'sortavalanmlk': 'sortavala',
    'viipurinmlk': 'viipuri',
    'käkisalmenmlk': 'käkisalmi',
    'viipu': 'viipuri'
}
