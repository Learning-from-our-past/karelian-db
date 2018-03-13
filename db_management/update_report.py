import datetime

from common.siirtokarjalaistentie_models import *


class UpdateReportService:

    def __init__(self):
        self._filename = None
        self._changed_records_counts = {}
        self._record_counts_at_beginning = {}
        self._record_counts_after_update = {}
        self._ignored_records_counts = {}
        self._comment = ''

    def _get_counts_of_tables(self):
        counts = {'Person': Person.select(Person.id).count(), 'Child': Child.select(Child.id).count(),
                  'LivingRecord': LivingRecord.select(LivingRecord.id).count(),
                  'Marriage': Marriage.select(Marriage.id).count(), 'Page': Page.select(Page.id).count(),
                  'Place': Place.select(Place.id).count(), 'Profession': Profession.select(Profession.id).count()}

        return counts

    def _initialize_counts_to_zero(self):
        counts = {'Person': 0, 'Child': 0, 'LivingRecord': 0, 'Marriage': 0, 'Page': 0, 'Place': 0, 'Profession': 0}

        return counts

    def setup(self, filename):
        self._filename = filename
        self._record_counts_at_beginning = self._get_counts_of_tables()
        self._changed_records_counts = self._initialize_counts_to_zero()
        self._record_counts_after_update = self._initialize_counts_to_zero()
        self._ignored_records_counts = self._initialize_counts_to_zero()

    def changed_record_in(self, table_name):
        self._changed_records_counts[table_name] += 1

    def ignored_record_in(self, table_name, count=1):
        self._ignored_records_counts[table_name] += count

    def save_report(self):
        self._record_counts_after_update = self._get_counts_of_tables()

        for key, value in self._record_counts_after_update.items():
            self._record_counts_after_update[key] -= self._record_counts_at_beginning[key]

        m = KairaUpdateReportModel(
            time=datetime.datetime.utcnow(),
            kairaFileName=self._filename,
            changedRecordsCount=self._changed_records_counts,
            recordCountChange=self._record_counts_after_update,
            ignoredRecordsCount=self._ignored_records_counts,
            comment=self._comment
        )

        m.save()



update_report = UpdateReportService()
