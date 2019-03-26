from typing import Dict, List

import requests
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from django.core.management import BaseCommand
from django.conf import settings

from river_data.models import Site, Series


class Command(BaseCommand):
    help: str = 'Retrieves the Logan River sites metadata and updates the database with the data retrieved.'
    ns: Dict[str, str] = {'cuahsi': 'http://www.cuahsi.org/waterML/1.1/'}
    watershed: str = 'Logan River'
    batch_size: int = 100

    def parse_site_xml(self, site_element: Element) -> Site:
        site_info: Element = site_element.find('.//cuahsi:siteInfo', self.ns)
        return Site(
            site_code=site_info.find('.//cuahsi:siteCode', self.ns).text,
            site_name=site_info.find('.//cuahsi:siteName', self.ns).text,
            elevation_m=float(site_info.find('.//cuahsi:elevation_m', self.ns).text),
            latitude=float(site_info.find('.//cuahsi:geoLocation//cuahsi:geogLocation//cuahsi:latitude', self.ns).text),
            longitude=float(site_info.find('.//cuahsi:geoLocation//cuahsi:geogLocation//cuahsi:longitude', self.ns).text),
            vertical_datum=site_info.find('.//cuahsi:verticalDatum', self.ns).text,
            state=site_info.find('.//cuahsi:siteProperty[@name="State"]', self.ns).text,
            county=site_info.find('.//cuahsi:siteProperty[@name="County"]', self.ns).text,
            site_type=site_info.find('.//cuahsi:siteProperty[@name="Site Type"]', self.ns).text,
            watershed=self.watershed,
            active=True
        )

    def parse_series_xml(self, series_element: Element) -> List[Series]:
        series_xml: Element
        series: List[Series] = []
        site_code: str = series_element.find('.//cuahsi:site//cuahsi:siteInfo//cuahsi:siteCode', self.ns).text
        for series_xml in series_element.findall('.//cuahsi:site//cuahsi:seriesCatalog//cuahsi:series', self.ns):
            qc_id: str = series_xml.find('.//cuahsi:qualityControlLevel', self.ns).attrib['qualityControlLevelID']
            if not is_raw_quality(qc_id):
                continue

            source_id: str = series_xml.find('.//cuahsi:source', self.ns).attrib['sourceID']
            method_id: str = series_xml.find('.//cuahsi:method', self.ns).attrib['methodID']
            variable_code: str = series_xml.find('.//cuahsi:variable//cuahsi:variableCode', self.ns).text
            series.append(Series(
                variable_code=variable_code,
                variable_name=series_xml.find('.//cuahsi:variable//cuahsi:variableName', self.ns).text,
                unit_name=series_xml.find('.//cuahsi:variable//cuahsi:unit//cuahsi:unitName', self.ns).text,
                unit_abbreviation=series_xml.find('.//cuahsi:variable//cuahsi:unit//cuahsi:unitAbbreviation', self.ns).text,
                sampled_medium=series_xml.find('.//cuahsi:variable//cuahsi:sampleMedium', self.ns).text,
                identifier=f'{site_code}_{variable_code}_{qc_id}_{source_id}_{method_id}',
                site_id=site_code
            ))
        return series

    def get_sites(self) -> Element:
        response: requests.Response = requests.get(settings.GET_SITES_SERVICE)
        return ElementTree.fromstring(response.text)

    def get_site_variables(self, site_code: str) -> Element:
        response: requests.Response = requests.get(settings.GET_SITE_INFO_SERVICE.format(site_code=site_code))
        return ElementTree.fromstring(response.text)

    def handle(self, *args: str, **options: str) -> None:
        sites: List[Site] = []
        series: List[Series] = []

        site_xml: Element
        sites_xml: Element = self.get_sites()

        print('- getting site and series data')
        for site_xml in sites_xml.findall('cuahsi:site', self.ns):
            site: Site = self.parse_site_xml(site_xml)
            sites.append(site)

            series_xml: Element = self.get_site_variables(site.site_code)
            series.extend(self.parse_series_xml(series_xml))

        print(f'- inserting {len(sites)} sites with a total of {len(series)} series.')
        Site.objects.bulk_create(sites, batch_size=self.batch_size)
        Series.objects.bulk_create(series, batch_size=self.batch_size)
        print('- done!')


def is_raw_quality(quality_code: str) -> bool:
    return quality_code == '0'