from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.detail import DetailView

from .forms import HtmlForm, CityForm
from .models import City
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

def home(request, pk=None):
    cities = City.objects.all()
    paginator = Paginator(cities, 5)
    page = request.GET.get('page')
    cities = paginator.get_page(page)
    context = {'objects_list': cities, }
    return render(request, 'cities/home.html', context)


class CityDetailView(DetailView):
    queryset = City.objects.all()
    context_object_name = 'object'
    template_name = 'cities/detail.html'


class CityCreateView(SuccessMessageMixin, CreateView):
    model = City
    form_class = CityForm
    template_name = 'cities/create.html'
    success_url = reverse_lazy('cities:home')
    success_message = 'Город успешно создан!'

class CityUpdateView(SuccessMessageMixin, UpdateView):
    model = City
    form_class = CityForm
    template_name = 'cities/update.html'
    success_url = reverse_lazy('cities:home')
    success_message = 'Город отредактирован!'

class CityDeleteView(DeleteView):
    model = City
    # template_name = 'cities/delete.html'
    success_url = reverse_lazy('cities:home')

    def get(self, request, *args, **kwargs):
        messages.success(request, 'Город успешно удален!')
        return self.post(request, *args, **kwargs)
