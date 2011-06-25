from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

def user_timetable(request, template_name="timetables/user_timetable.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))
