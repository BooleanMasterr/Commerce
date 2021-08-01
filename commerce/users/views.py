from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.contrib import messages


# Create your views here.


def register(request):

    form = UserRegistrationForm()

    if request.method == "POST":

        form = UserRegistrationForm(request.POST or None)

        if form.is_valid():

            form.save()

            messages.success(request, "You are now able to login")
            return HttpResponseRedirect(reverse("login"))

    context = {"form": form}

    return render(request, "users/register.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("listings"))
        else:
            messages.error(request, "Invalid username and/or password")
            return HttpResponseRedirect(reverse("login"))

    return render(request, "users/login.html")
