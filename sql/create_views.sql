-- Person with birthdata
CREATE VIEW siirtokarjalaisten_tie.PersonExtended AS
  SELECT
    Person.id,
    firstname,
    lastname,
    prevlastname,
    profession.name as profession,
    sex,
    ownhouse,
    returnedkarelia,
    previousmarriages,
    pagenumber,
    origtext,
    Place.name AS birthplace,
    Place.latitude AS birthlatitude,
    Place.longitude AS birthlongitude,
    Place.region AS birthregion,
    birth.day AS birthday,
    birth.month AS birthmonth,
    birth.year AS birthyear
  FROM siirtokarjalaisten_tie.Person
    LEFT JOIN siirtokarjalaisten_tie.PersonDate AS birth ON birth.id = siirtokarjalaisten_tie.Person.birthdate
    LEFT JOIN siirtokarjalaisten_tie.Profession AS profession ON profession.id = siirtokarjalaisten_tie.Person.profession
    LEFT JOIN siirtokarjalaisten_tie.Place ON  siirtokarjalaisten_tie.Place.id =  siirtokarjalaisten_tie.Person.birthplace;

-- Spouse with birthdata
CREATE VIEW siirtokarjalaisten_tie.SpouseExtended AS
  SELECT
    Spouse.id,
    firstname,
    lastname,
    prevlastname,
    profession.name as profession,
    marriageyear,
    spouse,
    sex,
    siirtokarjalaisten_tie.Place.name AS birthplace,
    siirtokarjalaisten_tie.Place.latitude AS birthlatitude,
    siirtokarjalaisten_tie.Place.longitude AS birthlongitude,
    siirtokarjalaisten_tie.Place.region AS birthregion,
    birth.day AS birthday,
    birth.month AS birthmonth,
    birth.year AS birthyear,
    death.day AS deathday,
    death.month AS deathmonth,
    death.year AS deathyear
  FROM siirtokarjalaisten_tie.Spouse
    LEFT JOIN siirtokarjalaisten_tie.PersonDate AS birth ON birth.id = siirtokarjalaisten_tie.Spouse.birthdate
    LEFT JOIN siirtokarjalaisten_tie.PersonDate AS death ON death.id = siirtokarjalaisten_tie.Spouse.deathdate
    LEFT JOIN siirtokarjalaisten_tie.Profession AS profession ON profession.id = siirtokarjalaisten_tie.Spouse.profession
    LEFT JOIN siirtokarjalaisten_tie.Place ON siirtokarjalaisten_tie.Place.id =  siirtokarjalaisten_tie.Spouse.birthplace;

-- Main person with spouse data
CREATE VIEW siirtokarjalaisten_tie.PersonAndWife AS
  SELECT PersonExtended.*,
  siirtokarjalaisten_tie.SpouseExtended.firstname AS spouse_firstname,
  siirtokarjalaisten_tie.SpouseExtended.lastname AS spouse_lastname,
  siirtokarjalaisten_tie.SpouseExtended.prevlastname AS spouse_prevlastname,
  siirtokarjalaisten_tie.SpouseExtended.sex AS spouse_sex,
  siirtokarjalaisten_tie.SpouseExtended.profession AS spouse_profession,
  siirtokarjalaisten_tie.SpouseExtended.marriageyear AS marriageyear,
  siirtokarjalaisten_tie.SpouseExtended.birthplace AS spouse_birthplace,
  siirtokarjalaisten_tie.SpouseExtended.birthlatitude AS spouse_birthlatitude,
  siirtokarjalaisten_tie.SpouseExtended.birthlongitude AS spouse_birthlongitude,
  siirtokarjalaisten_tie.SpouseExtended.birthregion AS spouse_birthregion,
  siirtokarjalaisten_tie.SpouseExtended.birthday AS spouse_birthday,
  siirtokarjalaisten_tie.SpouseExtended.birthmonth AS spouse_birthmonth,
  siirtokarjalaisten_tie.SpouseExtended.birthyear AS spouse_birthyear,
  siirtokarjalaisten_tie.SpouseExtended.deathday AS spouse_deathday,
  siirtokarjalaisten_tie.SpouseExtended.deathmonth AS spouse_deathmonth,
  siirtokarjalaisten_tie.SpouseExtended.deathyear AS spouse_deathyear
  FROM siirtokarjalaisten_tie.PersonExtended LEFT JOIN siirtokarjalaisten_tie.SpouseExtended ON siirtokarjalaisten_tie.SpouseExtended.spouse = siirtokarjalaisten_tie.PersonExtended.id;

-- Living records with location data
CREATE VIEW siirtokarjalaisten_tie.LivingPlace AS
  SELECT Place.name, Place.latitude, Place.longitude, Place.region, person, movedin, movedout
  FROM siirtokarjalaisten_tie.LivingRecord INNER JOIN siirtokarjalaisten_tie.Place ON siirtokarjalaisten_tie.Place.id = siirtokarjalaisten_tie.LivingRecord.place;