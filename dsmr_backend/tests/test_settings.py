from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_backend.models.settings import BackendSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = BackendSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(BackendSettings))

    def test_data_retention_in_weeks(self):
        self.assertIsNone(self.instance.data_retention_in_weeks)
