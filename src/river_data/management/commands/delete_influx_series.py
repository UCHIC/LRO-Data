import logging

from django.core.management import BaseCommand
from odm.helpers import InfluxDataHelper

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help: str = 'Deletes influxdb data for one or more ODM series'

    def add_arguments(self, parser):
        parser.add_argument('series_identifiers', nargs='*', type=str,
                            help='delete series measurement data for one or more series on influxdb')

    def handle(self, *args: str, **options: str):
        individual_series = options.get('series_identifiers', [])

        for series_identifier in individual_series:
            helper: InfluxDataHelper = InfluxDataHelper()
            delete_response = helper.delete_measurement_data(f'{series_identifier}')
            if delete_response.status_code == 200:
                logger.info(f'-- successful request to delete series {series_identifier}.')
            else:
                logger.warning(f'** series {series_identifier} was not deleted.')
