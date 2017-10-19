from django.shortcuts import render
from .models import LocationSearch
from .forms import LocationForm
import requests
from operator import itemgetter
from django.utils import timezone


def search(request):
    recent_searches = get_recent_searches()
    form = LocationForm(request.GET)
    if form.is_valid():
            print("form is valid")
            cd = form.cleaned_data
            food = cd['food']
            location = cd['location']
            print(food, location)
            offset = request.GET.get('offset')
            if offset is None:
                offset = 0
            url = 'https://api.foursquare.com/v2/venues/explore'
            params = dict(
                client_id='V131V0IPODZOAI4DH0TXB0W1VF4R1QCAHASGHJI35D3KJLWK',
                client_secret='L5RZFRA1K2KPH33H12BFD3MECOJKEBIJSLP14KXYRYW3A5AF',
                v='20170801',
                near=location,
                query=food,
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
                    if phone_number is None:
                        phone_number = 'N/A'
                    check_in_count = groups.get('venue', {}).get('stats').get('checkinsCount')
                    venue_list = get_venue_list(venue_list, name, phone_number, check_in_count)
            print("selam")
            print(venue_list)
            print("venue list length: " + str(len(venue_list)))
            sorted_list = sorted(venue_list, key=itemgetter('checkin_count'), reverse=True)
            po_exists = False  # previous offset
            no_exists = False  # next offset
            next_offset = int(offset) + 10
            prev_offset = int(offset) - 10
            try:
                total_results = data['response']['totalResults']
            except KeyError:
                total_results = 0
            if total_results != 0:
                current_search = get_and_save_the_obj(food, location)
                if int(offset) > 0:  # previous link exists after first page
                    po_exists = True
                if int(offset) < total_results:  # next link exits until its last page
                    no_exists = True
            context = {
                'venue_list': sorted_list,
                'recent_searches': recent_searches,
                'form_box': form,
                'next_offset': next_offset,
                'no_exists': no_exists,
                'prev_offset': prev_offset,
                'po_exists': po_exists,
                'current_search': current_search,
                'total_venue_count': total_results,

            }
            return render(request, 'foursquare/maintemp.html', context)
    else:
        form = LocationForm()
        context = {
            'recent_searches': recent_searches,
            'form_box': form,
        }
        return render(request, 'foursquare/maintemp.html', context)


def get_venue_list(venue_list, name, phone_number, check_in_count):

    venue_list.append(get_venue_dict(name, phone_number, check_in_count))
    return venue_list


def get_venue_dict(name, phone_number, check_in_count):
    venue = {'name': name, 'phone_number': phone_number, 'checkin_count': check_in_count}
    return venue


def get_recent_searches():
    return LocationSearch.objects.order_by('-search_date')[:10]


def get_and_save_the_obj(food, location):
    # search for the object in database, if objects doesn't exist,
    # then create it, finally change its search_date to now,
    # so it will appear on top of the recent_searches list.
    try:
        search_obj = LocationSearch.objects.get(food=food, location=location)
        print(str(search_obj.search_date))
        search_obj.search_date = timezone.now()
        search_obj.save()
        print(str(search_obj.search_date))
        print("test ???")
    except LocationSearch.DoesNotExist:
        search_obj = LocationSearch.objects.create(food=food, location=location)
    except LocationSearch.MultipleObjectsReturned:
        print("object exists")
    finally:
        search_obj.search_date = timezone.now()
        recent_searches = LocationSearch.objects.order_by('-search_date')[:10]
        for obj in recent_searches:
            print("recent searches: " + obj.food + " " + obj.location)
        return search_obj



            # page_list = []
            # if total_results % 10 == 0:
            #     total_page_numbers = int(total_results / 10)
            # else:
            #     total_page_numbers = int(total_results / 10 + 1)
            #
            # for i in range(total_page_numbers):
            #     page_list.append(i + 1)
            #     # print("---")
            #     # print(page_list)
            # page = request.GET.get('page')
            # if page is None or int(page) < 0 or int(page) > total_page_numbers:
            #     page = 1
            # current_page = int(page)
            # print(page)
            # next_page = int(current_page) + 1
            # previous_page = int(current_page) - 1
            # offset = (int(current_page) - 1) * 10
            # print(offset)
            # print(current_page)
            # last_page = len(page_list)
            # print('Previous page:', str(previous_page))
            # print('Current page:', str(current_page))
            # print('Next page:', str(next_page))
# venue = {'name': name, 'phone_number': phone_number, 'checkin_count': check_in_count}
                    # venue_list.append(venue)

        # 'previous_page': previous_page,
        # 'next_page': next_page,
        # 'current_page': current_page,
        # 'total_page_numbers': total_page_numbers,
        # 'page_list': page_list,
        # 'last_page': last_page,