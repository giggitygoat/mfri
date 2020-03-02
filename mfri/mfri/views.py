from django.shortcuts import render
import os
from django.http import HttpResponse
import webbrowser, bs4, sys, requests, time
import numpy as np

def home(request):
    text = """<h1>Velkommen til Djanpy !</h1> Hvem sagde Front-end?"""
    return render(request, "index.html", {})


def associates(request):
    text="xx"
    return render(request, "associates.html",{})

def portfolio(request):
    text="xx"
    return render(request, "portfolio.html",{})

def about(request):
    text="xx"
    return render(request, "about.html",{})

def scrapeSite():
    url = 'https://re.reddit.com/r/VegRecipes/top/?sort=top&t=all'
    header = {'Accept-Encoding': 'gzip, deflate, sdch',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
    res = requests.get(url, headers = header)
    if res.status_code == 200:
        print("status code 200!!!")
        return res
    else:
        return


