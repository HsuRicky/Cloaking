from django.urls import path
from ABPage.views import index, cuttly

urlpatterns = [
    path('', index),
    path('cuttly/<str:no>/', cuttly)
]
