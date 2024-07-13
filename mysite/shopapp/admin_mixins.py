import csv

from django.core import serializers
from django.db.models import QuerySet
from django.db.models.options import Options
from django.http import HttpRequest, HttpResponse
from django.utils.html import format_html

from .models import Order, Product


class ExportAsCSVFile:
    def export_as_csv(self, request: HttpRequest, queryset: QuerySet):
        meta: Options = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}-export.csv'

        writer = csv.writer(response)
        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export to CSV file"


class ExportAsJSONFile:
    def export_as_json(self, request: HttpRequest, queryset: QuerySet):
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename={self.model.__name__}-export.json'

        response.write(serializers.serialize('json', queryset))

        return response

    export_as_json.short_description = "Export to JSON file"


class ColoredText:
    def product_colored_id(self, obj: Product):
        if obj.archived is True:
            return format_html(
                '<span style="color: #800000;">{}</span>',
                obj.id,
            )
        return format_html(
            '<span style="color: #FF0000;">{}</span>',
            obj.id,
        )

    def order_colored_id(self, obj: Order):
        return format_html(
            '<span style="color: #FF0000;">{}</span>',
            obj.id,
        )

    def colored_price(self, obj: Product):
        if obj.archived is True:
            return format_html(
                '<span style="color: #800000; font-weight: 450;">{}</span>',
                obj.price,
            )
        return format_html(
            '<span style="color: #00FF00; font-weight: 450;">{}</span>',
            obj.price,
        )

    def colored_name(self, obj: Product):
        if obj.archived is True:
            return format_html(
                '<span style="color: #800080; font-weight: 500;">{}</span>',
                obj.name,
            )
        return format_html(
            '<span style="color: #FF00FF; font-weight: 500;">{}</span>',
            obj.name,
        )

    def colored_delivery_address(self, obj: Order):
        return format_html(
            '<span style="color: #FFFF00;">{}</span>',
            obj.delivery_address,
        )

    def colored_short_description(self, obj: Product):
        if len(obj.description) > 50:
            obj.description = obj.description[:50] + "..."

        if obj.archived is True:
            return format_html(
                '<span style="color: #808080;">{}</span>',
                obj.description,
            )
        return format_html(
            '<span style="color: #FFFFFF;">{}</span>',
            obj.description,
        )

    product_colored_id.short_description = "id"
    order_colored_id.short_description = "id"
    colored_price.short_description = "price"
    colored_name.short_description = "name"
    colored_delivery_address.short_description = "delivery_address"
    colored_short_description.short_description = "description"
