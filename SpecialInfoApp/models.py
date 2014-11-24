from django.db import models
from helper_functions import my_strftime

# Create your models here.

#Abstract base class to hold base of the extra info (i.e. the specific interest or specific school)
class ExtraInfoTypes(models.Model):
    #Holds the title of the extra info
    title = models.TextField()
    
    class Meta:
        abstract = True

#Abstract base class used in a m2m relationship between UserProfile and ExtraInfoTypes
class ExtraInfo(models.Model):
    user = models.ForeignKey('userInfo.UserProfile')
    date_started = models.DateTimeField(null=True)
    date_ended = models.DateField(null=True)
    time_added = models.DateField(auto_now_add=True)
 
    def getDetail(self):
        """Returns base info"""
        return { 'date_started' : my_strftime(self.date_started),
                'date_ended' : my_strftime(self.date_ended),
                'timestamp' : my_strftime(self.time_added), 'user' : self.user.getInfo() }
    class Meta:
        abstract = True

class Interest(ExtraInfoTypes):
    #Holds data for particular interest. Nothing to extend for now
    pass

class HasInterest(ExtraInfo):
    interest = models.ForeignKey(Interest)

    def getDetail(self):
        """Returns dictionary object with basic info about the interest"""
        detail = super(HasInterest, self).getDetail()
        detail.update({ 'interest' : self.interest.title, 'type' : 'interest'})
        return detail

class School(ExtraInfoTypes):
    #Holds data for specific school.
    pass

class HasSchool(ExtraInfo):
    #Holds membership data for particular school
    school = models.ForeignKey(School)
    studied = models.TextField(null=True)

    def getDetail(self):
        """Returns dict with info"""
        detail = super(HasSchool, self).getDetail()
        detail.update({ 'school' : self.school.title, 'studied' : self.studied, 'type' : 'school' }) 
        return detail

class LivingLoc(ExtraInfoTypes):
    #Holds data for specific Living location.
    pass

class HasLivingLoc(ExtraInfo):
    #Holds membership data for particular living location
    living_loc = models.ForeignKey(LivingLoc)

    def getDetail(self):
        """Returns dict with info"""
        detail = super(HasLivingLoc, self).getDetail()
        detail.update({ 'living_loc' : self.living_loc.title, 'type' : 'living_loc' })
        return detail

class Workplace(ExtraInfoTypes):
    #Holds data for specific workplace.
    pass

class HasWorkplace(ExtraInfo):
    #Holds membership data for particular workplace
    workplace = models.ForeignKey(Workplace)
    job = models.TextField(null=True)

    def getDetail(self):
        """Returns dict with info"""
        detail = super(HasWorkplace, self).getDetail()
        detail.update({ 'workplace' : self.workplace.title, 'job' : self.job, 'type' : 'workplace' }) 
        return detail
