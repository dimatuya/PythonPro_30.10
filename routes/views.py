from django.contrib import messages
from django.shortcuts import render, redirect

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
            trains = []
            for route in right_ways:
                # для городов по пути следования, выбираем необходимые поезда
                tmp = {}
                tmp['trains'] = []
                total_time = 0
                for index in range(len(route) - 1):
                    qs = Train.objects.filter(from_city=route[index],
                                              to_city=route[index + 1])
                    qs = qs.order_by('travel_time').first()
                    total_time += qs.travel_time
                    tmp['trains'].append(qs)
                    tmp['total_time'] = total_time
                if total_time <= travelling_time:
                    # если общее время в пути, меньще заданного,
                    # то добавляем маршрут в общий список
                    trains.append(tmp)
                if not trains:
                    # если список пуст, то нет таких маршрутов,
                    # которые удовлетворяли бы заданным условиям
                    messages.error(request, 'Время в пути, больше заданного.')
                    return render(request, 'routes/home.html', {'form': form})
                routes = []
                cities = {'from_city': from_city.name, 'to_city': to_city.name}
                for tr in trains:
                    # формирую список всех маршрутов
                    routes.append({'route': tr['trains'],
                    'total_time': tr['total_time'],
                    'from_city': from_city.name,
                    'to_city': to_city.name})
                sorted_routes = []
                if len(routes) == 1:
                    sorted_routes = routes
                else:
                    # если маршрутов больше одного, то сортирую их по времени
                    times = list(set(x['total_time'] for x in routes))
                    times = sorted(times)
                    for time in times:
                        for route in routes:
                            if time == route['total_time']:
                                sorted_routes.append(route)
                context = {}
                form = RouteForm()
                context['form'] = form
                context['routes'] = sorted_routes
                context['cities'] = cities
                return render(request, 'routes/home.html', context)

        return render(request, 'routes/home.html', {'form': form})
    else:
        messages.error(request, 'Создайте маршрут')
    form = RouteForm()
    return render(request, 'routes/home.html', {'form': form})


def add_route(request):
    if request.method == 'POST':
        form = RouteModelForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data
            name = data['name']
            travel_times = data['travel_times']
            from_city = data['from_city']
            to_city = data['to_city']
            trains = data['trains'].split(' ')
            trains_lst = [int(x) for x in trains if x.isalnum()]
            qs = Train.objects.filter(id__in=trains_lst)
            route = Route(name=name, from_city=from_city,
                          to_city=to_city, travel_times=travel_times)
            route.save()  # сохранение нового маршрута
            for tr in qs:  # сохранение в маршрут, поездов из списка
                route.trains.add(tr.id)
            messages.success(request, 'Маршрут был успешно сохранен.')
            return redirect('/')
    else:
        data = request.GET
        if data:  # формирую данные для формы сохранения маршрута
            travel_times = data['travel_times']
            from_city = data['from_city']
            to_city = data['to_city']
            trains = data['trains'].split(' ')
            trains_lst = [int(x) for x in trains if x.isalnum()]
            qs = Train.objects.filter(id__in=trains_lst)
            train_list = ' '.join(str(i) for i in trains_lst)
            # передача начальных данных в форму
            form = RouteModelForm(initial={'from_city': from_city, 'to_city': to_city,
                         'travel_times': travel_times, 'trains': train_list})
            route_desc = []
            for tr in qs:
                dsc = '''Поезд No{} следующий из г.{} в г.{}
                . Время в пути {}.'''.format(tr.name, tr.from_city, tr.to_city,
                                         tr.travel_time)
                route_desc.append(dsc)
            context = {'form': form, 'descr': route_desc, 'from_city': from_city,
                       'to_city': to_city, 'travel_times': travel_times}
            # assert False
            return render(request, 'routes/create.html', context)
        else:
            # защита от обращения по адресу без данных
            messages.error(request, 'Невозможно сохранить несуществующий маршрут')
            return redirect('/')
