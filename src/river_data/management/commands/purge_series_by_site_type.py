from typing import Dict, List

from django.core.management import BaseCommand

from river_data.models import Site


class Command(BaseCommand):
    help: str = 'Sets the download links for raw and controlled data.'

    def handle(self, *args: str, **options: str) -> None:
        site: Site
        sites = Site.objects.prefetch_related('series').all()

        print(f'updating series for {sites.count()} sites.')
        for site in sites:
            allowed_series: List[str] = site_variables[site_type_map[site.site_type]]
            if site.site_code == 'LR_Wilkins_R':
                allowed_series: List[str] = site_variables['wilkins_repeater']
            allowed_count: int = site.series.filter(variable_code__in=allowed_series).update(active=True)
            filtered_count: int = site.series.exclude(variable_code__in=allowed_series).update(active=False)
            print(f'- site {site.site_code} allowed {allowed_count} series and filtered out {filtered_count} series.')


site_type_map: Dict[str, str] = {
    'Land': 'climate',
    'Atmosphere': 'climate',
    'Stream': 'aquatic',
    'Storm sewer': 'storm_drain'
}

site_variables: Dict[str, List[str]] = {
    'climate': ['AirTemp_ST110_Avg', 'BP_Avg', 'RH', 'VaporPress_Avg', 'WindSp_Avg',
                'WindDir_Avg', 'JuddDepth_Avg', 'Precip_Tot_Avg', 'PARIn_Avg', 'PAROut_Avg',
                'SWOut_NR01_Avg', 'SWIn_NR01_Avg', 'NetRad_NR01_Avg', 'LWOut_Cor_NR01_Avg', 'LWIn_Cor_NR01_Avg',
                'Evapotrans_ETo', 'Evapotrans_ETr', 'VWC_5cm_Avg', 'SoilTemp_5cm_Avg', 'Permittivity_5cm_Avg',
                'VWC_10cm_Avg', 'SoilTemp_10cm_Avg', 'Permittivity_10cm_Avg', 'VWC_20cm_Avg', 'SoilTemp_20cm_Avg',
                'Permittivity_20cm_Avg', 'VWC_50cm_Avg', 'SoilTemp_50cm_Avg', 'Permittivity_50cm_Avg',
                'VWC_100cm_Avg', 'SoilTemp_100cm_Avg', 'Permittivity_100cm_Avg'],
    'aquatic': ['WaterTemp_EXO', 'SpCond', 'pH', 'ODO', 'ODO_Local', 'TurbMed', 'BGA',
                'Chlorophyll', 'fDOM', 'Stage', 'Nitrate-N'],
    'storm_drain': ['Level_ISCO', 'Velocity_ISCO', 'Flow_ISCO', 'Volume_ISCO', 'WaterTemp_ISCO'],
    'wilkins_repeater': ['AirTemp_HMP50_Avg', 'RH_HMP51', 'WindSp_S_WVT', 'WindDir_D1_WVT'],
}
