from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from river_data.models import Site


class SitesView(ListView):
    template_name: str = 'river_data/sites.html'
    queryset = Site.objects.all()
    context_object_name: str = 'sites'
