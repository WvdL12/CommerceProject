from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=32, default="Other")
    
    def __str__(self):
        return f"{self.name}"
        
class Listing(models.Model):
    #Fields user (foreignkey), title, description, starting bid, image url (opt), category (opt, foreignkey)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.DecimalField(decimal_places=2, max_digits=6)
    img = models.URLField(max_length=200, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET("None"), related_name="listings")
    watchlisted = models.ManyToManyField(User, blank=True, related_name="watchlist")
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.id}: {self.title}"
    
class Bid(models.Model):
    #foreignkey connection to Listings
    #foreignkey connection to user
    price = models.DecimalField(decimal_places=2, max_digits=6)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    
    def __str__(self):
        return f"{self.price}"

class Comment(models.Model):
    #foreignkey Listings
    #foreignkey User
    #field title, body, datetime
    body = models.TextField()
    datetime = models.CharField(max_length=17)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET("Anonymous"), related_name="comments")
    
    def __str__(self):
        return f"{self.user} on {self.listing} at {self.datetime}"
        