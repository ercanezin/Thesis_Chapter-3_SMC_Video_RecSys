from . import views
from django.urls import include, re_path

app_name = 'recommender'

urlpatterns = [
 
    re_path(r"^$", views.index, name="index"),
    re_path(r"^index/$", views.index, name="index"),
    re_path('register/', views.register, name='register'),
    re_path('login_user/', views.login_user, name='login_user'),
    re_path('logout_user/', views.logout_user, name='logout_user'),
    re_path('home/', views.home, name='home'),
    re_path('profile/', views.profile, name='profile'),
    re_path('create_bundle/', views.create_bundle, name='create_bundle'),
    re_path('add_pois/', views.add_pois, name='add_pois'),
    re_path('edit_pois/', views.edit_pois, name='edit_pois'),
    re_path('get_videos/', views.get_videos, name='get_videos'),
    re_path('save_poi/', views.save_poi, name='save_poi'),
    re_path('delete_poi/', views.delete_poi, name='delete_poi'),
    re_path('bundles/', views.bundles, name='bundles'),
    re_path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    re_path('subscribe/', views.subscribe, name='subscribe'),
    re_path('deletebundle/', views.deletebundle, name='deletebundle'),
    re_path('watch_videos/', views.watch_videos, name='watch_videos'),
    re_path('update_bundle/', views.update_bundle, name='update_bundle'),
    re_path('update_bundle_end_date/', views.update_bundle_end_date, name='update_bundle_end_date'),
    re_path('update_bundle_name/', views.update_bundle_name, name='update_bundle_name'),
    re_path('log_interaction/', views.log_interaction, name='log_interaction'),
    re_path('get_video_history/', views.get_video_history, name='get_video_history'),
    re_path('decision/', views.decision, name='decision')
]

'''
urlpatterns = [
    re_path(r"^index/$", views.index, name="index"),
    re_path(r"^bio/(?P<username>\w+)/$", views.bio, name="bio"),
    re_path(r"^blog/", include("blog.urls")),
    ...,
]
'''

# urlpatterns = [
#     path('index/', views.index, name='main-view'),
#     path('bio/<username>/', views.bio, name='bio'),
#     path('articles/<slug:title>/', views.article, name='article-detail'),
#     path('articles/<slug:title>/<int:section>/', views.section, name='article-section'),
#     path('weblog/', include('blog.urls')),
#     ...
# ]
