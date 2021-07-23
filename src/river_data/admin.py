from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path

from odm.helpers import SiteDataHelper, InfluxDataHelper
from odm.models import ODMSite
from river_data.models import Site, Series, SitePhoto


class SitePhotoInline(admin.StackedInline):
    model = SitePhoto
    extra = 0


class SeriesInline(admin.TabularInline):
    model = Series
    can_delete = False
    exclude = ('odm_series_id', 'odm_series_key', 'identifier')
    readonly_fields = ('variable_code', 'variable_name', 'unit_name',
                       'unit_abbreviation', 'sampled_medium', 'identifier')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    exclude = ('odm_site_id', )
    actions = ['update_site_metadata', 'clear_site_data']
    inlines = [SeriesInline, SitePhotoInline, ]
    change_list_template = 'admin/site_changelist.html'
    readonly_fields = ('site_code', 'site_name', 'elevation_m', 'latitude', 'longitude',
                       'vertical_datum', 'state', 'county', 'watershed', 'site_type')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def update_site_metadata(self, request, sites):
        site_helper: SiteDataHelper = SiteDataHelper()
        for site in sites:
            site_helper.sync_individual_site(site)
        self.message_user(request, "successfully updated.")

    def clear_site_data(self, request, sites):
        influx_helper: InfluxDataHelper = InfluxDataHelper()
        site_codes = list(sites.values_list('site_code', flat=True))
        odm_sites = ODMSite.objects.filter(site_code__in=site_codes)
        for site in odm_sites:
            influx_helper.delete_site_data(site)
        self.message_user(request, f"Influx data deleted for sites: {list(sites)}")

    def update_sites_list(self, request):
        site_helper: SiteDataHelper = SiteDataHelper()
        site_helper.sync_sites_list()
        self.message_user(request, "All sites have been successfully updated.")
        return HttpResponseRedirect("../")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('update_list/', self.update_sites_list),
        ]
        return my_urls + urls
