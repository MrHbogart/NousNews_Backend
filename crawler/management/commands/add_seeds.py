from django.core.management.base import BaseCommand

from crawler.models import CrawlSeed
from crawler.services import get_config


SEED_URLS = [
    "https://www.fxstreet.com/news/",
    "https://www.reuters.com/world/",
    "https://www.reuters.com/markets/",
    "https://www.investing.com/news/",
    "https://www.marketwatch.com/latest-news",
    "https://finance.yahoo.com/news",
    "https://www.bloomberg.com/markets",
    "https://www.businessinsider.com/markets",
    "https://www.forexfactory.com/news",
    "https://www.isna.ir/service/Economy",
    "https://www.isna.ir/service/Politics",
    "https://www.mehrnews.com/service/economy",
    "https://www.mehrnews.com/service/politics",
    "https://www.donya-e-eqtesad.com/news",
    "https://www.eghtesadonline.com",
    "https://www.economic24.ir",
    "https://www.tabnak.ir/fa/economic",
    "https://www.entekhab.ir",
    "https://www.tasnimnews.com/fa/economy",
]


class Command(BaseCommand):
    help = "Add default crawl seed URLs."

    def handle(self, *args, **options):
        config = get_config()
        created = 0
        updated = 0
        for url in SEED_URLS:
            seed, was_created = CrawlSeed.objects.get_or_create(
                url=url,
                defaults={"config": config},
            )
            if was_created:
                created += 1
            else:
                updated += 1
                if seed.config_id is None:
                    seed.config = config
            if not seed.is_active:
                seed.is_active = True
            if seed.is_active and seed.config_id:
                seed.save(update_fields=["is_active", "config"])
            elif seed.is_active:
                seed.save(update_fields=["is_active"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeds added. created={created} existing={updated}"
            )
        )
