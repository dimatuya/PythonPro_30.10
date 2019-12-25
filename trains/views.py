from django.contrib.messages.views import SuccessMessageMixin
from django.core.checks import messages
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView

from trains.forms import TrainForm
from trains.models import Train


def home(request, pk=None):
    trains = Train.objects.all()
    paginator = Paginator(trains, 5)
    page = request.GET.get('page')
    trains = paginator.get_page(page)
    context = {'objects_list': trains, }
    return render(request, 'trains/home.html', context)

class TrainCreateView(SuccessMessageMixin, CreateView):
    model = Train
    form_class = TrainForm
    template_name = 'trains/create.html'
    success_url = reverse_lazy('trains:home')
    success_message = 'Поезд успешно создан!'


class TrainUpdateView(SuccessMessageMixin, UpdateView):
    model = Train
    form_class = TrainForm
    template_name = 'trains/update.html'
    success_url = reverse_lazy('trains:home')
    success_message = 'Поезд отредактирован!'

class TrainDeleteView(DeleteView):
    model = Train
    # template_name = 'trains/delete.html'
    success_url = reverse_lazy('trains:home')

    def get(self, request, *args, **kwargs):
        messages.success(request, 'Поезд успешно удален!')
        return self.post(request, *args, **kwargs)


class TrainDetailView(DetailView):
    queryset = Train.objects.all()
    context_object_name = 'object'
    template_name = 'trains/detail.html'
