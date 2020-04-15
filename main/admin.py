from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum
from django.urls import path
from django.template.response import TemplateResponse
from django import forms
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string


from .models import (Product, 
                    ProductImage,
                    ProductTag,
                    User,
                    BasketLine,
                    Basket,
                    OrderLine,
                    Order,
                    Address)

import tempfile
from weasyprint import HTML
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "address1", "address2", "city", "country")
    readonly_fields = ("user", )

def make_active(self, request, queryset):
    queryset.update(active=True)
make_active.short_description = "Mark selected items as active"

def make_inactive(self, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = (
    "Mark selected items as inactive"
)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'in_stock', 'price')
    list_filter = ('active', 'in_stock', 'date_updated')
    list_editable = ('in_stock',)
    search_fields = ('name',)
    prepopulated_fields = {'slug':('name',)}
    autocomplete_fields = ('tags',)
    actions = [make_active, make_inactive]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ['slug', 'name']

    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}

class DispatchersProductAdmin(ProductAdmin):
    readonly_fields = ("description", "price", "tags", "active")
    prepopulated_fields = {}
    autocomplete_fields = ()

class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug':('name',)}

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ['slug', 'name']

    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag', 'product_name')
    readonly_fields = ('thumbnail',)
    search_fields = ('product__name',)
    
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(f"<img src='{obj.thumbnail.url}'/>")
        return '-'
    
    thumbnail_tag.short_description = "Thumbnail"

    def product_name(self, obj):
        return obj.product.name

class BasketLineInline(admin.TabularInline):
    model = BasketLine
    raw_id_fields = ("product",)

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id","user","status","count")
    list_editable = ('status',)
    list_filter = ('status',)
    inlines = (BasketLineInline,)

class OrderLineInline(admin.TabularInline):
    model = OrderLine
    raw_id_fields = ("product",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","user","status")
    list_editable = ('status',)
    list_filter = ('status',"shipping_country", "date_added")
    inlines = (OrderLineInline,)

    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_zipcode",
                    "billing_city",
                    "billing_country",
                )
            },
        ),
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zipcode",
                    "shipping_city",
                    "shipping_country",
                )
            },
        ),
    )

class CentralOfficeOrderLineInLine(admin.TabularInline):
    model = OrderLine
    readonly_fields = ("product",)

class CentralOfficeOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    readonly_fields = ("user",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInLine,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing Info",
            {
                "fields": 
                (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_zipcode",
                    "billing_city",
                    "billing_country"
                )
            }
        ),
        (
            "Shipping Info",
            {
                "fields":
                (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zipcode",
                    "shipping_city",
                    "shipping_country"
                )
            }
        )
    )
    

class DispatchersOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "shipping_name", "date_added", "status",)
    list_filter = ("status", "shipping_country", "date_added",)
    inlines = (CentralOfficeOrderLineInLine,)
    fieldsets = (
                (
                    "Shipping Info",
                    {
                        "fields":
                        (
                            "shipping_name",
                            "shipping_address1",
                            "shipping_address2",
                            "shipping_zipcode",
                            "shipping_city",
                            "shipping_country"
                        )
                    },
                ),
            )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status = Order.PAID)

"""The class below will pass to the Django Admin templates a couple
    of extra values that represent colors of headings"""
class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context["site_header_color"] = getattr(self, "site_header_color", None)
        context["module_caption_color"] = getattr(self, "module_caption_color", None)

        return context

class PeriodSelectForm(forms.Form):
    PERIODS = ((30, "30 days"), (60, "60 days"), (90, "90 days"))
    period = forms.TypedChoiceField(choices=PERIODS, coerce=int, required=True)

