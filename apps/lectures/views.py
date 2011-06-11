from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from lectures.forms import LectureCreateForm
from lectures.models import Lecture

def lecture_list(request, template_name="lectures/lecture_list.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))

@login_required
def lecture_create(request, template_name="lectures/lecture_create.html"):
    
    if request.method == 'POST': 
        form = LectureCreateForm(request.POST) 
        if form.is_valid():     
            new_lecture = form.save(request.user)        
            return HttpResponseRedirect(reverse('lecture_session', args=(new_lecture.id,))) 
    else:
        form = LectureCreateForm() 

    return render_to_response(template_name, {
                                   'is_lecturer':request.user.get_profile().is_lecturer,             
                                   'form':form,
                              }, context_instance=RequestContext(request))

def lecture_detail(request, lecture_id, template_name="lectures/lecture_detail.html"):
    return render_to_response(template_name, context_instance=RequestContext(request))

@login_required
def lecture_session(request, lecture_id, template_name="lectures/lecture_session.html"):
    
    return render_to_response(template_name, {
                                    'lecture':Lecture.objects.get(id=lecture_id),
                              },                              
                              context_instance=RequestContext(request))