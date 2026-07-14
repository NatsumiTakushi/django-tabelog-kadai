from django.shortcuts import render
from django.views.generic import ListView, DetailView
from base.models import User
from django.db.models import Q

class loginView(ListView):
    model = User
    template_name = 'pages/login.html'
