from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView

from river_data.models import Site


class SitesView(ListView):
    template_name: str = 'river_data/sites.html'
    queryset = Site.objects.all()
    context_object_name: str = 'sites'


class SiteDetailView(DetailView):
    model = Site
    context_object_name = 'site'
    template_name = 'river_data/site_details.html'
