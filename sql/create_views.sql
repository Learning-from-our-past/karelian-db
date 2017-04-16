-- Person with birthdata
CREATE VIEW siirtokarjalaisten_tie."PersonExtended" AS
  SELECT
    "Person".id,
    "firstName",
    "lastName",
    "prevLastName",
    "birthDay",
    "birthMonth",
    "birthYear",
    "deathDay",
    "deathMonth",
    "deathYear",
    profession.name as profession,
    sex,
    "ownHouse",
    "returnedKarelia",
    "previousMarriages",
    "pageNumber",
    "originalText",
    "Place".name AS birthplace,
    "Place".latitude AS birthlatitude,
    "Place".longitude AS birthlongitude,
    "Place".region AS birthregion
  FROM siirtokarjalaisten_tie."Person"
    LEFT JOIN siirtokarjalaisten_tie."Profession" AS profession ON profession.id = siirtokarjalaisten_tie."Person"."professionId"
    LEFT JOIN siirtokarjalaisten_tie."Place" ON siirtokarjalaisten_tie."Place".id = siirtokarjalaisten_tie."Person"."birthPlaceId";

-- Main person with spouse data
CREATE VIEW siirtokarjalaisten_tie."PersonAndSpouse" AS
  SELECT
    "man".id AS "manId",
    "man"."firstName" AS "man.firstName",
    "man"."lastName" AS "man.lastName",
    "man"."prevLastName" AS "man.prevLastName",
    "man"."birthDay" AS "man.birthDay",
    "man"."birthMonth" AS "man.birthMonth",
    "man"."birthYear" AS "man.birthYear",
    "man"."deathDay" AS "man.deathDay",
    "man"."deathMonth" AS "man.deathMonth",
    "man"."deathYear" AS "man.deathYear",
    "man".profession AS "man.profession",
    "man".sex  AS "man.sex",
    "man"."ownHouse" AS "man.ownHouse",
    "man"."returnedKarelia" AS "man.returnedKarelia",
    "man"."previousMarriages" AS "man.previousMarriages",
    "man"."pageNumber" AS "man.pageNumber",
    "man".birthplace AS "man.birthPlace",
    "man".birthlatitude AS "man.birthLatitude",
    "man".birthlongitude AS "man.birthLongitude",
    "man".birthregion AS "man.birthRegion",

    "weddingYear",

    "woman".id AS "womanId",
    "woman"."firstName" AS "woman.firstName",
    "woman"."lastName" AS "woman.lastName",
    "woman"."prevLastName" AS "woman.prevLastName",
    "woman"."birthDay" AS "woman.birthDay",
    "woman"."birthMonth" AS "woman.birthMonth",
    "woman"."birthYear" AS "woman.birthYear",
    "woman"."deathDay" AS "woman.deathDay",
    "woman"."deathMonth" AS "woman.deathMonth",
    "woman"."deathYear" AS "woman.deathYear",
    "woman".profession AS "woman.profession",
    "woman".sex  AS "woman.sex",
    "woman"."ownHouse" AS "woman.ownHouse",
    "woman"."returnedKarelia" AS "woman.returnedKarelia",
    "woman"."previousMarriages" AS "woman.previousMarriages",
    "woman"."pageNumber" AS "woman.pageNumber",
    "woman".birthplace AS "woman.birthPlace",
    "woman".birthlatitude AS "woman.birthLatitude",
    "woman".birthlongitude AS "woman.birthLongitude",
    "woman".birthregion AS "woman.birthRegion",
    "man"."originalText" AS "originalText"
  FROM siirtokarjalaisten_tie."Marriage"
  LEFT JOIN siirtokarjalaisten_tie."PersonExtended" AS man
  ON "manId" = man.id
  RIGHT JOIN siirtokarjalaisten_tie."PersonExtended" AS woman
  ON "womanId" = woman.id


-- Living records with location data
CREATE VIEW siirtokarjalaisten_tie."LivingPlace" AS
  SELECT "Place".name, "Place".latitude, "Place".longitude, "Place".region, "personId", "movedIn", "movedOut"
  FROM siirtokarjalaisten_tie."LivingRecord"
  INNER JOIN siirtokarjalaisten_tie."Place" ON siirtokarjalaisten_tie."Place".id = siirtokarjalaisten_tie."LivingRecord"."placeId";
