from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=32)
    
    def __str__(self):
        return f"{self.category_name}"
        
class Listings(models.Model):
    #Fields user (foreignkey), title, description, starting bid, image url (opt), category (opt, foreignkey)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.DecimalField(decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.SET("None"), related_name="listings")
    
    def __str__(self):
        return f"{self.id}: {self.title}"
    
class Bids(models.Model):
    #foreignkey connection to Listings
    #foreignkey connection to user
    price = models.DecimalField(decimal_places=2, max_digits=6)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    
    def __str__(self):
        return f"${self.price}"

class Comments(models.Model):
    #foreignkey Listings
    #foreignkey User
    #field title, body, datetime
    title = models.CharField(max_length=32)
    body = models.TextField()
    datetime = models.DateTimeField()
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET("Anonymous"), related_name="comments")
    
    def __str__(self):
        return f"{self.title} by {self.user}"
    
