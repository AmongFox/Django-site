from django.contrib.sitemaps import Sitemap

from .models import Product


class ShopSiteMap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Product.objects.all().order_by("-created_at")

    def lastmod(self, obj: Product):
        return obj.created_at

