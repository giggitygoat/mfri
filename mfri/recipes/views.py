
from __future__ import print_function
from django.shortcuts import render, redirect
from django.db.models import Q
from recipes import models as recMod
import webbrowser, bs4, sys, requests, time
import numpy as np
import operator
import time
from functools import reduce
from django.db.models import Prefetch
from django.contrib import messages
from django import template
import firebase_admin
from firebase_admin import messaging, credentials

import datetime
register = template.Library()

@register.filter
def in_list(value, the_list):
    value = str(value)
    return value in the_list.split(',')

cred = credentials.Certificate("/home/www/mfri/recipes/p4alarm-firebase-adminsdk-g8il1-a3e2d3020a.json")
firebase_admin.initialize_app(cred)
def scrapeSite(url):
    
    header = {'Accept-Encoding': 'gzip, deflate, sdch',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
    res = requests.get(url, headers = header)
    if res.status_code == 200:
        print("status code 200!!!")
        return res.content
    else:
        return

def send_to_token(msg):
    # [START send_to_token]
    # This registration token comes from the client FCM SDKs.
    registration_token = 'et1Gy1YilHQ:APA91bGqIAj2gb2sdZlCEcJH5mDE7bxMmNnLW3oY2iJEExM7uYHzRHE_T0_Mbr1qhWeIlEGq7fM4V95cR4WCSW51OXnpE1q5sggsrTrYLxVNx3KiDTxsBecbohm3YeaPZ7kzBoR18tt2'

    # See documentation on defining a message payload.
    noti = messaging.AndroidNotification(
        sound='R.raw.fire_pager',
        body=msg,
        title='titel',


    )

    andro=messaging.AndroidConfig(
        notification=noti
    )

    message = messaging.Message(
        data={
            'score': 'alarm',
            'time': '2:45',
        },
        android=andro,
        token=registration_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_token]

def scraperMain(url):
    requestx = scrapeSite(url)

    vegSoup = bs4.BeautifulSoup(requestx.decode('utf-8'))
#SCRAPING TOOL
    linkFinder = vegSoup.select('.lazyload')
    link = []
    for href in linkFinder:
        req = scrapeSite(href['href'])
        beautify = bs4.BeautifulSoup(req.decode('utf-8', 'ignore')) 
        title = beautify.find('h1').get_text()
        print('title: ',title)
        #reci = recMod.Recipe(name=title,link=href['href'])
        #reci.save()
        try:
            scraper= beautify.find("ul",{"class":"ingredientlist content"}).find_all("li")
        except:
            pass
        for each in scraper:
            #ingredient = each.get_text()
            #ingr = recMod.Ingredient(name=ingredient, recipe=reci)
            #ingr.save()
            print('ingre:')
        
        link.append(href['href'])

def tester(request, ingreList, ok):
    multipleFilterList =[]
    name = ''

    if ok==True:
        name = request.POST['searchField']
        
        isInTheList = False
        for each in ingreList:
            if name.lower() == each.lower():
                isInTheList=True
                break
        if isInTheList==False:
            if len(name)>1:
                ingreList.append(name)
            else:
                messages.warning(request, 'Indtast minimum 2 karaktere')
                
        else:
            messages.warning(request, 'Du har allerede søgt på '+name)
    

    if len(ingreList)<1:
        print('ingreList er 0')
        return render(request, "recipes.html", {}) 

    else:
        firstIngredient = ingreList[0].lower()
        
        filterList = recMod.Recipe.objects.filter(ingredient__name__icontains=firstIngredient).order_by('name').prefetch_related('ingredient_set').distinct('name')
        """
        if len(ingreList)==1:
            print("her")
            
            return render(request, "recipes.html", {'dict':filterList,'results':len(filterList),'ingreList':ingreList}) 
        """ 

        print("HVORDAN")
        startTime = time.time()
        
        #print(len(filterList))
        request.session['ingre'] = ingreList
        if not len(ingreList)==1:
            for every in filterList:
                ingreds = every.ingredient_set.all().values_list('name', flat=True)
            
                counter=0

                for ingreObj in ingreList:
                    
                    if any(ingreObj.lower() in s for s in ingreds):
                        counter+=1
                    
                if counter>=len(ingreList):
                    multipleFilterList.append(every)
                
            if len(multipleFilterList)<=1:
                print('jeg returnede her')
                return render(request, "recipes.html", {'dict':'', 'ingreList':ingreList}) 
    
        else:
            return render(request, "recipes.html", {'dict':filterList,'results':len(filterList),'ingreList':ingreList}) 
    #print("HEEER",multipleFilterList)  
    #print(multipleFilterList)  
    if len(multipleFilterList)>=1:
        filterList = multipleFilterList
    endTime = time.time()
    print(endTime-startTime)  
    """
    for each in filterList:
        #print(each.name)
        try:
            tempDict[each.name] = each.link
        except:
            pass
    """
    
    return render(request, "recipes.html", {'dict':filterList,'results':len(filterList),'ingreList':ingreList}) 

def recipes(request):
    ingreList = []
    try:
        ingreList = request.session['ingre']
    except:
        pass
    if request.method=="POST":
        if 'searchField' in request.POST:
            if request.POST['searchField'] == 'salt':
                return redirect('https://youtu.be/ooOELrGMn14?t=10')

            return tester(request, ingreList, True)
        if 'ingre' in request.POST:
            try:
                ingreList.remove(request.POST.get('ingre', ""))
            except:
                pass
            request.session['ingre'] = ingreList
            if len(ingreList)>0:
                print(ingreList)
                return tester(request, ingreList, False)
            else:
                print("ingreList er tom")
                return render(request, "recipes.html", {})
        


        if 'recField' in request.POST:
            getRecipes = list(recMod.Recipe.objects.distinct('link').filter(name__icontains=request.POST['recField']).values())
            print(getRecipes)
            return render(request, "recipes.html", {'recipeList':getRecipes})
       

    if len(ingreList)>0:
        print('hej')
        return tester(request, ingreList, False)

        #print(temp)

    #url = 'https://www.valdemarsro.dk/opskrifter/'
    #scraperMain(url)

   # for i in range(9, 13):
    #    scraperMain(url+'page/'+str(i)+'/')

    return render(request, "recipes.html", {'dict':'', 'ingreList':ingreList})

def heleMummum(url):
    requestx = scrapeSite(url)

    vegSoup = bs4.BeautifulSoup(requestx.decode('utf-8'))
    #linkFinder = vegSoup.find("div",{"class":"section mute-heading section--expanded teaser-deck-d"})
    #section mute-heading section--expanded teaser-deck-d section--expanded
    linkFinder = vegSoup.find("div",{"class":"section mute-heading section--expanded teaser-deck-d section--expanded"})

    print(linkFinder)
    scraper = []
    try:
        scraper= linkFinder.find_all("div",{"class":"col-xs-6 col-sm-4 col-md-3"})
    except Exception as e:
        print(str(e))
    #print(scraper)
    for each in scraper:
        try:
            newLink = each.find_all("a")[0]['href']
        except:
            pass
        #print(newLink)
        if not '#' in newLink:
            newLinkPlus = "https://dr.dk"+newLink
            print(newLinkPlus)
            ingScrape = scrapeSite(newLinkPlus)
            beautify = bs4.BeautifulSoup(ingScrape.decode('utf-8', 'ignore')) 

            title = beautify.find_all('h1')[1].get_text()
            print('title: ',title)
            ingList = []
            try:
                ingList = beautify.find("div",{"class":"recipe-ingredients col-xs-12 col-sm-4"}).find_all("span",{"class":"recipe-ingredients__ingredient-instruction"})
            except Exception as e:
                print(str(e))
            
            reci = recMod.Recipe(name=title,link=newLinkPlus)
            
            try:
                reci.save()
            except Exception as e:
                print(str(e))
            
            for every in ingList:
                ingredient = every.get_text()
                print('ingre: ', ingredient)
                
                ingr = recMod.Ingredient(name=ingredient, recipe=reci)
                try:
                    ingr.save()
                except Exception as e: 
                    print(str(e))
                

            

    #print(scraper)
    link = []


def scrapeMumum(request):


    if request.method=="POST":
        send_to_token(request.POST['searchField'])
        

    return render(request, "scrapemum.html",{})


def lykkehjul(request):

    return render(request, "lykkehjul/lykkehjul.html",{})



"""
    for href in linkFinder:
        req = scrapeSite(href['href'])
        beautify = bs4.BeautifulSoup(req.decode('utf-8', 'ignore')) 
        title = beautify.find('h1').get_text()
        print('title: ',title)
        reci = recMod.Recipe(name=title,link=href['href'])
        reci.save()
        try:
            scraper= beautify.find("ul",{"class":"ingredientlist content"}).find_all("li")
        except:
            pass
        for each in scraper:
            ingredient = each.get_text()
            ingr = recMod.Ingredient(name=ingredient, recipe=reci)
            ingr.save()
            print('ingre: ', ingredient)
        
        link.append(href['href'])
"""



  
