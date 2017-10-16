from django.shortcuts import render
from django.http import HttpResponse
from .models import LocationSearch
from .forms import LocationForm
import requests
from operator import itemgetter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone


def search(request):
    recent_searches = LocationSearch.objects.order_by('-search_date')[:10]
    #LocationSearch.objects.all().delete()
    if request.method == 'GET':
        form = LocationForm(request.GET)

        if form.is_valid():
            print("form is valid")

            food = request.GET.get('food', '')
            location = request.GET.get('location', '')
            for obj in recent_searches:
                print("recent searches: " + obj.food + " " + obj.location + " " + str(obj.search_date))
            context = {
                'recent_searches': recent_searches,
                'form_box': form,
            }
            print(food, location)
            if food == "" and location == "":
                print("food and location info not found")
                return render(request, 'foursquare/maintemp.html', context)

            else:
                try:
                    total_results = return_total_results(food, location)
                    if total_results == 0:
                        return render(request, 'foursquare/maintemp.html', context)
                    search_obj = LocationSearch.objects.get(food=food, location=location)

                    print(str(search_obj.search_date))
                    search_obj.search_date = timezone.now()
                    search_obj.save()

                    print(str(search_obj.search_date))

                    print("test ???")

                except LocationSearch.DoesNotExist:
                    #if total_results == 0:
                     #   print("Object will not be saved:  " + str(search_obj.food) + " " + str(search_obj.location))
                    #else:
                    search_obj = LocationSearch.objects.create(food=food, location=location)
                    search_obj.save()
                except LocationSearch.MultipleObjectsReturned:
                    print("object exists")
                finally:
                    print("Total results: " + str(total_results))
                    if total_results != 0:
                        search_obj.search_date = timezone.now()
                        recent_searches = LocationSearch.objects.order_by('-search_date')[:10]
                        current_search = recent_searches[0]
                        context = {
                            'recent_searches': recent_searches,
                            'form_box': form,
                            'current_search': current_search,
                        }
                        for obj in recent_searches:
                            print("recent searches: "+obj.food+" "+obj.location)
                        offset = 0
                        return paging(request, search_obj, context)
        else:
            print("form is not valid")
            context = {
                'recent_searches': recent_searches,
                'form_box': form,
            }
            return render(request, 'foursquare/maintemp.html', context)
    else:

        form = LocationForm()
        context = {
                'recent_searches': recent_searches,
                'form_box': form,
        }
        return render(request, 'foursquare/maintemp.html', context)


def api(request, search_obj, offset, context, ):

    url = 'https://api.foursquare.com/v2/venues/explore'
    params = dict(
        client_id='V131V0IPODZOAI4DH0TXB0W1VF4R1QCAHASGHJI35D3KJLWK',
        client_secret='L5RZFRA1K2KPH33H12BFD3MECOJKEBIJSLP14KXYRYW3A5AF',
        v='20170801',
        near=search_obj.location,
        query=search_obj.food,
        limit=10,
        offset=offset,
    )
    resp = requests.get(url=url, params=params)
    data = resp.json()
    venue_list = []
    for item in data['response']['groups']:
        for groups in item['items']:
            name = groups.get('venue').get('name')
            phone_number = groups.get('venue', {}).get('contact').get('formattedPhone')
            if phone_number == None:
                phone_number = 'N/A'
            checkin_count = groups.get('venue', {}).get('stats').get('checkinsCount')
            venue = {'name': name, 'phone_number': phone_number, 'checkin_count': checkin_count}
            venue_list.append(venue)
    print("selam")
    print(venue_list)
    venue_list_length = len(venue_list)
    print("venue list length: " + str(venue_list_length))
    sorted_list = sorted(venue_list, key=itemgetter('checkin_count'), reverse=True)
    context2 = {
        'venue_list': sorted_list,
        }
    context.update(context2)
    return render(request, 'foursquare/maintemp.html',  context)
    #return paging(request, total_results, context)
    #return listing(request, context, sorted_list)


def paging(request, search_obj, context):

    total_results = return_total_results(search_obj.food, search_obj.location)
    page_list = []
    if total_results % 10 == 0:
        total_page_numbers = int(total_results / 10)
    else:
        total_page_numbers = int(total_results / 10 + 1)

    for i in range(total_page_numbers):
        page_list.append(i+1)
    # print("---")
    # print(page_list)
    page = request.GET.get('page')
    if page is None or int(page) < 0:
        page = 1
    current_page = int(page)
    print(page)
    next_page = int(current_page) + 1
    previous_page = int(current_page) - 1
    offset = (int(current_page)-1) * 10
    print(offset)
    print(current_page)
    last_page = len(page_list)
    context4 = {
         'previous_page': previous_page,
         'next_page': next_page,
         'current_page': current_page,
         'total_page_numbers': total_page_numbers,
         'page_list': page_list,
         'last_page': last_page,
     }
    print('Previous page:', str(previous_page))
    print('Current page:', str(current_page))
    print('Next page:', str(next_page))
    print('')
    context.update(context4)
    return api(request, search_obj, offset, context)

def return_total_results(food, location):
    url = 'https://api.foursquare.com/v2/venues/explore'
    params = dict(
        client_id='V131V0IPODZOAI4DH0TXB0W1VF4R1QCAHASGHJI35D3KJLWK',
        client_secret='L5RZFRA1K2KPH33H12BFD3MECOJKEBIJSLP14KXYRYW3A5AF',
        v='20170801',
        near=location,
        query=food,
        limit=10,
        offset=0,
    )
    resp = requests.get(url=url, params=params)
    data = resp.json()
    try:
        total_results = data['response']['totalResults']
    except KeyError:
        total_results = 0
    return total_results


