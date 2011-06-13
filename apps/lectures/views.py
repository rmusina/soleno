from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from lectures.forms import LectureCreateForm
from lectures.models import Lecture, NotesUpdate

from django.http import Http404

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
    try:
        current_lecture = Lecture.objects.get(id=lecture_id)
    except:
        raise Http404
    
    if request.is_ajax():
        if request.method == 'GET':
            update_id = request.GET.get("id", None)
            requested_update = NotesUpdate.objects.get(id=update_id)           
            
            if requested_update is not None:
                return HttpResponse(requested_update.text)
            else:
                return HttpResponse("There are no user notes with your specified id.")
        if request.method == 'POST':
            try:
                data = request.POST.get("data", None)
                
                if data is not None and data != "":                
                    new_update = NotesUpdate(lecture = current_lecture,
                                             created_by = request.user,
                                             text = data)
                    new_update.save()
                    
                    return HttpResponse("Save successful")
                else:
                    return HttpResponse("Your input is empty or inexistent")
            except:
                return HttpResponse("There was a server error while trying to process your request")
    
    return render_to_response(template_name, {
                                    'lecture': current_lecture,
                                    'updates_list': NotesUpdate.objects.filter(lecture=current_lecture).select_related('created_by', 'saved_at')
                              },                              
                              context_instance=RequestContext(request))