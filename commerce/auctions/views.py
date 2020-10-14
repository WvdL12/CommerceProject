from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template.defaulttags import register
from datetime import datetime

from .models import User, Category, Listing, Bid, Comment

@register.filter
def get_price(dict, key):
    return dict.get(key)

def index(request):
    listings = Listing.objects.all()
    prices = {}
    for listing in listings:
        price = listing.start_bid
        if listing.bids.all():
            price = listing.bids.order_by('-price').first()
        prices[listing.id] = price
    return render(request, "auctions/index.html", {
        "listings": listings, "prices": prices
        })

def listings(request, list_id):
    listing = Listing.objects.get(pk = list_id)
    price = listing.start_bid
    num_bids = listing.bids.count()
    if listing.bids.all():
        price = listing.bids.order_by('-price').first()
        
    if request.method == "POST":
        name = request.POST["name"]
        user = request.user
        
        if name == "comment-form":
            body = request.POST["comment"]
            now = datetime.now()
            posted_datetime = now.strftime("%d/%m/%Y, %H:%M")
            comment = Comment(body = body, datetime = posted_datetime, listing = listing, user = user)
            comment.save()
            
        elif name == "bid-form":
            bid = request.POST["bid"]
            bid_value = float(bid)
            invalid_bid = False
            if num_bids > 0:
                price_value = float(price.price)
                invalid_bid = bid_value == price_value
            else:
                invalid_bid = bid_value < price
        
            if invalid_bid:
                return render(request, "auctions/listing.html", {
                    "listing": listing, "price": price, "num_bids": num_bids, "message": "Bid must be equal or higher than starting bid, and higher than highest current bid."
                    })
            else:
                new_bid = Bid(price = bid, listing = listing, user = user)
                new_bid.save()
                
        elif name == "remove-form":
            listing.watchlisted.remove(user)
            
        elif name == "add-form":
            listing.watchlisted.add(user)
        
        elif name == "close-listing":
            listing.active=False
            listing.save()
        
        return HttpResponseRedirect(reverse('listing', kwargs={
            'list_id': listing.id
            })) 
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing, "price": price, "num_bids": num_bids
            })
        
@login_required
def watchlist(request):
    user = request.user
    listings = user.watchlist.all()
    prices = {}
    for listing in listings:
        price = listing.start_bid
        if listing.bids.all():
            price = listing.bids.order_by('-price').first()
        prices[listing.id] = price
        
    return render(request, "auctions/watchlist.html", {
        "listings": listings, "prices": prices
        })

@login_required
def new_listing(request):
    if request.method == "POST":
        listing = Listing(
            user = request.user,
            title = request.POST["title"],
            description = request.POST["description"],
            start_bid = request.POST["start_bid"],
            img = request.POST["img"],
            category = Category.objects.get(name = request.POST["category"]))
        listing.save()

        return HttpResponseRedirect(reverse('listing', kwargs={
                'list_id': listing.id
            }))
    else:
        return render(request, "auctions/newlisting.html", {
            "categories": Category.objects.all()
            })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
        })

def category(request, ctg_name):
    category = Category.objects.get(name=ctg_name)
    listings = category.listings.all()
    prices = {}
    for listing in listings:
        price = listing.start_bid
        if listing.bids.all():
            price = listing.bids.order_by('-price').first()
        prices[listing.id] = price
    
    return render(request, "auctions/category.html", {
        "category": category, "listings": listings, "prices": prices
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        valuenext = request.POST.get('next')
        
        # Check if authentication successful
        if user is not None and valuenext=="":
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        elif user is not None and valuenext!="":
            login(request, user)
            return redirect(valuenext)
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
