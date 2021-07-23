import logging

from django.core.management import BaseCommand

from odm.helpers import InfluxDataHelper
from odm.models import ODMSite

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help: str = 'Deletes all influxdb data'

    def handle(self, *args: str, **options: str):
        sites = ODMSite.objects.prefetch_related('odm_series').all()
        print(f'- about to delete all series data for all {sites.count()} sites in the ODM database')

        for site in sites:
            print(f'-- deleting {site.odm_series.count()} series\' influx data for site {site.site_code}')
            helper: InfluxDataHelper = InfluxDataHelper()
            series_responses = helper.delete_site_data(site)
            for series_identifier, delete_response in series_responses.items():
                if delete_response.status_code == 200:
                    print(f'-- successful request to delete series {series_identifier}.')
                else:
                    print(f'** series {series_identifier} was not deleted.')
