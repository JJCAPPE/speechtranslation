from django.urls import path
from . import views

#url configuration
# path( 'url' , function )  --  no need to add mainapp/ as we configured all mainapp/ to be handled by this file in speechapp.urls.py

urlpatterns = [
    path('test/', views.test_request),
    path('translateview/', views.SpeechTranslator.as_view(), name='translateview')
]