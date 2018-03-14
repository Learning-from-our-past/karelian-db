import os
on_ci = 'CI' in os.environ

if on_ci:
    class TestOnCI:
        def should_have_anonymize_setting_on_in_database_config(self):
            """
            Check the value to prevent wrong setting being merged to the master.
            Check that the source code has correct setting of having anonymize true. Can't check the value by importing
            module since the value could have been changed during tests.
            """
            config_file = open('db_management/database_config.py')
            file_contents = config_file.read()
            assert file_contents.find('"anonymize": True,') != -1
