from django.shortcuts import render
from django.db.models import Q
from recipes import models as recMod
import webbrowser, bs4, sys, requests, time
import numpy as np
import operator
from functools import reduce
from django.db.models import Prefetch
from django.contrib import messages
from django import template

register = template.Library()

@register.filter
def in_list(value, the_list):
    value = str(value)
    return value in the_list.split(',')


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
            print('ingre: ', ingredient)
        
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
        print(len(filterList))
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
    request.session['ingre'] = ingreList
    #print("HEEER",multipleFilterList)  
    #print(multipleFilterList)  
    if len(multipleFilterList)>=1:
        filterList = multipleFilterList
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
    linkFinder = vegSoup.find("div",{"class":"section mute-heading section--expanded teaser-deck-d"})
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
        print(newLink)
        if not '#' in newLink:
            ingScrape = scrapeSite("https://dr.dk"+newLink)
            beautify = bs4.BeautifulSoup(ingScrape.decode('utf-8', 'ignore')) 

            title = beautify.find('h1').get_text()
            print('title: ',title)
            ingList = []
            try:
                ingList = beautify.find("ul",{"class":"recipe-ingredients col-xs-12 col-sm-4"}).find_all("li")
            except Exception as e:
                print(str(e))
            """
            reci = recMod.Recipe(name=title,link=newLink)
            
            try:
                reci.save()
            except Exception as e:
                print(str(e))
            """
            for every in ingList:
                ingredient = every.get_text()
                print('ingre: ', ingredient)
                """
                #ingr = recMod.Ingredient(name=ingredient, recipe=reci)
                try:
                    #ingr.save()
                except Exception as e: 
                    print(str(e))
                """

            

    #print(scraper)
    link = []


def scrapeMumum(request):


    if request.method=="POST":
        antalSider = 156
        url= 'https://dr.dk/mad/opskrift/'
        heleMummum(url)

        


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



  
