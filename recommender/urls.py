from django.conf.urls import url
from . import views
from django.urls import path

app_name = 'recommender'

urlpatterns = [

    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login_user/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('create_bundle/', views.create_bundle, name='create_bundle'),
    path('add_pois/', views.add_pois, name='add_pois'),
    path('edit_pois/', views.edit_pois, name='edit_pois'),
    path('get_videos/', views.get_videos, name='get_videos'),
    path('save_poi/', views.save_poi, name='save_poi'),
    path('delete_poi/', views.delete_poi, name='delete_poi'),
    path('bundles/', views.bundles, name='bundles'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('deletebundle/', views.deletebundle, name='deletebundle'),
    path('watch_videos/', views.watch_videos, name='watch_videos'),
    path('update_bundle/', views.update_bundle, name='update_bundle'),
    path('update_bundle_end_date/', views.update_bundle_end_date, name='update_bundle_end_date'),
    path('update_bundle_name/', views.update_bundle_name, name='update_bundle_name'),
    path('log_interaction/', views.log_interaction, name='log_interaction'),
    path('get_video_history/', views.get_video_history, name='get_video_history'),
    path('decision/', views.decision, name='decision')
]

# urlpatterns = [
#     path('index/', views.index, name='main-view'),
#     path('bio/<username>/', views.bio, name='bio'),
#     path('articles/<slug:title>/', views.article, name='article-detail'),
#     path('articles/<slug:title>/<int:section>/', views.section, name='article-section'),
#     path('weblog/', include('blog.urls')),
#     ...
# ]
