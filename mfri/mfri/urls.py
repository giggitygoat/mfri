"""mfri URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from recipes import views as repViews
from django.conf import settings
from django.shortcuts import redirect
from recipes.models import Recipe, Ingredient, Token
from django.conf.urls.static import static  
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets
from rest_framework.renderers import JSONRenderer
from threading import Thread
from rest_framework import status
from django.template import loader
from django.http import HttpResponse, JsonResponse


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model=Ingredient 
        fields = ['name']


class RecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=True, read_only=True, source='ingredient_set')
    class Meta:
        model = Recipe
        fields = ['name','link','ingredient']


class ResponseThen(Response):
    def __init__(self, data, then_callback, **kwargs):
        super().__init__(data, **kwargs)
        self.then_callback = then_callback

    def close(self):
        super().close()
        self.then_callback()
        


@csrf_exempt
def p4Alarm(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            
            filer = request.FILES['file']
            destination = open("/home/www/static/alarmpics/filename.jpg", 'wb')
            for chunk in filer.chunks():
                #print(chunk)
                destination.write(chunk)
                destination.close()
            """
            filer = request.FILES['file']
            
            destination = open("/home/www/static/alarmpics/filename.jpg", 'wb')
            for chunk in filer.chunks():
                #print(chunk)
                destination.write(chunk)
            destination.close()
            """
        if 'alarm' in request.POST:
            #sendNoti = Thread(target = repViews.send_to_token,args(request.POST['alarm']))
            #sendNoti.start()
            def sendDataToMobile():
                repViews.send_to_token(request.POST['alarm'])
                
            response = Response(
            {"detail": "Den var okay! godt klaret jeg er stolt af dig!"},
            content_type="application/json",
            status=status.HTTP_200_OK)
        
            
            return ResponseThen(JsonResponse("ok"),sendDataToMobile,status=status.HTTP_200_OK)
            
        if 'token' in request.POST:
            tok = Token(identi=request.POST['token'])
            tok.save()
            return redirect('https://mfri.dk')
    if request.method == 'GET':
        image_data = open("/home/www/static/alarmpics/filename.jpg", mode='rb').read()
        return HttpResponse(image_data, content_type="image/jpg")

@csrf_exempt
def recipeViewSet(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = Recipe.objects.filter(ingredient__name__icontains='ananas').order_by('name').distinct('name')
        serializer = RecipeSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)       


        


"""                          # ViewSets define the view behavior.
class recipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

"""                                        # Routers provide an easy way of automatically determining the URL conf.
#router = routers.DefaultRouter()
#router.register(r'recipes', recipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('associates/', views.associates, name='associates'),
    path('home/', views.home),
    path('portfolio/', views.portfolio),
    path('about/', views.about),
    path('lykkehjul/', repViews.lykkehjul),
    path('opskrifter/', repViews.recipes),
    path('alarmTest/', repViews.scrapeMumum),
    #path('api/', include(router.urls)),
    path('api/recipes', recipeViewSet),
    path('api/alarm', p4Alarm),
    path('api2/', include('rest_framework.urls', namespace='rest_framework'))
    ]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
