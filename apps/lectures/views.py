from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils import simplejson

from lectures.forms import LectureCreateForm
from lectures.models import Lecture, NotesUpdate, LectureKeyTerm
from avatar.templatetags.avatar_tags import avatar

from django.http import Http404

import tornado.web
from django_tornado.decorator import asynchronous

from nltk.corpus import wordnet as wn

import operator
import urllib
import xml.dom.minidom as xmlParser
    
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
def lecture_session(request, lecture_id=None, template_name="lectures/lecture_session.html"):
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

   
