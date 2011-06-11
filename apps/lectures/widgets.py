from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings

class SliderWidget(forms.TextInput):
    
    def render(self, name, value, attrs=None):
        return mark_safe(u"""
            <div id="slider_container">
                <input id="id_lecture_duration" name="lecture_duration" type="hidden"/>
                <div id="current_value"></div>
                <div id="slider-range-min"></div>
            </div>
            """)
    
    class Media:
        css = {
               'all': ('http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.13/themes/sunny/jquery-ui.css', settings.STATIC_URL + 'lectures/widgets/css/slider.css',)
        }
        js = ('http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.13/jquery-ui.min.js', 
              settings.STATIC_URL + 'lectures/widgets/js/slider.js',)
        

        
            