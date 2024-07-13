from django import forms
from django.contrib.auth.models import Group

from .models import Order, Product
from django.utils.translation import gettext_lazy


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = True

    class Meta:
        model = Product
        fields = [
            "name",
            "price",
            "description",
            "discount",
            "quantity",
            "preview",
        ]

    price = forms.IntegerField(label=gettext_lazy("Цена"), min_value=0, max_value=100000, step_size=1000)

    discount = forms.IntegerField(
        label=gettext_lazy("Процент скидки"), min_value=0, max_value=150, step_size=10
    )
    images = MultipleFileField(label=gettext_lazy("Список изображений"), required=False)


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["delivery_address"].required = True

    class Meta:
        model = Order
        fields = [
            "delivery_address",
            "promocode",
            "user",
            "products",
        ]


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = [
            "name",
        ]


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
