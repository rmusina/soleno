from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from lectures.forms import LectureCreateForm
from lectures.models import Lecture, NotesUpdate
from avatar.templatetags.avatar_tags import avatar
from avatar.forms import avatar_img

from django.http import Http404

import tornado.web
from django_tornado.decorator import asynchronous

import datetime

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

class UpdatesController():
    listeners = []
    cache = []
    cache_size = 200
        
    def wait_for_updates(self, callback, listenerId=None):

        if listenerId:
            index = 0
            for i in xrange(len(self.cache)):
                index = len(self.cache) - i - 1
                if self.cache[index]["id"] == listenerId : break
            recent = self.cache[index + 1:]
            if recent:
                callback(recent)
                return
        self.listeners.append(callback)   
        
    def new_updates(self, updates): 
        print "Sending new message to %r listeners" % len(self.listeners)
        
        for callback in self.listeners:
            try:
                callback(updates)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        self.listeners = []
        self.cache.extend(updates)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]

updatesController = UpdatesController()

@login_required
def lecture_session_new(request, lecture_id):
    print "new " + lecture_id
    
    try:
        current_lecture = Lecture.objects.get(id=lecture_id)
    except:
        raise Http404
    
    if request.is_ajax() and request.method == 'POST':
        try:
            data = request.POST.get("data", None)
            
            print data
                            
            if data is not None and data != "":                
                
                new_update = NotesUpdate(lecture = current_lecture,
                                         created_by = request.user,
                                         text = data)
                new_update.save()
                
                updatesController.new_updates([{"id": new_update.id,
                                                "created_by_username": request.user.username,
                                                "created_by_avatar_src": avatar(request.user, 32), 
                                                "saved_at": new_update.saved_at.strftime("%H:%M:%S"),
                                                }])
                
                return HttpResponse("Save successful")
            else:
                return HttpResponse("Your input is empty or inexistent")
        except:
            return HttpResponse("There was a server error while trying to process your request")
    
    raise Http404

@asynchronous
def lecture_session_updates(request, handler, lecture_id=None):
    
    def new_updates_callback(updates):
        if handler.request.connection.stream.closed():
            return
        print updates
        
        handler.finish({'updates' : updates})
            
    if request.is_ajax() and request.method == 'POST':
        listenerId = request.POST.get("listenerId", None)
        updatesController.wait_for_updates(handler.async_callback(new_updates_callback), listenerId=listenerId)

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
                
    return render_to_response(template_name, {
                                    'lecture': current_lecture,
                                    'updates_list': NotesUpdate.objects.filter(lecture=current_lecture).select_related('created_by', 'saved_at')
                              },                              
                              context_instance=RequestContext(request))