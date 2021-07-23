import logging

from django.core.management import BaseCommand

from odm.helpers import InfluxDataHelper
from odm.models import ODMSite

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help: str = 'Deletes influxdb data for one or more ODM sites'

    def add_arguments(self, parser):
        parser.add_argument('site_codes', nargs='*', type=str,
                            help='delete all series measurement data for one of more sites on influxdb')

    def handle(self, *args: str, **options: str) -> None:
        individual_sites = options.get('site_codes', [])

        for site_code in individual_sites:
            helper: InfluxDataHelper = InfluxDataHelper()
            site = ODMSite.objects.filter(site_code=f'{site_code}').first()
            if not site:
                logger.warning(f'site {site_code} was not found in the database')
                continue
            series_responses = helper.delete_site_data(site)
            for series_identifier, delete_response in series_responses.items():
                if delete_response.status_code == 200:
                    logger.info(f'-- successful request to delete series {series_identifier}.')
                else:
                    logger.warning(f'** series {series_identifier} was not deleted.')
