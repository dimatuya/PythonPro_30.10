from django.contrib import messages
from django.shortcuts import render

from trains.models import Train
from .forms import *


def home(request):
    form = RouteForm()
    return render(request, 'routes/home.html', {'form': form})

def dfs_paths(graph, start, goal):
    """Функция поиска всех возможных маршрутов
    из одного города в другой. Вариант посещения
    одного и того же города более одного раза,
    не рассматривается.
    """
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        if vertex in graph.keys():
            for next_ in graph[vertex] - set(path):
                if next_ == goal:
                    yield path + [next_]
                else:
                    stack.append((next_, path + [next_]))


def get_graph():
    qs = Train.objects.values('from_city')
    from_city_set = set(i['from_city'] for i in qs)
    graph = {}
    for city in from_city_set:
        trains = Train.objects.filter(from_city=city).values('to_city')
        tmp = set(i['to_city'] for i in trains)
        graph[city] = tmp
    return graph


def find_routes(request):
    if request.method == "POST":
        form = RouteForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data
            from_city = data['from_city']
            to_city = data['to_city']
            cities = data['cities']
            travelling_time = data['travelling_time']
            graph = get_graph()
            all_ways = list(dfs_paths(graph, from_city.id, to_city.id))
            if len(all_ways) == 0:
                # нет ни одного маршрута для данного поиска
                messages.error(request, 'Маршрута, удовлетворяющего условиям не  существует.')
                return render(request, 'routes/home.html', {'form': form})
            if cities:
                # если есть города, через которые нужно проехать
                across_cities = [city.id for city in cities]
                right_ways = []
                for way in all_ways:
                    # тогда отбираем те маршруты, которые проходят через них
                    if all(point in way for point in across_cities):
                        right_ways.append(way)
                if not right_ways:
                    # когда список маршрутов пуст
                    messages.error(request, 'Маршрут, через эти города невозможен ')
                return render(request, 'routes/home.html', {'form': form})
            else:
                right_ways = all_ways
        return render(request, 'routes/home.html', {'form': form})
    else:
        messages.error(request, 'Создайте маршрут')
    form = RouteForm()
    return render(request, 'routes/home.html', {'form': form})
