import json
import logging
import multiprocessing.dummy as mp
import random
import re
from datetime import *
from functools import partial
from random import shuffle
import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .YoutubeAPI import *
from .decisionSystem import DecisionSystem
from .forms import *
from .generateRec import GenerateRec
from .models import *
from .trustProcessor import TrustProcessor
from TravelMadeEasy.settings import YOUTUBE_DEVELOPER_KEY

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

RECOMMENDATION_COUNT = 9


def index(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return render(request, 'recommender/index.html', {})
        else:
            return redirect('recommender:home')

    elif request.method == 'POST':

        if 'login' in request.POST:
            return redirect('recommender:login_user')

        elif 'createAccount' in request.POST:
            return redirect('recommender:register')


def login_user(request):
    if request.user.is_authenticated:
        return render(request, 'recommender/home.html')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('recommender:home')
            else:
                return render(request, 'recommender/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'recommender/login.html', {'error_message': 'Invalid login'})
    return render(request, 'recommender/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('recommender:home')

    return render(request, 'recommender/register.html', {"form": form})


def logout_user(request):
    logout(request)
    return redirect('/')


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        subscriptions = Subscription.objects.filter(user=request.user)

        return render(request, 'recommender/home.html', {'subscriptions': subscriptions})


def bundles(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        user_subscriptions = Subscription.objects.filter(user=request.user)
        subs = []
        for sb in user_subscriptions:
            subs.append(sb.bundle.id)

        all_bundles = Bundle.objects.all()

        return render(request, 'recommender/bundles.html',
                      {'bundles': all_bundles, 'user_subscriptions': subs, 'timenow': timezone.now()})


@csrf_exempt
def subscribe(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            bundle_id = request.POST['bundle_id']
            bundle = Bundle.objects.get(id=bundle_id)
            subscription = Subscription(bundle=bundle, user=request.user)
            subscription.save()

        return redirect('recommender:bundles')


@csrf_exempt
def unsubscribe(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            bundle_id = request.POST["bundle_id"]
            Subscription.objects.filter(user=request.user, bundle__id=bundle_id).delete()

        return redirect('recommender:bundles')


@csrf_exempt
def deletebundle(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            bundle_id = request.POST["bundle_id"]
            Bundle.objects.filter(user=request.user, id=bundle_id).delete()
            # Bundle.objects.all().delete() to clean all bundles...use with caution!!!
        return redirect('recommender:bundles')


def profile(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        updated = False

        return render(request, 'recommender/profile.html',
                      {
                          'updated': updated,
                      })


def create_bundle(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        return render(request, 'recommender/create_bundle.html')


def add_pois(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        form = CreateBundleForm(request.POST or None)
        if form.is_valid():
            bundle = form.save(commit=False)
            bundle.user = request.user
            bundle.end_date = datetime.datetime.strptime(request.POST['end_date'], '%Y-%m-%d').replace(
                tzinfo=timezone.now().tzinfo)
            bundle.save()

            subscription = Subscription(user=request.user, bundle=bundle)
            subscription.save()

            if bundle is not None:
                return render(request, 'recommender/add_pois.html', {"bundle": bundle, "range": range(10)})

        return render(request, 'recommender/create_bundle.html')


def edit_pois(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.GET.get('bundleid'):
            bundleid = request.GET.get('bundleid')
            bundleObj = Bundle.objects.get(user=request.user, id=bundleid)
            if bundleObj is not None:
                return render(request, 'recommender/edit_pois.html', {"bundle": bundleObj, "range": range(10)})
            else:
                return redirect('recommender:bundles')
        else:
            return redirect('recommender:bundles')


@csrf_exempt
def get_videos(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            place = request.POST["place"]
            yt_videos = YoutubeAPI.youtube_search(place, 30)

            html = render_to_string('recommender/yt_videos.html', {'videos': yt_videos, 'place': place})
            return HttpResponse(html)

        return render(request, 'recommender/create_bundle.html')


@csrf_exempt
def save_poi(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        poiObj = None
        if request.method == "POST":
            place = request.POST["poi"]
            videos = request.POST.getlist("videos")
            bundle_id = request.POST["bundleId"]

            bundle = Bundle.objects.get(id=bundle_id)
            poi = POI(bundle=bundle, location_name=place)
            poi.save()

            p = mp.Pool(len(videos))
            p.map(partial(video_saver, bundle, poi), videos)
            p.close()
            p.join()

            poiObj = model_to_dict(poi)
            poiObj["numOfVideos"] = len(videos)

        return JsonResponse(json.dumps(poiObj), safe=False)


def video_saver(bundle, poi, video_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_DEVELOPER_KEY)

    # Make an API request to fetch video details
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id
    )
    response = request.execute()

    if response['items']:  # Check if we got a valid result
        video_data = response['items'][0]

        video = Video(bundle=bundle,
                      poi=poi,
                      video_url='https://www.youtube.com/watch?v=' + video_id,
                      video_title=video_data['snippet'].get('title', ""),
                      video_owner=video_data['snippet'].get('channelTitle', ""),
                      video_view_count=int(video_data['statistics'].get('viewCount', 0)),
                      video_length=calculate_video_length(video_data['contentDetails'].get('duration')),
                      video_description=video_data['snippet'].get('description', "").encode('ascii', 'ignore'),
                      video_rating=0.0,  # YouTube API v3 might not provide this directly
                      video_likes=int(video_data['statistics'].get('likeCount', 0)),
                      video_dislikes=int(video_data['statistics'].get('dislikeCount', 0)),
                      video_duration=calculate_video_length(video_data['contentDetails'].get('duration'))
                      )
        video.save()
    else:
        print('Vide Not Found')


# Helper function to convert ISO 8601 duration to seconds
def calculate_video_length(iso_duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0
        return hours * 3600 + minutes * 60 + seconds
    else:
        return 0  # Handle invalid duration formats


@csrf_exempt
def delete_poi(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            bundle_id = request.POST["bundle_id"]
            poi_id = request.POST["poi_id"]
            bundleObj = Bundle.objects.filter(user=request.user, id=bundle_id)
            POI.objects.filter(id=poi_id).delete()
        return JsonResponse(json.dumps({"success": 1}), safe=False)


@csrf_exempt
def update_bundle(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            bundle_id = request.POST["bundle_id"]
            number_of_final_dest = request.POST["number_of_final_dest"]
            if int(number_of_final_dest) < 2:
                return JsonResponse(json.dumps({"success": 0}), safe=False)

            Bundle.objects.filter(user=request.user, id=bundle_id).update(number_of_final_dest=number_of_final_dest)

    return JsonResponse(json.dumps({"success": 1}), safe=False)


@csrf_exempt
def update_bundle_end_date(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            bundle_id = request.POST["bundle_id"]
            bundle_end_date = request.POST["bundle_end_date"]
            result = Bundle.objects.filter(user=request.user, id=bundle_id).update(end_date=bundle_end_date)
            return JsonResponse(json.dumps({"success": result}), safe=False)

        return JsonResponse(json.dumps({"success": 0}), safe=False)


@csrf_exempt
def update_bundle_name(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            bundle_id = request.POST["bundle_id"]
            bundle_name = request.POST["bundle_name"]
            result = Bundle.objects.filter(user=request.user, id=bundle_id).update(name=bundle_name)
            return JsonResponse(json.dumps({"success": result}), safe=False)

        return JsonResponse(json.dumps({"success": 0}), safe=False)


@csrf_exempt
def log_interaction(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')

    if request.method == "POST":
        video_id = request.POST["video_id"]
        interaction = request.POST["interaction"]
        bundle_id = request.POST["bundle_id"]

        video_obj = Video.objects.get(id=video_id)
        bundle_obj = Bundle.objects.get(id=bundle_id)

        if video_obj is not None:
            watch_hist = WatchHistory.objects.filter(user=request.user, video=video_obj)
            rec_list_item = RecListItem.objects.filter(user=request.user, video=video_obj).order_by('-id')
            if interaction == '1' and watch_hist.count() == 0:
                wh = WatchHistory(user=request.user, video=video_obj, bundle=bundle_obj)
                wh.save()

                if rec_list_item.count() > 0:
                    rec_list_item[0].is_liked = 0
                    rec_list_item[0].save()

            elif interaction == '2' and watch_hist.count() != 0:
                wh = watch_hist.latest('id')
                wh.is_liked = 1
                wh.save()
                if rec_list_item.count() > 0:
                    rec_list_item[0].is_liked = 1
                    rec_list_item[0].save()

            elif interaction == '3' and watch_hist.count() != 0:
                wh = watch_hist.latest('id')
                wh.is_liked = -1
                wh.save()
                if rec_list_item.count() > 0:
                    rec_list_item[0].is_liked = -1
                    rec_list_item[0].save()

        return JsonResponse(json.dumps({"success": 1}), safe=False)

    return JsonResponse(json.dumps({"success": 0}), safe=False)


def watch_videos(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:

        bundle_id = request.GET["bundleId"]
        bundle = Bundle.objects.get(id=bundle_id)

        if bundle is not None and bundle.end_date <= timezone.now():
            response = redirect('recommender:decision')
            response['Location'] += '?bundleId=' + bundle_id
            return response

        usr = request.user

        if bundle is not None:

            # CREATE VIDEO DICT for PER POI
            pois = list(bundle.poi_set.all().order_by('id'))
            pois_dict = {}
            for poi in pois:
                vids = list(poi.video_set.all())
                shuffle(vids)
                pois_dict[poi.location_name] = vids[:RECOMMENDATION_COUNT]  # Take first 9 videos from the list

            subscribers = Subscription.objects.filter(bundle=bundle).exclude(user=usr)
            watch_histories = WatchHistory.objects.filter(bundle=bundle)
            user_wh_count = watch_histories.filter(user=usr).count()
            trust_replaced_videos = None
            # Make sure user has watched at least twice amount of pois in the list
            if (user_wh_count >= len(pois) * 2) and len(watch_histories) >= len(subscribers) * len(pois) * 2:
                vid_ids = GenerateRec().generate_rec_list(bundle, usr, RECOMMENDATION_COUNT)

                # pick a random subcriber
                sub = random.choice(subscribers)
                trust_rec_vid_ids = GenerateRec().generate_rec_list(bundle,
                                                                    sub.user,
                                                                    RECOMMENDATION_COUNT)

                trust_replaced_videos = TrustProcessor().get_replaced_video_list(vid_ids,
                                                                                 trust_rec_vid_ids,
                                                                                 usr,
                                                                                 sub.user,
                                                                                 bundle,
                                                                                 RECOMMENDATION_COUNT)

            return render(request, 'recommender/watch_videos.html',
                          {"bundle": bundle, "pois_dict": pois_dict, "recommended_videos": trust_replaced_videos})

        return render(request, 'recommender/home.html')


@csrf_exempt
def get_video_history(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        if request.method == "POST":
            bundle_id = request.POST["bundle_id"]

            bundle = Bundle.objects.get(id=bundle_id)
            watch_hist_set = WatchHistory.objects.filter(user=request.user, video__bundle__exact=bundle)
            wh_list = []
            for wh in watch_hist_set:
                wh_list.append(model_to_dict(wh))

            return JsonResponse(json.dumps(wh_list), safe=False)
        else:
            return JsonResponse({"success": 0}, safe=False)


def decision(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
        bundle_id = request.GET["bundleId"]
        bundle = Bundle.objects.get(id=bundle_id)
        if bundle is not None:
            result_dict = DecisionSystem().getdecision(bundle)
            return render(request, 'recommender/decision.html', {'result_dict': result_dict})
        else:
            return render(request, 'recommender/home.html')
