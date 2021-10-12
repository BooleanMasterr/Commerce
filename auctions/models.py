from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image

# Create your models here.

CHOICES = (
    ('electronics', 'ELECTRONICS'),
    ('toys', 'TOYS'),
    ('fashion', 'FASHION'),
    ('home', 'HOME'),
)


class Listing(models.Model):

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=20)
    date = models.DateTimeField(default=timezone.now, unique=True)
    title = models.CharField(max_length=300)
    description = models.TextField(max_length=400, blank=True)
    is_closed = models.BooleanField(default=False)
    category = models.CharField(choices=CHOICES, max_length=255, blank=True)
    image_url = models.URLField(max_length=600, blank=True, null=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    listing_key = models.ForeignKey(Listing, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)


class Bid(models.Model):
    listing_key = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='l_key')
    bid = models.DecimalField(decimal_places=2, max_digits=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    @staticmethod
    def arg_max(key=None, queryset=None):
        if queryset:

            bids = []

            for obj in queryset:
                try:
                    bid = Bid.objects.filter(listing_key=obj, is_closed=False).order_by('-bid')[0]
                except IndexError:
                    bids.append(None)
                else:
                    bids.append(bid)

            return bids
        try:
            obj = Bid.objects.filter(listing_key=key, is_closed=False).order_by('-bid')[0]
        except IndexError:
            return None
        else:
            return obj



class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_watched = models.BooleanField(default=False)
    listing_key = models.ManyToManyField(Listing)

    def __unicode__(self):
        return self.listing_key.title
