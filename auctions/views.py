from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import User, category, listing, bid, watchlist, comment


def index(request):
    listings = listing.objects.filter(active = "yes")
    current_price = []
    for i in listings:
        highest_bid = bid.objects.filter(item=i).order_by('-price').first()
        try:
            current_price.append(highest_bid.price)
        except:
            current_price.append(i.start_bid)

    # using 2 variables in for loop in django: https://stackoverflow.com/questions/14079815/using-for-in-template-with-two-variables-django
    zip_data = zip(listings, current_price)
    return render (request,"auctions/index.html",{
    "zip_data":zip_data
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
    
@login_required(login_url="login")
def new_listing(request):
    if request.method == "POST":
        #required + image optional. 
        title = request.POST["title"]
        description = request.POST["description"]
        start_bid = int(request.POST["start_bid"])
        image = request.POST["image"]
        categ_post = request.POST["categ"]

        user = request.user

        if title == "" or description == "" or start_bid =="":
            return HttpResponse("Enter required fields.")
        
        if categ_post == "":
            #https://docs.djangoproject.com/en/5.0/topics/db/queries/
            l = listing.objects.create(title=title, description=description, start_bid=start_bid,image=image,usr=user)
            l.save()
            return HttpResponseRedirect(reverse("index"))
        #optional category
        else:
            try:
                categ = category.objects.get(category=categ_post)
                l = listing.objects.create(title=title, description=description, start_bid=start_bid,image=image,category=categ,usr=user)
                l.save()
            except category.DoesNotExist:
                return HttpResponse("Category not found.")
        return HttpResponseRedirect(reverse("index"))
    else:
        categories = category.objects.all()
        return render(request,"auctions/new_listing.html",{
            "categories":categories 
        })



def listing_page_views(request,listing_id):
    if request.method == "POST":
        watchlist_value = request.POST.get("watchlist_action")
        # Handling multiple forms: https://www.youtube.com/watch?v=j77urTdU26M
        form_type = request.POST.get("form_type")
        item = listing.objects.get(id=listing_id)
        user = request.user
        #watchlist:
        if form_type == "watchlist":
            if watchlist_value == "Add to watchlist":
                try:
                    w = watchlist.objects.get(usr=user)
                except watchlist.DoesNotExist:
                    w = watchlist.objects.create(usr=user)
                    
                w.items.add(item)
                w.save()
            elif watchlist_value == "Remove from watchlist":
                w = watchlist.objects.get(usr=user)
                w.items.remove(item)
                w.save()
        
        #make bid:
        if form_type =="bid":
            bid_price =request.POST.get("bid")
            highest_bid = bid.objects.filter(item=item).order_by('-price').first()
            try:
                exist_bid = highest_bid.price
            except:
                exist_bid =None
            start_bid = item.start_bid
            try: 
                bid_price = int(bid_price)
            except:
                return HttpResponse("Provide a number.")
            
            if exist_bid is not None:
                if bid_price > exist_bid:
                    bid.objects.create(price=bid_price, item=item, usr=user)
                else:
                    return HttpResponse("Provide a bigger number.")
            else:
                if bid_price >= start_bid:
                    bid.objects.create(price=bid_price, item=item, usr=user)
                else:
                    return HttpResponse("Provide a bigger number.")
        #Close Auction:
        if form_type =="close":
            highest_bid = bid.objects.filter(item=item).order_by('-price').first()
            if user == item.usr:
                try: 
                    highest_bid_user = highest_bid.usr
                    print("try route")
                    print(highest_bid_user)
                    item.winner = highest_bid_user
                    item.active = "no"
                    item.save()
                except:
                    print("except route")
                    item.active = "no"
                    item.save()
        #Comment:
        if form_type =="comment":
            comment_text = request.POST.get("comment_text")
            comment.objects.create(comment=comment_text, item=item, usr=user)
            
        return redirect('listing_page', listing_id=listing_id)
    
    else:
        #get or 404: https://www.geeksforgeeks.org/get_object_or_404-method-in-django-models/
        listing_item = get_object_or_404(listing, id=listing_id)
        b_object = bid.objects.filter(item=listing_item).order_by('-price').first()
        u = request.user
        #bid price:
        if b_object is not None and b_object.price > listing_item.start_bid:
            price = b_object.price
        else:
            price = listing_item.start_bid
        #watchlist:
        watchlist_text = ""
            #for checking if user is logged in: https://stackoverflow.com/questions/3644902/how-to-check-if-a-user-is-logged-in-how-to-properly-use-user-is-authenticated
        if request.user.is_authenticated:
            try:
                watchlist_object = watchlist.objects.get(usr=u)
                watchlist_items = watchlist_object.items.all()
            except watchlist.DoesNotExist:
                watchlist_items = []
            
            if listing_item in watchlist_items:
                watchlist_text = "Remove from watchlist"
            else:
                watchlist_text = "Add to watchlist"

        # closing auction 
        if u == listing_item.usr and listing_item.active=="yes":
            close = "yes"
        else:
            close = None

        #Variable wheter to display bid form.
        if listing_item.active=="yes":
            active = "yes"
        else:
            active = None

        #if the user won the auction:
        if u == listing_item.winner:
            winner = "You Won!"
        else:
            winner = None

        #comments render:
        comments = listing_item.comment.all()

        return render(request,"auctions/listing_page.html",{
            'listing_id':listing_id,
            "list":listing_item,
            'price':price,
            'watchlist_text':watchlist_text,
            "close":close,
            "active":active,
            "winner":winner,
            "comments":comments
    })


def watchlist_views (request):
    user =request.user
    user_watchlist = watchlist.objects.filter(usr=user)
    
    return render(request,"auctions/watchlist.html",{
        "user_watchlist":user_watchlist
    })

def categories(request):
    categories_items = category.objects.all()
    return render(request,"auctions/categories.html",{
        "categories_items":categories_items
    })

def category_page_views(request,category_id):
    specific_category = get_object_or_404(category, id=category_id)

    listings_in_category = specific_category.listing.filter(active="yes")

    return render(request, "auctions/category_page.html",{
        "category_id":category_id,
        "listings_in_category":listings_in_category
    })
