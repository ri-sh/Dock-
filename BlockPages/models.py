from django.db import models
from datetime import datetime
from datetime import timedelta
from math import pow
from helper_functions import my_strftime
from helper_functions import relative_timestamp

# Create your models here.
class BlockPage(models.Model):
    """
    This model is a place-holder of sorts for a particular block. When a user
    enters a block, their current_block entry is set to the BlockPage corresponding
    to the (x,y) grid they fall into. If the BlockPage doesn't exist, it is created
    """

    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    
    #Optional latitude, longitude values of lower left corner of block
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    views = models.IntegerField(default=0)

    def getActivity(self, user=None, offset=0, num_results=10):
        """
        Returns dictionary with list of dictionary objects describing the posts/events
        for this block and the 8 blocks immediately surrounding it
        along with general info about this block
        """
        #Increment number of times this page has been viewed
        self.views = self.views + 1
        self.save()

        try:
            offset = int(offset) #Make sure its an integer
        except ValueError:
            #Default it to 0
            offset = 0
        try:
            num_results = int(num_results) #Make sure its an integer
        except ValueError:
            #Default it to 10
            num_results = 10

        num_results = 10
        activity = []

        for x in range(self.x_coordinate-1,self.x_coordinate+2):
            for y in range(self.y_coordinate-1,self.y_coordinate+2):
                #Get block for these coordinates if it exists
                try:
                    hold = BlockPage.objects.get(x_coordinate=x, y_coordinate=y)

                    #Add events
                    activity.extend([ event.getDetail(user=user) for event in hold.blockevent_set.filter(time_created__gt=datetime.now()+timedelta(hours=-24)).order_by('-time_created')[0:offset+num_results]])
        
                    #Add posts to activity
                    activity.extend([ post.getDetail() for post in hold.post_set.filter(time_posted__gt=datetime.now()+timedelta(hours=-24)).order_by('-time_posted')[0:offset+num_results] ])
                except BlockPage.DoesNotExist:
                    pass    #Nothing is in this block, just move on
                    
        #Within this set of 10, sort them in descending order by their 'score'
        activity = sorted(activity, key=lambda item: -1*item['score'])[offset:offset+num_results]

        return { 'success' : 1, 'activity' : activity, 'offset' : offset, 'size' : len(activity) }

class BlockPost(models.Model):
    #Foreign key to Block posted to
    block_page = models.ForeignKey(BlockPage)

    author = models.ForeignKey('userInfo.UserProfile')
    time_posted = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True)

    #This holds the the 'rating' of this post (importance), as upvoted by users
    score = models.IntegerField(default=0)

    def getDetail(self):
        """Returns dictionary object containing info about this post"""
        return { 'author' : self.author.getInfo(), 'text' : self.text, 'score' : self.score,
                'timestamp' : my_strftime(self.time_posted) }

    def upvote(self):
        """Increments the score attribute of this model"""
        self.score = self.score + 1
        self.score.save()

class BlockEvent(models.Model):
    """
    Holds data for a same-day event in this user's block
    All events are totally open - no one is invited, but anyone can come
    """

    block_page = models.ForeignKey(BlockPage)
    
    author = models.ForeignKey('userInfo.UserProfile')
    time_created = models.DateTimeField(auto_now_add=True)

    duration = models.TextField()   #This is just a string such as '5 pm to 7pm' that the user enters
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    event_title = models.TextField()
    description = models.TextField(null=True)
    location = models.TextField()
    score = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    image = models.ForeignKey('userInfo.ImageHolder', null=True)

    def getDetail(self, user=None):
        """
        Returns dictionary object containing info about this event
        Optionally, relative to a logged-in user
        """
        if user is not None:
            user_attending = 1 if user in self.userprofile_set.all() else 0
        else:
            user_attending = 0

        #Get event picture
        if self.image is not None:
            event_image = self.image.handle
        else:
            event_image = 'default_event.jpg'

        #Build attending list
        attending_list = [ u.getInfo() for u in self.userprofile_set.all() ]

        return { 'author' : self.author.getInfo(), 'title' : self.event_title, 'description' : self.description, 
                'num_attending' : len(self.userprofile_set.all()), 'attending' : attending_list, 'timestamp' : my_strftime(self.time_created),
                'type' : 'event', 'score' : self.getScore(), 'duration' : self.duration, 
                'user_attending' : user_attending, 'relative_timestamp' :  relative_timestamp(self.time_created), 'id' : self.id,
                'location' : self.location, 'picture' : event_image, 'thumbnail' : 'Thumbnails/' + event_image }
    
    def getScore(self):
        """
        Calculates the 'score' of this event
        score = (.1*views + num_comments + 2*num_attending) / log(time_elapsed+1)
        """
        elapsed = datetime.now() - self.time_created
        return (.1*self.views + len(self.eventcomment_set.all()) + 2*len(self.userprofile_set.all())) + (10**3)*pow(.001 + elapsed.seconds, -.5)

    def getComments(self, offset=0, user=None):
        """
        Returns list of comments plus the details for this event
        """
        try:
            offset = int(offset)
        except ValueError:
            offset = 0

        #Increment number of views for this event
        self.views = self.views + 1
        self.save()

        info = self.getDetail(user)

        a = [ comment.getDetail() for comment in self.eventcomment_set.order_by("-time_created")[offset:offset+10] ]
        a.reverse()
        info['comments'] = a
        return info

class EventComment(models.Model):
    """
    Represents a comment on a particular BlockEvent
    """
    event = models.ForeignKey(BlockEvent)

    author = models.ForeignKey('userInfo.UserProfile')
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def getDetail(self):
        return { 'author' : self.author.getInfo(), 'text' : self.text,
                'timestamp' : my_strftime(self.time_created), 'type' : 'comment',
                'relative_timestamp' : relative_timestamp(self.time_created) }
