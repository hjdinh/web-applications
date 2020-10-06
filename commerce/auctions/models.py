from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    CATEGORIES = [
        ('CLOTHING', 'Clothing'),
        ('ELECTRONICS', 'Electronics'),
        ('HOME', 'Home'),
        ('KITCHEN', 'Kitchen'),
        ('OTHER', 'Other')
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_listings")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_bid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    photo = models.URLField(blank=True)
    category = models.CharField(blank=True, choices=CATEGORIES, max_length=64)
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="favorited")
    winner = models.ForeignKey(User, blank=True, default=None, on_delete=models.PROTECT, related_name="winner_listings")

    def __str__(self):
        return f"{self.title} - ${self.starting_bid}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    bid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bid_time = models.DateTimeField(auto_now_add=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bid")

    def __str__(self):
        return f"Bid on {self.listing.title} by {self.bidder} for {self.bid}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    comment = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} comment on {self.listing.title}"