from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.db.utils import OperationalError, ConnectionDoesNotExist
from django.db import connections

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_backup.models.settings import DropboxSettings, BackupSettings
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_notification.models.settings import NotificationSetting
from dsmr_weather.models.settings import WeatherSettings
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_weather.models.reading import TemperatureReading
from dsmr_stats.models.statistics import HourStatistics, DayStatistics
from dsmr_frontend.models.message import Notification
from dsmr_datalogger.models.reading import MeterStatistics, DsmrReading
from dsmr_api.models import APISettings
from dsmr_stats.models.note import Note


class Command(BaseCommand):
    help = _('Migrates the data inside a MySQL database of this project to a PostgreSQL database.')

    # As defined in migration settings.
    MYSQL_DB_KEY = 'default'
    POSTGRESQL_DB_KEY = 'target'

    OVERRIDE_MODELS = (
        APISettings, BackupSettings, DropboxSettings, ConsumptionSettings, DataloggerSettings, FrontendSettings,
        MinderGasSettings, NotificationSetting, WeatherSettings, EnergySupplierPrice, MeterStatistics, Notification
    )
    # These models will be skipped if their PK already exists.
    APPEND_MODELS = (
        Note, TemperatureReading, HourStatistics, DayStatistics, ElectricityConsumption, GasConsumption, DsmrReading
    )

    def handle(self, **options):
        self._test_databases()
        self._summary()
        self._migrate_override()
        self._migrate_resume()
        self._summary()

    def _test_databases(self):
        """ Tests connections first. """

        for current in (self.MYSQL_DB_KEY, self.POSTGRESQL_DB_KEY):
            try:
                connections[current].cursor()
            except ConnectionDoesNotExist:
                raise CommandError(_('Please run this command with --settings=dsmrreader.migration_settings'))
            except OperationalError as error:
                raise CommandError(error)

    def _summary(self):
        """ Summary of content in both database. """
        print()
        print('{:40} {:<20} {:<20}'.format('Data summary', 'Source count', 'Target count'))

        for current in self.OVERRIDE_MODELS + self.APPEND_MODELS:
            print('{:40} {:<20} {:<20}'.format(
                current.__name__,
                current.objects.using(self.MYSQL_DB_KEY).all().count(),
                current.objects.using(self.POSTGRESQL_DB_KEY).all().count(),
            ))

    def _migrate_override(self):
        print()
        print('Inserting or updating data')

        for current_model in self.OVERRIDE_MODELS:
            dataset = current_model.objects.using(self.MYSQL_DB_KEY).all()

            for current in dataset:
                print(' - {}'.format(current_model.__name__))
                current.save(using=self.POSTGRESQL_DB_KEY)

        print('Done')

    def _migrate_resume(self):
        print()
        print('Inserting or resuming data')

        for current_model in self.APPEND_MODELS:
            source_dataset = current_model.objects.using(self.MYSQL_DB_KEY).all().order_by('pk')

            print(' - {}'.format(current_model.__name__))

            try:
                # Resume. If possible.
                latest_at_target = current_model.objects.using(self.POSTGRESQL_DB_KEY).all().order_by('-pk')[0]
            except IndexError:
                pass
            else:
                print(' --- Resume @ #{}'.format(latest_at_target.pk))
                source_dataset = source_dataset.filter(pk__gt=latest_at_target.pk)

            print(' --- Processing {} item(s)'.format(source_dataset.count()))

            for current in source_dataset:
                current.save(using=self.POSTGRESQL_DB_KEY)

        print('Done')
