from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class category(models.Model):
    category = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.category}"

class listing(models.Model):
    yes="yes"
    no="no"
    active_choices = (
        (yes,"yes"),
        (no,"no")
    )

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=255)
    start_bid = models.IntegerField()
    image = models.URLField()
    category = models.ForeignKey(category, on_delete=models.CASCADE, related_name="listing",null=True)
    usr = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing_user",default=None)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing_winner", null=True, default=None, blank=True)
    active= models.CharField(max_length=3,choices= active_choices, default=yes)
    def __str__(self):
        return f"{self.title}"

class bid(models.Model):
    price = models.IntegerField()
    item = models.ForeignKey(listing, on_delete=models.CASCADE, related_name="bid")
    usr = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_user", null=True, default=None)

    def __str__(self):
        return f"{self.usr} | {self.item} | {self.price}"
    
class comment(models.Model):
    comment = models.CharField(max_length=255)
    item = models.ForeignKey(listing, on_delete=models.CASCADE, related_name="comment")
    usr = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_usr", null=True, default=None)
    
    def __str__(self):
        return f"{self.usr} | {self.item}"
    
class watchlist(models.Model):
    items = models.ManyToManyField(listing, related_name="watchlists")
    usr = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")

    def __str__(self):
        return f"{self.usr}'s Watchlist"