class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
                        path("orders_per_day/", self.admin_view(self.orders_per_day)),
                        path("most_bought_products/", self.admin_view(self.most_bought_products), name="most_bought_products"),
                    ]

        return extra_urls + urls

    """Creates a temporary/annotated day field, populating it
        with data based on the date_added field
        • Uses the new day field as a unit for aggregation
        • Counts orders for specific days
        The query includes two annotate() calls. The first acts on all
        rows in the order table. The second, instead of acting on all rows, acts on
        the result of the GROUP BY clause, which is generated by the values() call.
        
        SELECT DATE_TRUNC('day', "main_order"."date_added" AT TIME ZONE
        'UTC') AS "day",
            COUNT("main_order"."id") AS "c" FROM "main_order"
             WHERE "main_order"."date_added" > 2018-01-16
        19:20:01.262472+00:00
            GROUP BY DATE_TRUNC('day', "main_order"."date_added" AT
        TIME ZONE 'UTC')"""
    def orders_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)
        order_data = (Order.objects.filter(date_added__gt=starting_day).annotate(day=TruncDay("date_added")).values("day").annotate(c=Count("id")))

        labels = [x["day"].strftime("%Y-%m-%d") for x in order_data]
        values = [x["c"] for x in order_data]
        context = dict(self.each_context(request), title="Orders per day", labels=labels, values=values,)
        
        return TemplateResponse(request, "orders_per_day.html", context)

    def most_bought_products(self, request):
        if request.method == "POST":
            form = PeriodSelectForm(request.POST)
            if form.is_valid():
                days = form.cleaned_data["period"]
                starting_day = datetime.now() - timedelta(days=days)

            data = (
                 OrderLine.objects.filter(
                     order__date_added__gt=starting_day
                 )
                 .values("product__name")
                 .annotate(c=Count("id"))
             )
            logger.info(
                "most_bought_products query: %s", data.query
            )
            labels = [x["product__name"] for x in data]
            values = [x["c"] for x in data]
        else:
            form = PeriodSelectForm()
            labels = None
            values = None
        context = dict(
            self.each_context(request),
            title="Most bought products",
            form=form,
            labels=labels,
            values=values,
        )
        return TemplateResponse(
            request, "most_bought_products.html", context
        )
    
    def index(self, request, extra_context=None):
        reporting_pages = [
            {
                "name": "Orders per day",
                "link": "orders_per_day/",
            },
            {
                "name": "Most bought products",
                "link": "most_bought_products/"
            }
        ]
        if not extra_context:
            extra_context = {}
        extra_context = {"reporting_pages": reporting_pages}
        return super().index(request, extra_context)



class DispatchersAdminSite(ColoredAdminSite):
    site_header = "BookTime central dispatch administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"
    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_dispatcher
        )

class InvoiceMixin:
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "invoice/<int:order_id>/",
                self.admin_view(self.invoice_for_order),
                name="invoice",
            )
        ]
        return my_urls + urls

    def invoice_for_order(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)

        if request.GET.get("format") == "pdf":
            html_string = render_to_string(
                "invoice.html", {"order": order}
            )
            html = HTML(
                string=html_string,
                base_url=request.build_absolute_uri(),
            )

            result = html.write_pdf()

            response = HttpResponse(
                content_type="application/pdf"
            )
            response[
                "Content-Disposition"
            ] = "inline; filename=invoice.pdf"
            response["Content-Transfer-Encoding"] = "binary"
            with tempfile.NamedTemporaryFile(
                delete=True
            ) as output:
                output.write(result)
                output.flush()
                output = open(output.name, "rb")
                binary_pdf = output.read()
                response.write(binary_pdf)

            return response

        return render(request, "invoice.html", {"order": order})

class OwnersAdminSite(InvoiceMixin, ReportingColoredAdminSite):
    site_header = "BookTime owners administration"
    site_header_color = "black"
    module_caption_color = "grey"
    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_superuser
        )

class CentralOfficeAdminSite(InvoiceMixin, ReportingColoredAdminSite):
    site_header = "BookTime central office administration"
    site_header_color = "purple"
    module_caption_color = "pink"
    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_employee
        )

    
main_admin = OwnersAdminSite()

main_admin.register(Product, ProductAdmin)
main_admin.register(ProductTag, ProductTagAdmin)
main_admin.register(ProductImage, ProductImageAdmin)
main_admin.register(User, UserAdmin)
main_admin.register(Address, AddressAdmin)
main_admin.register(Basket, BasketAdmin)
main_admin.register(Order, OrderAdmin)

central_office_admin = CentralOfficeAdminSite(
    "central-office-admin"
)
central_office_admin.register(Product, ProductAdmin)
central_office_admin.register(ProductTag,
ProductTagAdmin)
central_office_admin.register(
    ProductImage, ProductImageAdmin
)
central_office_admin.register(Address, AddressAdmin)
central_office_admin.register(
    Order, CentralOfficeOrderAdmin
)

dispatchers_admin = DispatchersAdminSite("dispatchers-admin")
dispatchers_admin.register(
    Product, DispatchersProductAdmin
)
dispatchers_admin.register(ProductTag, ProductTagAdmin)
dispatchers_admin.register(Order, DispatchersOrderAdmin)