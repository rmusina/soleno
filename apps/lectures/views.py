from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ugettext

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils import simplejson

from lectures.forms import LectureCreateForm
from lectures.models import Lecture, NotesUpdate, LectureKeyTerm
from avatar.templatetags.avatar_tags import avatar

from django.http import Http404
from django.db.models import Max

import tornado.web
from django_tornado.decorator import asynchronous

from nltk.corpus import wordnet as wn

from soleno.tasks import set_lecture_to_finished
from datetime import datetime, timedelta

import operator
import urllib
import xml.dom.minidom as xmlParser
    
def connect_to_session(session_no, request):
    try:
        nr = int(session_no)
        lecture = Lecture.objects.get(id=nr)
        if lecture.state == 'a':
            return HttpResponseRedirect(reverse("lecture_session", args=[nr]))
        else:
            return HttpResponseRedirect(reverse("lecture_detail", args=[nr]))
    except:
        pass
    
    request.user.message_set.create(message=ugettext(u"The lecture does not exist")) 
    
    return HttpResponseRedirect(reverse("lecture_list"))
    
def lecture_list(request, template_name="lectures/lecture_list.html"):
    session_no = request.GET.get('quick_connect', '')
    if session_no:
        return connect_to_session(session_no, request)
    
    lectures = Lecture.objects.all()
    keywords = LectureKeyTerm.objects.order_by('?')[:20]   
    
    search_terms = request.GET.get('search', '')
    print search_terms
    
    if search_terms:
        search_keywords = LectureKeyTerm.objects.filter(key_term=search_terms).values("lecture")
        lectures = lectures.filter(Q(title__icontains=search_terms) | 
                                   Q(id__in=search_keywords))
    
    return render_to_response(template_name, {
                                    'lectures': lectures,
                                    'keywords': keywords,
                              },                              
                              context_instance=RequestContext(request))

@login_required
def lecture_create(request, template_name="lectures/lecture_create.html"):
    
    if request.method == 'POST': 
        form = LectureCreateForm(request.POST) 
        if form.is_valid():     
            new_lecture = form.save(request.user) 

            session_expiration_date = datetime.now() + timedelta(minutes=new_lecture.duration)     
            set_lecture_to_finished.apply_async(args=[new_lecture.id, ], eta=session_expiration_date)
             
            return HttpResponseRedirect(reverse('lecture_session', args=(new_lecture.id,))) 
    else:
        form = LectureCreateForm() 

    return render_to_response(template_name, {
                                   'is_lecturer':request.user.get_profile().is_lecturer,             
                                   'form':form,
                              }, context_instance=RequestContext(request))

def lecture_detail(request, lecture_id, template_name="lectures/lecture_detail.html"):
    try:
        current_lecture = Lecture.objects.get(id=lecture_id)
    except:
        current_lecture = None
    
    #lecture_notes = NotesUpdate.objects.filter(lecture=current_lecture)
    #if lecture_notes:
    lecture_notes = None
    lecture_participants = 0;
    
    if current_lecture:
        try:
            session_notes = NotesUpdate.objects.filter(lecture=current_lecture)
            distinct_users = session_notes.values_list('created_by').distinct()
            
            lecture_notes = []
            for user in distinct_users:
                lecture_notes.append(session_notes.filter(created_by=user[0]).annotate(most_recent=Max('saved_at')).order_by('-most_recent')[0])
            
            lecture_participants = len(lecture_notes)
        except:
            pass
        
    
    return render_to_response(template_name, {
                                    'current_lecture': current_lecture,
                                    'lecture_notes': lecture_notes,
                                    'lecture_participants' : lecture_participants,
                              },
                              context_instance=RequestContext(request))

def lecture_note_details(request, lecture_id, note_id, template_name="lectures/lecture_note_detail.html"):
    try:
        lecture_note = NotesUpdate.objects.get(id=note_id)
        lecture_id_int = int(lecture_id)
    except:
        lecture_note = None
    
    is_me = False    
    if lecture_note and lecture_note.lecture.id != lecture_id_int:
        lecture_note = None
    else:
        is_me = request.user == lecture_note.created_by
    
    return render_to_response(template_name, {
                                    'lecture_note' : lecture_note,
                                    'is_me' : is_me,
                              },
                              context_instance=RequestContext(request))

