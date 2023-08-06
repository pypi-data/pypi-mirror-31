"""brythonapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from django.conf.urls.static import static
from django.conf import settings

from android.core import main
from radiant.framework.views import BrythonFramework


urlpatterns = [
    #path('admin/', admin.site.urls),

    path('', BrythonFramework.as_view(), name='home'),
    path('system_python', main.Brython.as_view(), name='system_python'),
    path('splash', TemplateView.as_view(template_name="splash.html"), name="splash"),

    path('d4a/', include('radiant.framework.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
