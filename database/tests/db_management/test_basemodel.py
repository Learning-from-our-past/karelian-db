import pytest
import tests.utils.population_utils as population_utils
from db_management.models.db_siirtokarjalaistentie_models import *
from tests.utils.dbUtils import DBUtils


@pytest.yield_fixture(autouse=True, scope='module', name='person_data')
def populate_person_information_to_db(database):
    DBUtils.truncate_db()
    # Person data is anonymized and tweaked and only usable for software testing.
    return population_utils.populate_from_json(database, "./tests/populate/data/person2.json")[0]

class TestGetEditableFields:

    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def should_not_return_fields_edited_by_human(self, person, researcher_connection):
        with Using(researcher_connection, [Person]):
            # Save change to user with researcher user's connection
            person.firstName = 'Kalle'
            person.save()

        person = Person.get(Person.id == person.id)
        fields = person.get_editable_fields()

        assert 'firstName' not in fields
        assert 'lastName' in fields

    def should_throw_error_for_model_with_no_edit_logs(self):
        page = Page.get()

        with pytest.raises(AttributeError):
            page.get_editable_fields()

    def should_return_none_for_empty_editlog(self):
        person = Person()
        person.editLog = {}
        assert person.get_editable_fields() is None


class TestGetNonEditableFields:

    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def should_return_fields_edited_by_human(self, person, researcher_connection):
        with Using(researcher_connection, [Person]):
            # Save change to user with researcher user's connection
            person.firstName = 'Kalle'
            person.save()

        person = Person.get(Person.id == person.id)
        fields = person.get_non_editable_fields()

        assert 'firstName' in fields
        assert 'lastName' not in fields

    def should_throw_error_for_model_with_no_edit_logs(self):
        page = Page.get()

        with pytest.raises(AttributeError):
            page.get_non_editable_fields()

    def should_return_none_for_empty_editlog(self):
        person = Person()
        person.editLog = {}
        assert person.get_non_editable_fields() is None
