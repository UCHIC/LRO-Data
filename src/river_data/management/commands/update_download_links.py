from typing import Dict

from django.core.management import BaseCommand

from river_data.models import Site


class Command(BaseCommand):
    help: str = 'Sets the download links for raw and controlled data.'

    def handle(self, *args: str, **options: str) -> None:
        key: str
        item: Dict[str, str]
        for key, item in site_hydroshare_links.items():
            site: Site = Site.objects.filter(site_code=key).first()
            if not site:
                print(f'-- site {key} doesn\'t exist.')
                continue
            site.raw_data_download_link = item.get('raw')
            site.controlled_data_download_link = item.get('controlled')
            site.save()
            print(f'- updated links for site {key}.')


site_hydroshare_links: Dict[str, Dict[str, str]] = {
    "LR_FB_C": {
        "raw": "https://www.hydroshare.org/resource/965dc124cabc4587955e6f1f722fc33b/",
        "controlled": "https://www.hydroshare.org/resource/08b352fb637c41a2971fa6e1daa20ade/"
    },
    "LR_Mendon_AA": {
        "raw": "https://www.hydroshare.org/resource/728566f42906412698b09f6fe2f7cd02/",
        "controlled": "https://www.hydroshare.org/resource/e55012dcffe64aaba9a9b39f0329b101/"
    },
    "LR_WaterLab_AA": {
        "raw": "https://www.hydroshare.org/resource/ecb77926c2484e068f28acda434f8772/",
        "controlled": "https://www.hydroshare.org/resource/1b87fe7452624e82a54fa57432b17583/"
    },
    "LR_GC_C": {
        "raw": "https://www.hydroshare.org/resource/96310f82dd5247ba8201955750093923/",
        "controlled": "https://www.hydroshare.org/resource/86a27290e1b443a488f0b84cb9e2af91/"
    },
    "LR_Wilkins_R": {
        "raw": "https://www.hydroshare.org/resource/b653f3cf03214e52aa765f6cb65fbc22/"
    },
    "LR_TWDEF_C": {
        "raw": "https://www.hydroshare.org/resource/47e6ae5461a7474dbf37abe475a0d6da/",
        "controlled": "https://www.hydroshare.org/resource/200a03e04591410f8b6310b43558634b/"
    },
    "LR_MainStreet_BA": {
        "raw": "https://www.hydroshare.org/resource/23650489df6646edaf412cffa9881279/",
        "controlled": "https://www.hydroshare.org/resource/98788289144a48e4b5151ab87a1f8ad5/"
    },
    "LR_RH_SD": {
        "raw": "https://www.hydroshare.org/resource/29ddd49f7e1149c6b14246eada15713b/"
    },
    "LR_FB_BA": {
        "raw": "https://www.hydroshare.org/resource/8971ca6bab084779913f925e0e485008/",
        "controlled": "https://www.hydroshare.org/resource/1bb3210918414e13b077e87798d4a696/"
    },
    "LR_SC_SD": {
        "raw": "https://www.hydroshare.org/resource/fd7e56d92c06427583cd83eddf4adf42/"
    },
    "BSF_CONF_BA": {
        "raw": "https://www.hydroshare.org/resource/94bcad20fbfb4c44ac7f98a0fdfa5e79/",
        "controlled": "https://www.hydroshare.org/resource/67dc333cb7a9451fab1e926f7bd332bd/"
    },
    "LR_TG_C": {
        "raw": "https://www.hydroshare.org/resource/8db626f2625c4b689638f845b75e8e23/",
        "controlled": "https://www.hydroshare.org/resource/de17599743af4ee7a634eaafd78de8c2/"
    },
    "LR_TG_BA": {
        "raw": "https://www.hydroshare.org/resource/5cc3cf79eab2413fa46da70435a43265/",
        "controlled": "https://www.hydroshare.org/resource/b93121c191a94abbb288acabba07f954/"
    }
}
