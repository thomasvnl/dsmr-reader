from distutils.version import StrictVersion
import re

from django.db.models.functions import TruncHour
from django.db.models import Count
from django.utils import timezone
from django.conf import settings
import requests

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_backend.models.settings import BackendSettings
from dsmr_datalogger.models.reading import DsmrReading


def get_capabilities(capability=None):
    """
    Returns the capabilities of the data tracked, such as whether the meter supports gas readings or
    if there have been any readings regarding electricity being returned.

    Optionally returns a single capability when requested.
    """
    capabilities = {
        # We rely on consumption because DSMR readings might be flushed in the future.
        'electricity': ElectricityConsumption.objects.exists(),
        'electricity_returned': ElectricityConsumption.objects.filter(
            # We can not rely on meter positions, as the manufacturer sometimes initializes meters
            # with testing data. So we just have to wait for the first power returned.
            currently_returned__gt=0
        ).exists(),
        'gas': GasConsumption.objects.exists(),
        'weather': WeatherSettings.get_solo().track and TemperatureReading.objects.exists()
    }
    capabilities['any'] = any(capabilities.values())

    # Single selection.
    if capability is not None:
        return capabilities[capability]

    return capabilities


def is_latest_version():
    """ Checks whether the current version is the latest one available on Github. """
    response = requests.get(settings.DSMR_LATEST_VERSION_FILE)

    local_version = '{}.{}.{}'.format(* settings.DSMR_RAW_VERSION[:3])
    remote_version = re.search(r'^VERSION = \((\d+), (\d+), (\d+),', str(response.content, 'utf-8'), flags=re.MULTILINE)
    remote_version = '.'.join(remote_version.groups())

    return StrictVersion(local_version) >= StrictVersion(remote_version)


def apply_data_retention():
    """
    When data retention is enabled, this discards all data applicable for retention. Keeps at least one data point per
    hour available.
    """
    backend_settings = BackendSettings.get_solo()

    if backend_settings.data_retention_in_weeks is None:
        # No retention enabled at all (default behaviour).
        return

    # Required to prevent the first run for data rich environments to block the application entirely.
    MAX_HOURS_CLEANUP = 24

    # These models should be rotated with retention. Dict value is the datetime field used.
    MODELS_TO_CLEANUP = {
        DsmrReading.objects.processed(): 'timestamp',
        ElectricityConsumption.objects.all(): 'read_at',
    }

    retention_date = timezone.now() - timezone.timedelta(weeks=backend_settings.data_retention_in_weeks)

    for base_queryset, datetime_field in MODELS_TO_CLEANUP.items():

        hours_to_cleanup = base_queryset.filter(
            **{'{}__lt'.format(datetime_field): retention_date}
        ).annotate(
            item_hour=TruncHour(datetime_field)
        ).values('item_hour').annotate(
            item_count=Count('id')
        ).order_by().filter(
            item_count__gt=1
        ).order_by('item_hour').values_list(
            'item_hour', flat=True
        )[:MAX_HOURS_CLEANUP]

        for current_hour in hours_to_cleanup:
            # Fetch all data per hour.
            data_set = base_queryset.filter(
                **{
                    '{}__gte'.format(datetime_field): current_hour,
                    '{}__lt'.format(datetime_field): current_hour + timezone.timedelta(hours=1),
                }
            ).order_by()

            # Extract the first item, so we can exclude it.
            keeper_pk = data_set[0].pk

            # Now drop all others.
            data_set.exclude(pk=keeper_pk).delete()
