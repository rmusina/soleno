from django.contrib import admin
from lectures.models import Lecture, NotesUpdate, LectureKeyTerm

admin.site.register(Lecture)
admin.site.register(NotesUpdate)
admin.site.register(LectureKeyTerm)