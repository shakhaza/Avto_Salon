from django.shortcuts import render, get_object_or_404
from .models import Car
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

# Create your views here.
def cars(request):
    cars = Car.objects.order_by('-created_date')
    paginator = Paginator(cars, 4)
    page = request.GET.get('page')
    paged_cars = paginator.get_page(page)

    data = {
        'cars': paged_cars,
        'values': request.GET,
        **Car.get_search_fields()
    }
    return render(request, 'cars/cars.html', data)

def car_detail(request, id):
    single_car = get_object_or_404(Car, pk=id)

    data = {
        'single_car': single_car,
    }
    return render(request, 'cars/car_detail.html', data)


def search(request):
    cars = Car.objects.order_by('-created_date')

    # Mapping GET parameters to model fields
    filter_mappings = {
        'model': 'model__iexact',
        'city': 'city__iexact',
        'year': 'year__iexact',
        'body_style': 'body_style__iexact',
        'transmission': 'transmission__iexact',
    }

    filters = {}
    for param, field in filter_mappings.items():
        value = request.GET.get(param)
        if value:
            filters[field] = value

    cars = cars.filter(**filters)

    keyword = request.GET.get('keyword')
    if keyword:
        cars = cars.filter(Q(description__icontains=keyword) | Q(car_title__icontains=keyword))

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        cars = cars.filter(price__gte=min_price)
    if max_price:
        cars = cars.filter(price__lte=max_price)

    data = {
        'cars': cars,
        'values': request.GET,
        **Car.get_search_fields()
    }
    return render(request, 'cars/search.html', data)
