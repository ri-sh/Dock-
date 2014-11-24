from django.db import models
from datetime import datetime
from math import log, pow
from helper_functions import my_strftime
from helper_functions import relative_timestamp

# Create your models here.
class Post(models.Model):
    author = models.ForeignKey('userInfo.UserProfile', related_name='+')
    time_posted = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True)
    recipient = models.ForeignKey('userInfo.UserProfile', related_name='+')
    block = models.ForeignKey('BlockPages.BlockPage', null=True)
    votes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)

    def getDetail(self):
        """Returns dictionary object with basic info"""
        return { 'author' : self.author.getInfo(), 'recipient' : self.recipient.getInfo(), 'text' : self.text,
                'timestamp' : my_strftime(self.time_posted), 'type' : 'post', 'id' : self.id, 
                'num_comments' : len(self.comment_set.all()), 'relative_timestamp' : relative_timestamp(self.time_posted), 'score' : self.getScore() }

    def getScore(self):
        """
        Calculates the 'score' of this post
        score = (.1*views + num_comments) / log(time_elapsed+1)
        """
        elapsed = datetime.now() - self.time_posted
        return (.1*self.views + len(self.comment_set.all())) + (10**3)*pow(.001 + elapsed.seconds, -.5)

    def getComments(self):
        """Returns list of info about this post's comments"""
        #Increment number of views for this post
        self.views = self.views + 1
        self.save()
        return [ comment.getDetail() for comment in self.comment_set.all() ]

class Comment(models.Model):
    post = models.ForeignKey(Post)
    author = models.ForeignKey('userInfo.UserProfile')
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True)
    votes = models.IntegerField(default=0)

    def getDetail(self):
        """Returns dictionary object containing detail about this comment"""
        return { 'author' : self.author.getInfo(), 'text' : self.text, 'votes' : self.votes,
                'timestamp' : my_strftime(self.time_created), 'type' : 'comment',
                'relative_timestamp' : relative_timestamp(self.time_created) }
