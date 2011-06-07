from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

class Profile(models.Model):

    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length=50, null=False)
    specialization = models.CharField(_('Faculty/Major'),  max_length=50, null=False)
    university = models.CharField(_('university'), max_length=50, null=False)
    is_lecturer = models.BooleanField(_('is_lecturer'), editable=False)
    fields_of_interest = models.TextField(_('Fields of Interest'), null=True, blank=True)
    about = models.TextField(_('about'), null=True, blank=True)
      
    def __unicode__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return ('profile_detail', None, {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

def create_profile(sender, instance=None, **kwargs):
    if instance is None:
        return
    profile, created = Profile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User)

def user_created_handler(sender, created_user=None, is_lecturer=None, **kwargs):
    if created_user is None or is_lecturer is None:
        return
    
    profile = created_user.get_profile()
    profile.is_lecturer = is_lecturer
    profile.save()

from  account import signals
signals.user_created.connect(user_created_handler)
