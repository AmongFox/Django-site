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


class ProductCreateForm(forms.ModelForm):
    name = forms.CharField(label=gettext_lazy("Название"), max_length=40, required=True)
    price = forms.DecimalField(label=gettext_lazy("Цена"), min_value=0, max_value=100000, step_size=1000)
    description = forms.CharField(label=gettext_lazy("Описание"), widget=forms.Textarea, required=True)
    discount = forms.IntegerField(label=gettext_lazy("Процент скидки"), min_value=0, max_value=100, step_size=10)

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

    def save(self, commit=True):
        product = super(ProductCreateForm, self).save(commit=False)
        product.preview = None
        product.save()
        product.preview = self.cleaned_data["preview"]
        if commit:
            product.save()
        return product


class ProductUpdateForm(ProductCreateForm):
    images = MultipleFileField(label=gettext_lazy("Список изображений"), required=False)


class OrderForm(forms.ModelForm):
    delivery_address = forms.CharField(
        label=gettext_lazy("Адрес доставки"),
        widget=forms.Textarea(attrs={'rows': 8, 'cols': 50}),
        required=True,
    )

    class Meta:
        model = Order
        fields = [
            "delivery_address",
            "promocode",
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
