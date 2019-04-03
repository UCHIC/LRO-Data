from django.contrib import admin

from river_data.models import Site, Series, SitePhoto


class SitePhotoInline(admin.StackedInline):
    model = SitePhoto


class SeriesInline(admin.TabularInline):
    model = Series


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    inlines = [SeriesInline, SitePhotoInline, ]

