from django.db import models
from django.contrib.auth.models import User
from helper_functions import my_strftime

# Create your models here.

#This only contains metadata about this thread (i.e. just the subject for now)
#It is used in a Many-to-Many relationship with User, with a through object that contains the has_been_read flag
class Thread(models.Model):
    subject = models.CharField(max_length=64)

    def getThread(self):
        """Returns list of most recent messages with corresponding info"""
        return [message.getDetail() for message in self.message_set.order_by('time_sent')]

    def getThreadInfo(self, user=None):
        """
        Returns dictionary object containing basic info about thread,
        such as most recent message/author, title, etc.
        """
        if user == None:
            has_been_read = False
        else:
            has_been_read = ThreadMembership.objects.get(user=user, thread=self).has_been_read

        last_message = self.message_set.order_by('-time_sent')[0]
        return { 'subject' : self.subject, 'last_message' : last_message.getDetail(), 'id' : self.id, 
                'has_been_read' : has_been_read }

class Message(models.Model):
    thread = models.ForeignKey(Thread)
    user = models.ForeignKey('userInfo.UserProfile') #the author of this message
    time_sent = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def getDetail(self):
        """Returns dictionary object containing the info of this object"""
        return { 'author' : self.user.getInfo(),
                'timestamp' : my_strftime(self.time_sent),
                'text' : self.text }

class ThreadMembership(models.Model):
    user = models.ForeignKey('userInfo.UserProfile')
    thread = models.ForeignKey(Thread)

    #Meta data for user's relation to thread
    has_been_read = models.BooleanField(default=False)