class UpdatesController():
    listeners = {}
    cache = []
    cache_size = 200
        
    def wait_for_updates(self, callback, listener_id=None, lecture_id=None):
        if not lecture_id:
            return;
        
        if not self.listeners.has_key(lecture_id):
            self.listeners[lecture_id] = []
        
        self.listeners[lecture_id].append(callback)   
        
    def new_updates(self, updates, lecture_id): 
        print "Sending new message to %r listeners" % len(self.listeners[lecture_id])
        
        for callback in self.listeners[lecture_id]:
            try:
                callback(updates)
            except:
                logging.error("Error in waiter callback", exc_info=True)
                
        self.listeners[lecture_id] = []
        self.cache.extend(updates)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]

updatesController = UpdatesController()

@login_required
def lecture_session(request, lecture_id=None, template_name="lectures/lecture_session.html"):
    try:
        current_lecture = Lecture.objects.get(id=lecture_id)
    except:
        render_to_response(template_name, context_instance=RequestContext(request))
    
    if request.is_ajax():
        if request.method == 'GET':
            update_id = request.GET.get("id", None)
            requested_update = NotesUpdate.objects.get(id=update_id)           
            
            if requested_update is not None:
                return HttpResponse(requested_update.text)
            else:
                return HttpResponse("There are no user notes with your specified id.")
    updates_list = []
    user_text = ""
    
    try:
        session_notes = NotesUpdate.objects.filter(lecture=current_lecture);
        updates_list = session_notes.select_related('created_by', 'saved_at');
        user_text = session_notes.filter(created_by=request.user).annotate(most_recent=Max('saved_at')).order_by('-most_recent')[0].text
    except:
        pass
    
    return render_to_response(template_name, {                                              
                                    'user_text': user_text,
                                    'lecture': current_lecture,
                                    'updates_list': updates_list,
                              },                              
                              context_instance=RequestContext(request))

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
                                        
            if data is not None and data != "":                
                
                new_update = NotesUpdate(lecture = current_lecture,
                                         created_by = request.user,
                                         text = data)
                new_update.save()
                
                updatesController.new_updates([{"id": new_update.id,
                                                "created_by_username": request.user.username,
                                                "created_by_avatar_src": avatar(request.user, 32), 
                                                "saved_at": new_update.saved_at.strftime("%H:%M:%S"),
                                                }],
                                                lecture_id)
                
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
        listener_id = request.POST.get("listenerId", None)
        updatesController.wait_for_updates(handler.async_callback(new_updates_callback), listener_id=listener_id, lecture_id=lecture_id)

def get_similarity_rating(word1, pos1, word2, pos2):
    #print "similarity for " + word1 + " " + word2 
    
    try:
        word1_synset = wn.synsets(word1, pos=pos1.lower())
        word2_synset = wn.synsets(word2, pos=pos2.lower())
        
        similarity = word1_synset[0].lch_similarity(word2_synset[0])
        
        if similarity == 0:
            return 1
        else:
            return similarity 
    except:
        return 1

def search_in_session(expression, session_keywords):
    #print "searching for " + expression 
        
    try:
        return session_keywords.get(key_term=expression)
    except: 
        return None 

def get_maximum_similarity_rating(expression, parts_of_speech, session_keywords):
    words = expression.split(" ")
    max_similarity_rating = 0
    
    #print"in get_maximum_similarity_rating"
    
    session_expression = search_in_session(expression, session_keywords)
    
    if session_expression is not None:
        return session_expression.similarity_rating
    
    for i in range(len(words) - 1):
        for j in range(i+1, len(words)):
            rating = get_similarity_rating(words[i], 
                                           parts_of_speech[words[i]],
                                           words[j],
                                           parts_of_speech[words[j]])
            if rating > max_similarity_rating:
                max_similarity_rating = rating
    
    return max_similarity_rating

def get_global_rating(max_rating, occurrence, is_highlighted):
    global_rating = max_rating * occurrence
    
    if is_highlighted:
        global_rating *= 1.5
        
    return global_rating

