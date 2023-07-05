from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, DealerReview
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        st = request.GET.get("st")
        dealer_id = request.GET.get("id")
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/adf616e2-c029-4e08-bc72-d66c42006080/dealership-package/get-dealership"
        # Get dealers from the URL
        if st:
            dealerships = get_dealers_from_cf(url, st=st)
        elif dealer_id:
            dealerships = get_dealers_from_cf(url, dealer_id=dealer_id)
        else:
            dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        context = dict()
        context["dealerships"] = dealerships        
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/adf616e2-c029-4e08-bc72-d66c42006080/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/adf616e2-c029-4e08-bc72-d66c42006080/dealership-package/get-dealership"
        dealer = get_dealers_from_cf(url2, dealer_id=dealer_id)
        context = dict()
        context["reviews"] = reviews
        context["dealer"] = dealer
        context["dealer_id"] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def add_review(request, dealer_id):
    if request.user.is_authenticated:
        url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/adf616e2-c029-4e08-bc72-d66c42006080/dealership-package/get-dealership"
        dealer = get_dealers_from_cf(url2, dealer_id=dealer_id)
        context = dict()
        context["dealer_id"] = dealer_id
        context["dealer"] = dealer
        
        if request.method == "GET":
            cars = CarModel.objects.all()
            context["cars"] = cars
            return render(request, 'djangoapp/add_review.html', context)
        if request.method == "POST":
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/adf616e2-c029-4e08-bc72-d66c42006080/dealership-package/post-review"
            
            json_payload = dict()

            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)

            json_payload["name"] = username
            json_payload["dealership"] = dealer_id
            json_payload["review"] = request.POST["content"]
            if request.POST["purchased"] == 'on':
                json_payload["purchase"] = True
                json_payload["purchase_date"]
                json_payload["car_make"]
                json_payload["car_model"]
                json_payload["car_year"]
            else
                json_payload["purchase"] = False


            response = post_request(url, json_payload, id=dealer_id)
            return HttpResponse(response)
        