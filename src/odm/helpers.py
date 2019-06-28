from typing import Dict

from django.conf import settings

from odm.models import ODMSite, ODMSeries, ODMUnit
from river_data.models import Site, Series


class SiteDataHelper(object):
    watershed: str = settings.WATERSHED
    units: Dict[int, ODMUnit] = ODMUnit.objects.in_bulk()

    def copy_site_data(self, odm_site: ODMSite, site: Site = None) -> Site:
        if site is None:
            site: Site = Site()
            site.odm_site_id = odm_site.site_id
        site.site_code = odm_site.site_code
        site.site_name = odm_site.site_name
        site.elevation_m = odm_site.elevation_m
        site.latitude = odm_site.latitude
        site.longitude = odm_site.longitude
        site.vertical_datum = odm_site.vertical_datum
        site.state = odm_site.state
        site.county = odm_site.county
        site.site_type = odm_site.site_type
        site.watershed = self.watershed
        site.active = True
        return site

    def copy_series_data(self, site: Site, odm_series: ODMSeries, series: Series = None):
        if series is None:
            series: Series = Series()
            series.odm_series_id = odm_series.pk
        series.site_id = site.pk
        series.variable_code = odm_series.variable_code
        series.variable_name = odm_series.variable_name
        series.unit_name = odm_series.unit_name
        series.unit_abbreviation = self.units[odm_series.unit_id].unit_abbreviation
        series.sampled_medium = odm_series.sampled_medium
        series.identifier = f'{site.site_code}_{odm_series.variable_code}_' \
                            f'{odm_series.quality_control_level_id}_{odm_series.source_id}_{odm_series.method_id}'
        return series

    def sync_sites_list(self) -> None:
        odm_site: ODMSite
        odm_sites = ODMSite.objects.prefetch_related('odm_series').all()
        existing_sites = Site.objects.prefetch_related('series').all()

        for odm_site in odm_sites:
            existing_site = existing_sites.filter(site_code=odm_site.site_code).first()
            site = self.copy_site_data(odm_site, existing_site)
            site.save()

            for odm_series in odm_site.odm_series.all():
                if not is_raw_quality(odm_series.quality_control_level_code):
                    continue
                existing_series = site.series.filter(odm_series_id=odm_series.series_id).first()
                self.copy_series_data(site, odm_series, existing_series).save()

    def sync_individual_site(self, site: Site) -> None:
        odm_site: ODMSite = ODMSite.objects.prefetch_related('odm_series').filter(pk=site.odm_site_id).first()
        if not odm_site:
            return

        self.copy_site_data(odm_site, site).save()
        for odm_series in odm_site.odm_series.all():
            if not is_raw_quality(odm_series.quality_control_level_code):
                continue
            existing_series = site.series.filter(odm_series_id=odm_series.series_id).first()
            self.copy_series_data(site, odm_series, existing_series).save()


def is_raw_quality(quality_code: str) -> bool:
    return quality_code == '0'
