from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from djangoapp.models import CarModel, CarMake

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def static_template(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/static_template.html', context)

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)



# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact_us.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')

# ...

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')
# ...

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)
# ...

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://a263f979.eu-de.apigw.appdomain.cloud/api/dealership"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    context["dealer_id"] = dealer_id
    if request.method == "GET":
        url = "https://a263f979.eu-de.apigw.appdomain.cloud/api/review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        #reviews_names = ' '.join([review.name+": "+review.review+"("+review.sentiment+")" for review in reviews])
        context["reviews"] = reviews
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    context["dealer_id"]=dealer_id
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        if request.method == "POST":
            url = "https://a263f979.eu-de.apigw.appdomain.cloud/api/review"
            car_model_obj =CarModel.objects.get(id=request.POST['car'])
            review = dict()
            review["name"] = request.user.username
            review["purchase_date"] = request.POST['purchasedate']
            review["purchase"] = request.POST['purchasecheck']
            review["dealership"] = dealer_id
            review["car_model"] = car_model_obj.name
            review["car_make"] = car_model_obj.car_make.name
            review["car_year"] = car_model_obj.year.strftime("%Y")
            review["review"]=request.POST['content']
            json_payload=dict()
            json_payload["review"] = review
            post_response=post_request(url, json_payload=json_payload, dealer_id=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        elif request.method == 'GET':
            context["cars"]= CarModel.objects.filter(dealer_id=dealer_id)
            return render(request, 'djangoapp/add_review.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

