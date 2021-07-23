from django.db import models


# Create your models here.
class ODMSite(models.Model):
    site_id = models.IntegerField(primary_key=True, db_column='SiteID')
    site_code = models.CharField(max_length=50, db_column='SiteCode')
    site_name = models.CharField(max_length=255, db_column='SiteName')
    elevation_m = models.FloatField(blank=True, null=True, db_column='Elevation_m')
    latitude = models.FloatField(db_column='Latitude')
    longitude = models.FloatField(db_column='Longitude')
    vertical_datum = models.CharField(max_length=255, blank=True, null=True, db_column='VerticalDatum')
    state = models.CharField(max_length=255, db_column='State')
    county = models.CharField(max_length=255, db_column='County')
    watershed = models.CharField(max_length=255, db_column='Comments')
    site_type = models.CharField(max_length=255, db_column='SiteType')

    class Meta:
        db_table = 'Sites'
        managed = False


class ODMSeries(models.Model):
    series_id = models.IntegerField(primary_key=True, db_column='SeriesID')
    site_id = models.ForeignKey('ODMSite', related_name='odm_series', on_delete=models.CASCADE, db_column='SiteID')
    site_code = models.CharField(max_length=50, db_column='SiteCode')

    variable_id = models.IntegerField(db_column='VariableID')
    variable_code = models.CharField(max_length=50, db_column='VariableCode')
    variable_name = models.CharField(max_length=255, db_column='VariableName')

    unit_id = models.IntegerField(db_column='VariableUnitsID')
    unit_name = models.CharField(max_length=255, db_column='VariableUnitsName')

    sampled_medium = models.CharField(max_length=255, db_column='SampleMedium')

    quality_control_level_id = models.IntegerField(db_column='QualityControlLevelID')
    quality_control_level_code = models.CharField(max_length=50, db_column='QualityControlLevelCode')
    source_id = models.IntegerField(db_column='SourceID')
    method_id = models.IntegerField(db_column='MethodID')

    class Meta:
        db_table = 'SeriesCatalog'
        managed = False

    @property
    def identifier(self) -> str:
        return f'{self.site_code}_{self.variable_code}_' \
               f'{self.quality_control_level_id}_{self.source_id}_{self.method_id}'


class ODMUnit(models.Model):
    unit_id = models.IntegerField(primary_key=True, db_column='UnitsID')
    unit_abbreviation = models.CharField(max_length=255, db_column='UnitsAbbreviation')

    class Meta:
        db_table = 'Units'
        managed = False