def store_in_session(expression, 
                     similarity_rating,
                     occurrence,
                     is_highlighted,
                     current_lecture,
                     session_keywords):
    
    #print "in store_in_session"
    key_term = search_in_session(expression, session_keywords)
    
    if key_term is None:
        key_term = LectureKeyTerm(lecture = current_lecture,
                                  key_term = expression,   
                                  similarity_rating = similarity_rating,
                                  frequency = occurrence,
                                  is_highlighted = is_highlighted,   
                                  ttl = 4) 
    else: 
        key_term.frequency = (key_term.frequency + occurrence)/2;
        key_term.similarity_rating = (key_term.similarity_rating + similarity_rating)/2;
        key_term.ttl += 1
        if is_highlighted:
            key_term.is_highlighted = True 
    
    key_term.save()
    
def decrement_ttl(current_lecture):
    session_keywords = LectureKeyTerm.objects.filter(lecture=current_lecture)
    
    #print "in decrement_ttl"
    
    for key_term in session_keywords:
        key_term.ttl -= 1
        
        if key_term.ttl <= 0:
            key_term.delete()
        else:
            key_term.save()

def get_sorted_tuple(dictionary):
    return sorted(dictionary.iteritems(), key=operator.itemgetter(1), reverse=True)

def process_keywords(occurrences, parts_of_speech, is_highlighted, current_lecture):
    similarity_ratings = {}
    
    session_keywords = LectureKeyTerm.objects.filter(lecture=current_lecture)
    
    #print "in process_keywords"
            
    for (expression, occurrence) in occurrences.iteritems():
        similarity_rating = get_maximum_similarity_rating(expression, parts_of_speech, session_keywords)    
        
        similarity_ratings[expression] = round(get_global_rating(similarity_rating, occurrence, is_highlighted[expression]), 2)
        store_in_session(expression,
                         similarity_rating, 
                         occurrence, 
                         is_highlighted[expression],
                         current_lecture,
                         session_keywords)
    
    decrement_ttl(current_lecture)
    
    return get_sorted_tuple(similarity_ratings)

def getText(nodelist):
    result_list = []
    for node in nodelist:
        for textNode in node.childNodes:
            text = ""
            if textNode.nodeType == node.TEXT_NODE:
                text += textNode.data
        if text not in result_list:
            result_list.append(text)
    return result_list

def fetch_image_for_tags(tags, no_images):
    query_string = "http://nopsa.hiit.fi/pmg/index.php/api/search?apikey=8B4A21D09ECCBF43&tags=%2B" + "+".join(tags.split(" ")) + \
                   "&order_attr=relevancy&mode=any&per_page="+ str(no_images) + \
                   "&page=1&encoding=html&output_type=xml&yt1=Query"
    data = urllib.urlopen(query_string).read()
    
    dom = xmlParser.parseString(data)
    images = getText(dom.getElementsByTagName("baseName"))
    
    fetched_images = []
    for image in images:
        fetched_images.append("<img src=\"http://nopsa.hiit.fi/images/%s\"></img>" % (image))
    
    return fetched_images     

def fetch_images(similarity_ratings):
    image_list = []
    
    for (tag, score) in similarity_ratings:
        images = fetch_image_for_tags(tag, 5);
        for image in images:
            if image not in image_list:
                image_list.append(image)
    
    return image_list

@login_required
def lecture_session_keywords(request, lecture_id=None):
    try:
        current_lecture = Lecture.objects.get(id=lecture_id)
    except:
        raise Http404    
    
    if request.is_ajax() and request.method == 'POST':
        occurrences = simplejson.loads(request.POST.get("occurrences", None))
        parts_of_speech = simplejson.loads(request.POST.get("parts_of_speech", None))
        is_highlighted = simplejson.loads(request.POST.get("is_highlighted", None))
        
        if occurrences is not None and parts_of_speech is not None:
            similarity_ratings = process_keywords(occurrences, parts_of_speech, is_highlighted, current_lecture)
            fetched_images = fetch_images(similarity_ratings)
            
            return HttpResponse(simplejson.dumps( {"similarity_ratings" : similarity_ratings,
                                                   "fetched_images": fetched_images }));        
        else:
            return HttpResponseBadRequest()
    
    raise Http404

   
