from django import forms

from django.utils.translation import ugettext_lazy as _
from lectures.widgets import SliderWidget
from lectures.models import Lecture

class LectureCreateForm(forms.Form):
    
    lecture_title = forms.CharField(label = _("Lecture Title"), max_length = 30)
    lecture_description = forms.CharField(label = _("Lecture Description"), max_length = 200, widget = forms.widgets.Textarea())
    lecture_duration = forms.IntegerField(label = _("Lecture Duration (minutes)"), widget = SliderWidget())
    
    def save(self, user):
        lecture_title = self.cleaned_data['lecture_title']
        lecture_description = self.cleaned_data['lecture_description']
        lecture_duration = self.cleaned_data['lecture_duration']
        
        new_lecture = Lecture(created_by=user, 
                              title=lecture_title, 
                              description=lecture_description, 
                              duration=lecture_duration, 
                              state='a') #corresponds to active state
        new_lecture.save()
        
        return new_lecture        