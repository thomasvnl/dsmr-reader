from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class BackendSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    RETENTION_NONE = None
    RETENTION_WEEK = 1
    RETENTION_MONTH = 4
    RETENTION_HALF_YEAR = 26
    RETENTION_YEAR = 52
    RETENTION_CHOICES = (
        (RETENTION_NONE, _('None (keep all readings)')),
        (RETENTION_WEEK, _('Discard most readings after one week')),
        (RETENTION_MONTH, _('Discard most readings after one month')),
        (RETENTION_HALF_YEAR, _('Discard most readings after six months')),
        (RETENTION_YEAR, _('Discard most readings after one year')),
    )

    data_retention_in_weeks = models.IntegerField(
        blank=True,
        null=True,
        default=RETENTION_NONE,
        choices=RETENTION_CHOICES,
        verbose_name=_('Data retention'),
        help_text=_(
            'By default the application stores all readings taken. As there is a DSMR-reading every ten seconds, this '
            'results in over three million readings each year. This may or may not cause degraded performance in your '
            'setup used. For that reason you may want to apply retention to this data. Please note that enabling this '
            'feature will NOT discard ALL readings, as it will PRESERVE the first reading of each hour.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Backend configuration')
