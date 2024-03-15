from .models import *
from random import shuffle
import numpy as np
from .ratingsPredictor import RatingsPredictor
from .trustProcessor import *

"""
Buraya bir tur simulasyon yazmamiz lazim
Bu similasyon da 8 kullanici olusturmali hatta bu simulasyon icin bir arayuz olusturabiliriz. Olusturacagimiz arayuz de kullanicilar ve POI ler olacak asagidaki gibi.
Simulasyonda kullanicilar videolarin metadatasina(youtube izlenme datasi like/watch  datasi) gore like dislike ve watch islemi yapacaklar ve buna gore RecListler olsuturulacak. 
Simulasyon sirasinda olusturulacak kullanicilara profil verilecek mesela Most trusted yada liker disliker gibi, bu kullanicilarin ezici influnce ini etkilemek icin normalization yapmaliyiz. 

                POI-1                   POI-2                  .............POI-N
    V1,V2,..........V40 V1, V2...................V38            V1................V39
USer1
User2
USer3
USer4
.
.
.
User8



example quick value filler

subscribers = Subscription.objects.filter(bundle=bundle).exclude(user=usr)


bundle=Bundle.objects.get(pk=110)  buraya ornek bir inerarary id girelim


subscribers=Subscription.objects.filter(bundle=bundle) 

vids=Video.objects.filter(bundle=bundle)
for sub in subscribers:
    import random
    for vid in vids:
        if vid.id%2 == 0:
            rnd=random.randint(-1,1)
            wh=WatchHistory(user=sub.user,bundle=bundle,video=vid,is_liked=rnd)
            wh.save()

"""