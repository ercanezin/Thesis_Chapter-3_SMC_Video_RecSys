from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
import json
from .forms import *
from .models import *
from django.views.decorators.csrf import csrf_exempt
from .YoutubeAPI import *
import pafy
from random import shuffle
from django.forms.models import model_to_dict
import numpy as np
from .ratingsPredictor import RatingsPredictor
from .decisionSystem import DecisionSystem
from django.utils import timezone
import multiprocessing.dummy as mp
from datetime import datetime
from functools import partial
import logging
from .generateRec import GenerateRec
from .trustProcessor import TrustProcessor
import random

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

IS_WATCHED = 0
IS_LIKED = 1
IS_DISLIKED = -1

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
            print(request.POST['end_date'])
            bundle.end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
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
            yt_videos = YoutubeAPI.youtube_search(place, 20)  # TODO: slider

            html = render_to_string('recommender/yt_videos.html', {'videos': yt_videos, 'place': place})
            return HttpResponse(html)

        return render(request, 'recommender/create_bundle.html')


@csrf_exempt
def save_poi(request):
    if not request.user.is_authenticated:
        return render(request, 'recommender/login.html')
    else:
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


def video_saver(bundle, poi, v):
    videourl = 'https://www.youtube.com/watch?v=' + v
    video_data = pafy.new(videourl)
    video = Video(bundle=bundle,
                  poi=poi,
                  video_url=videourl,
                  video_title=video_data.title or "",
                  video_owner=video_data.author or "",
                  video_view_count=video_data.viewcount or 0,
                  video_length=video_data.length or 0,
                  video_description=video_data.description.encode('ascii', 'ignore') or "",
                  video_rating=video_data.rating or 0.0,
                  video_likes=video_data.likes or 0,
                  video_dislikes=video_data.dislikes or 0,
                  video_duration=video_data.duration or 0
                  )
    video.save()


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


# Watched:1
# liked:2
# disliked:3
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
                vids = list(poi.video_set.all().order_by('id'))
                shuffle(vids)
                pois_dict[poi.location_name] = vids[:RECOMMENDATION_COUNT]  # Take first 9 videos from the list

            subscribers = Subscription.objects.filter(bundle=bundle).exclude(user=usr)
            watch_histories = WatchHistory.objects.filter(bundle=bundle)
            wh_count = watch_histories.filter(user=usr).count()

            other_wh_count = watch_histories.exclude(user=usr).count()
            numofvideos = Video.objects.filter(bundle=bundle).count()
            vid_ids = None
            # Make sure user has watched at least 10 % of videos and all subscriber has watched at least 5% of videos
            # also make sure there is other users exist with initial watch from themas well.
            if subscribers.count() > 0 and wh_count != 0 and numofvideos / wh_count <= 10 and (
                    numofvideos * subscribers.count()) / other_wh_count < 5:
                vid_ids = GenerateRec().generate_rec_list(bundle, usr, RECOMMENDATION_COUNT)

                # pick a random subcriber
                sub = random.choice(subscribers)

                rec_vid_ids = GenerateRec().generate_rec_list(bundle,
                                                              sub.user,
                                                              RECOMMENDATION_COUNT)

                vid_ids = TrustProcessor().get_replaced_video_list(vid_ids,
                                                                   rec_vid_ids,
                                                                   usr,
                                                                   sub.user,
                                                                   bundle,
                                                                   RECOMMENDATION_COUNT)

            return render(request, 'recommender/watch_videos.html',
                          {"bundle": bundle, "pois_dict": pois_dict, "recommended_videos": vid_ids})

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
            return render(request, 'recommender/decision.html',
                          DecisionSystem().getdecision(bundle, [IS_WATCHED, IS_LIKED, IS_DISLIKED]))
        else:
            return render(request, 'recommender/home.html')
