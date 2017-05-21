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

CREATE VIEW siirtokarjalaisten_tie."ChildWithParents" AS
  SELECT
    "Child".id,
    "Child"."firstName",
    "Child"."lastName",
    "Child"."sex",
    "Child"."birthYear",
    "Place"."name" as "birthPlace",
    "Place"."region" as "birthPlaceRegion",
    "father"."firstName" AS "father.firstName",
    "father"."lastName" AS "father.lastName",
    "father"."prevLastName" AS "father.prevLastName",
    "father"."birthDay" AS "father.birthDay",
    "father"."birthMonth" AS "father.birthMonth",
    "father"."birthYear" AS "father.birthYear",
    "father"."deathDay" AS "father.deathDay",
    "father"."deathMonth" AS "father.deathMonth",
    "father"."deathYear" AS "father.deathYear",
    "father".profession AS "father.profession",
    "father".sex  AS "father.sex",
    "father"."ownHouse" AS "father.ownHouse",
    "father"."returnedKarelia" AS "father.returnedKarelia",
    "father"."previousMarriages" AS "father.previousMarriages",
    "father"."pageNumber" AS "father.pageNumber",
    "father".birthplace AS "father.birthPlace",
    "father".birthlatitude AS "father.birthLatitude",
    "father".birthlongitude AS "father.birthLongitude",
    "father".birthregion AS "father.birthRegion",

    "mother"."firstName" AS "mother.firstName",
    "mother"."lastName" AS "mother.lastName",
    "mother"."prevLastName" AS "mother.prevLastName",
    "mother"."birthDay" AS "mother.birthDay",
    "mother"."birthMonth" AS "mother.birthMonth",
    "mother"."birthYear" AS "mother.birthYear",
    "mother"."deathDay" AS "mother.deathDay",
    "mother"."deathMonth" AS "mother.deathMonth",
    "mother"."deathYear" AS "mother.deathYear",
    "mother".profession AS "mother.profession",
    "mother".sex  AS "mother.sex",
    "mother"."ownHouse" AS "mother.ownHouse",
    "mother"."returnedKarelia" AS "mother.returnedKarelia",
    "mother"."previousMarriages" AS "mother.previousMarriages",
    "mother"."pageNumber" AS "mother.pageNumber",
    "mother".birthplace AS "mother.birthPlace",
    "mother".birthlatitude AS "mother.birthLatitude",
    "mother".birthlongitude AS "mother.birthLongitude",
    "mother".birthregion AS "mother.birthRegion",
    "father"."originalText" AS "originalText"
  FROM siirtokarjalaisten_tie."Child"
  LEFT JOIN siirtokarjalaisten_tie."PersonExtended" AS father
  ON "fatherId" = father.id
  RIGHT JOIN siirtokarjalaisten_tie."PersonExtended" AS mother
  ON "motherId" = mother.id
  join "Place" on "Child"."birthPlaceId" = "Place".id

-- Living records with location data
CREATE VIEW siirtokarjalaisten_tie."LivingPlace" AS
  SELECT "Place".name, "Place".latitude, "Place".longitude, "Place".region, "personId", "movedIn", "movedOut"
  FROM siirtokarjalaisten_tie."LivingRecord"
  INNER JOIN siirtokarjalaisten_tie."Place" ON siirtokarjalaisten_tie."Place".id = siirtokarjalaisten_tie."LivingRecord"."placeId";
