from celery.task import task
from lectures.models import Lecture

@task
def add(x, y):
    return x + y

@task
def set_lecture_to_finished(lecture_id):
    try:
        lecture = Lecture.objects.get(id=lecture_id)
        lecture.state = 'f'
        lecture.save();
        
        return True
    except:
        return False
    
