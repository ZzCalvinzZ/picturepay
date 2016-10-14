"""picturepay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from picture.views import PictureIndexView, PaymentView

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^$', PictureIndexView.as_view(), name='picture-index'),
    url(r'^payment/$', PaymentView.as_view(), name='picture-payment'),


] + static(settings.MEDIA_URL, document_root=os.path.join(settings.MEDIA_ROOT)) \
  + static(settings.STATIC_URL, document_root=os.path.join(settings.STATIC_ROOT))
