from django.contrib import admin
from .models import *
from embed_video.admin import AdminVideoMixin

class MyModelAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass

admin.site.register(Bundle, MyModelAdmin)
admin.site.register(Video, MyModelAdmin)
admin.site.register(POI, MyModelAdmin)
admin.site.register(Subscription, MyModelAdmin)
admin.site.register(WatchHistory, MyModelAdmin)
