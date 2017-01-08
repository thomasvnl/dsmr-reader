from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_datalogger.models.settings import DataloggerSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = DataloggerSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(DataloggerSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_track(self):
        self.assertTrue(self.instance.track)

    def test_track_meter_statistics(self):
        self.assertTrue(self.instance.track_meter_statistics)

    def test_track_phases(self):
        self.assertFalse(self.instance.track_phases)

    def test_verify_telegram_crc(self):
        self.assertTrue(self.instance.verify_telegram_crc)

    def test_dsmr_version(self):
        self.assertEqual(self.instance.dsmr_version, DataloggerSettings.DSMR_VERSION_4)

    def test_com_port(self):
        self.assertEqual(self.instance.com_port, '/dev/ttyUSB0')
