from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import Form, ModelForm
from django.contrib.auth.decorators import login_required

import datetime

from .models import User, Listing, Bid, Comment

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'starting_bid',
            'photo',
            'category',
        ]

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            'comment',
        ]

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = [
            'bid',
        ]

def index(request):
    listings = Listing.objects.filter(active=True)
    for listing in listings:
        bids = Bid.objects.filter(listing=listing)
        bidcount = len(bids)
        if listing.max_bid == 0 or bidcount == 0:
            listing.max_bid = listing.starting_bid
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def login_view(request):
    if request.method == "POST":

            # Attempt to sign user in
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "auctions/login.html", {
                    "message": "Invalid username and/or password."
                })
    else:
        return render(request, "auctions/login.html")
            
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required()
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = Listing()
            listing.owner = request.user
            listing.title = form.cleaned_data["title"]
            listing.description = form.cleaned_data["description"]
            listing.starting_bid = form.cleaned_data["starting_bid"]
            listing.photo = form.cleaned_data["photo"]
            listing.category = form.cleaned_data["category"]
            listing.active = True
            listing.date_created = datetime.datetime.now()
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            form = ListingForm()
            return render(request, "auctions.create.html", {
                'form': form,
                'message': "Invalid input. Please try again."
            })
    else:
        watchlist = request.user.favorited.all()
        watchlistcount = len(watchlist)
        return render(request, "auctions/create.html", {
            'form': ListingForm(),
            'watchlistcount': watchlistcount
        })

def listing(request, listing_id):
    listing = Listing.objects.get(active=True, pk=listing_id)
    owner = listing.owner.username
    comments = Comment.objects.filter(listing=listing).order_by("-date")

    bids = Bid.objects.filter(listing=listing)
    bidcount = len(bids)

    if listing.max_bid == 0 or bidcount == 0:
        listing.max_bid = listing.starting_bid

    if request.user.is_authenticated:

        commentform = CommentForm()
        bidform = BidForm()

        favorites = request.user.favorited.all()
        favorite = listing in favorites

        check = request.user == listing.owner

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "owner": owner,
            "bids": bids,
            "bidcount": bidcount,
            "comments": comments,
            "commentform": commentform,
            "bidform": bidform,
            "favorite": favorite,
            "check": check
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "owner": owner,
            "bids": bids,
            "bidcount": bidcount,
            "comments": comments,
        })

def categories(request):
    categories = [cap for cap, category in Listing.CATEGORIES]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, category):
    listings = Listing.objects.filter(category=category, active=True)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category
    })

@login_required()
def watchlist(request):
    listings = Listing.objects.filter(watchlist=request.user)
    return render(request, "auctions/watchlist.html", {
        "listings": listings
        })

@login_required()
def add(request):
    if request.method == "POST":
        listingid = request.POST["listingid"]
        listing = Listing.objects.get(pk=listingid)
        user = request.user.id
        listing.watchlist.add(user)
    return HttpResponseRedirect("/listing/" + str(listingid))

@login_required()
def remove(request):
    if request.method == "POST":
        listingid = request.POST["listingid"]
        listing = Listing.objects.get(pk=listingid)
        user = request.user.id
        listing.watchlist.remove(user)
    return HttpResponseRedirect("/listing/" + str(listingid))

@login_required
def comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        listingid = request.POST["listingid"]
        if form.is_valid():
            comment = Comment()
            comment.comment = form.cleaned_data["comment"]
            comment.listing = Listing.objects.get(pk=listingid)
            comment.user = request.user
            comment.date = datetime.datetime.now()
            comment.save()
            return HttpResponseRedirect("/listing/" + str(listingid))
        return render(request, "auctions/listing.html", {
            "message": "Unable to save comment"
        })
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required
def bid(request):
    listingid = request.POST["listingid"]
    listing = Listing.objects.get(pk=listingid)
    bids = Bid.objects.filter(listing=listing)
    bidcount = len(bids)
    comments = Comment.objects.filter(listing=listing).order_by("-date")
    favorites = request.user.favorited.all()
    favorite = listing in favorites
    commentform = CommentForm()
    bidform = BidForm()
    if request.method == "POST":
        form = BidForm(request.POST)
        if listing.max_bid == 0 or bidcount == 0:
            listing.max_bid = listing.starting_bid
        if form.is_valid():
            bidamount = form.cleaned_data["bid"]
            if bidamount > listing.max_bid:
                bid = Bid()
                bid.listing = listing
                bid.bidder = request.user
                bid.bid_time = datetime.datetime.now()
                bid.bid = bidamount
                bid.save()
                listing.max_bid = bidamount
                listing.save()
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bids": bids,
                    "bidcount": bidcount,
                    "comments": comments,
                    "commentform": commentform,
                    "bidform": bidform,
                    "favorite": favorite,
                    "message": "Bid placed."
                })
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bids": bids,
                    "bidcount": bidcount,
                    "comments": comments,
                    "commentform": commentform,
                    "bidform": bidform,
                    "favorite": favorite,
                    "error": "Invalid bid."
                })
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required()
def close(request):
    if request.method == "POST":
        listingid = request.POST["listingid"]
        listing = Listing.objects.get(pk=listingid)
        bids = Bid.objects.filter(listing=listing)
        winner = bids.order_by('-bid').first().bidder
        favorites = request.user.favorited.all()
        favorite = listing in favorites
        comments = Comment.objects.filter(listing=listing).order_by("-date")
        if request.user == listing.owner:
            listing.active = False
            listing.winner = winner
            listing.save()
            return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "favorite": favorite,
                    "bids": bids,
                    "winner": winner,
                    "comments": comments,
                })