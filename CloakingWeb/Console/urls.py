from django.urls import path
from Console.views import switch, report

urlpatterns = [
    path('console/switch/', switch),
    path('console/report/', report),
]
