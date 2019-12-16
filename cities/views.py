from django.shortcuts import render
from .models import City

def home(request, pk=None):
    if pk:
        city = City.objects.filter(id=pk).first()
        return render(request, 'cities/detail.html', {'object': city, })
    cities = City.objects.all()
    return render(request, 'cities/home.html', {'objects_list': cities, })

