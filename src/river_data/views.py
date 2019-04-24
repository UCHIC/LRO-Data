from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView

from river_data.models import Site, Series


class SitesView(ListView):
    template_name: str = 'river_data/sites.html'
    queryset = Site.objects.all()
    context_object_name: str = 'sites'


class SiteDetailView(DetailView):
    model = Site
    context_object_name = 'site'
    template_name = 'river_data/site_details.html'
    queryset = Site.objects\
        .prefetch_related('photos')\
        .prefetch_related(Prefetch('series', queryset=Series.objects.filter(active=True), to_attr='active_series'))\
        .all()
