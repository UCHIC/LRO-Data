from PIL import Image
from django.conf import settings
from django.db import models


class Site(models.Model):
    odm_site_id = models.IntegerField()
    site_code = models.CharField(max_length=50, primary_key=True)
    site_name = models.CharField(max_length=255)
    elevation_m = models.FloatField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    vertical_datum = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255)
    county = models.CharField(max_length=255)
    watershed = models.CharField(max_length=255)
    site_type = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    raw_data_download_link = models.CharField(max_length=512, blank=True, null=True)
    controlled_data_download_link = models.CharField(max_length=512, blank=True, null=True)

    @property
    def safe_name(self):
        name = "".join([c for c in self.site_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        return f'{name}'

    def __str__(self) -> str:
        return f'{self.site_name}'

    def __repr__(self) -> str:
        return f'({self.site_code}, {self.site_name})'


class Series(models.Model):
    odm_series_id = models.IntegerField()  # DEPRECATED in favor of `odm_series_key`
    odm_series_key = models.CharField(max_length=50, default='')
    site = models.ForeignKey('Site', related_name='series', on_delete=models.CASCADE)
    variable_code = models.CharField(max_length=50)
    variable_name = models.CharField(max_length=255)
    unit_name = models.CharField(max_length=255)
    unit_abbreviation = models.CharField(max_length=255)
    sampled_medium = models.CharField(max_length=255)
    identifier = models.CharField(max_length=50, default='')
    active = models.BooleanField(default=True)

    @property
    def influx_values_url(self) -> str:
        return settings.GET_VALUES_SERVICE.format(series_identifier=self.identifier)

    def __str__(self) -> str:
        return f'{self.variable_code}'

    def __repr__(self) -> str:
        return f'({self.id}, {self.variable_code}, {self.unit_name}, {self.sampled_medium})'


def site_directory_path(instance, filename):
    return f'{instance.site.safe_name}/{instance.site.safe_name}_{filename}'


class SitePhoto(models.Model):
    PHOTO_MAX_SIZE = 720
    site = models.ForeignKey('Site', related_name='photos', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=site_directory_path)

    def save(self, *args, **kwargs):
        super(SitePhoto, self).save(*args, **kwargs)
        uploaded_image = Image.open(self.photo.path)
        image_size = self.get_new_size(self.photo)
        uploaded_image = uploaded_image.resize(image_size, Image.ANTIALIAS)
        uploaded_image.save(self.photo.path, optimize=True, quality=70)

    def get_new_size(self, image):
        is_landscape = image.width > image.height
        width = int(round(self.PHOTO_MAX_SIZE if is_landscape else (float(image.width) / image.height) * self.PHOTO_MAX_SIZE))
        height = int(round(self.PHOTO_MAX_SIZE if not is_landscape else (float(image.height) / image.width) * self.PHOTO_MAX_SIZE))
        return width, height

    def __str__(self) -> str:
        return f'{self.photo.name} - {self.site}'

    def __repr__(self) -> str:
        return f'({self.id}, {self.photo.name}, {self.site})'
