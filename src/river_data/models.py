from django.db import models


class Site(models.Model):
    site_code = models.CharField(max_length=50, unique=True)
    site_name = models.CharField(max_length=255)
    elevation_m = models.FloatField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    vertical_datum = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255)
    county = models.CharField(max_length=255)
    watershed = models.CharField(max_length=255)
    site_type = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f'{self.site_name}'

    def __repr__(self) -> str:
        return f'({self.id}, {self.site_code}, {self.site_name})'


class Series(models.Model):
    registration = models.ForeignKey('Site', related_name='series', on_delete=models.CASCADE)
    variable_code = models.CharField(max_length=50)
    variable_name = models.CharField(max_length=255)
    unit_name = models.CharField(max_length=255)
    unit_abbreviation = models.CharField(max_length=255)
    sampled_medium = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f'{self.variable_code}'

    def __repr__(self) -> str:
        return f'({self.id}, {self.variable_code}, {self.unit_name}, {self.sampled_medium})'
