from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

#for now only active and finished states will be used; created and pending will correspond to scheduled tasks
LECTURE_STATES = (
    ('c', 'created'),
    ('a', 'active'),   
    ('f', 'finished'),
    ('p', 'pending'),
);

class Lecture(models.Model):
    created_by = models.ForeignKey(User, verbose_name=_('created by'))
    title = models.CharField(_('lecture title'), max_length=100)
    description = models.TextField(_('lecture description'), max_length=200)
    duration = models.IntegerField(_('lecture duration'))
    created_at = models.DateTimeField(_('lecture creation time'), auto_now_add=True)
    state = models.CharField(_('lecture state'), max_length=1, choices=LECTURE_STATES)
        
    class Meta:
        verbose_name = _('lecture')
        verbose_name_plural = _('lectures')
        
class LectureKeywords(models.Model):
    lecture = models.ForeignKey(Lecture, verbose_name=_('lecture'))
    keyword = models.TextField(_('keyword'))        
        
class NotesUpdate(models.Model):
    lecture = models.ForeignKey(Lecture, verbose_name=_('lecture'))
    created_by = models.ForeignKey(User, verbose_name=_('created by'))
    text = models.TextField(_('note text'), max_length=5000)
    saved_at = models.DateTimeField(_('saved at'), auto_now_add=True)
        
    class Meta:
        verbose_name = _('Notes Update')
        verbose_name_plural = _('Notes Updates')