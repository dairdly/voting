from django.db import models 

class Candidate(models.Model):

    class Meta:
        get_latest_by = "votes"
        ordering = ["votes", "level"]
        default_related_name = "aspirant"

    class Candidate_positions(models.TextChoices):
        sug_president = "SUG PRESIDENT"
        vice_president = "VICE PRESIDENT"
        director_of_transport = "DIRECTOR OF TRANSPORT" 

    class Levels(models.IntegerChoices):
        one = 100
        two = 200 
        three = 300 
        four = 400 
        five = 500

    name = models.CharField(max_length=20, unique=True)
    level = models.IntegerField(choices=Levels.choices)
    votes = models.IntegerField(default=0)
    post = models.ForeignKey('main.Position', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Position(models.Model):

    name = models.CharField(max_length=30, unique=True)
    candidates = models.ManyToManyField(Candidate)

    def __str__(self):
        return self.name 
