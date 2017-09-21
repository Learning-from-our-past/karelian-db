import json


class TestUserApi:

    def should_return_json_object_of_one_user(self, app):
        # TODO: This is just an example test for API. User endpoint will change to something more sensible :)
        response = app.get('/user')
        data = json.loads(response.get_data(as_text=True))
        assert data['id'] == 0

    def should_do_other_stuff(self):
        assert True is True