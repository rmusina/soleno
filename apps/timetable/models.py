from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from lectures.models import Lecture

class TimetableEntry(models.Model):
    user = models.ForeignKey(User, verbose_name=_('created by'))
    lecture = models.ForeignKey(Lecture, verbose_name=_('lecture attending'))
        
    class Meta:
        verbose_name = _('timetable Entry')
        verbose_name_plural = _('timetable Entries')