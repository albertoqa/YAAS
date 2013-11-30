from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class auction(models.Model):
    LIFECYCLES_ = (
        ('A', 'Active'),
        ('B', 'Banned'),
        ('D', 'Due'),
        ('X', 'Adjudicated'),
    )

    title = models.CharField(max_length=150)
    description = models.TextField()
    min_price = models.FloatField()
    deadline = models.DateTimeField()
    lifecycle = models.CharField(max_length=1, choices=LIFECYCLES_)
    seller = models.ForeignKey(User)
    lock = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['deadline']

class bid(models.Model):
    STATUS_ = (
        ('W', 'Wining'),
        ('L', 'Losing'),
    )

    auct = models.ForeignKey(auction)
    user = models.ForeignKey(User)
    amount = models.FloatField()
    status = models.CharField(max_length=1, choices=STATUS_)
