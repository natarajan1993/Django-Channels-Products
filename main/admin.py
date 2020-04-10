from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from django.utils.html import format_html

from .models import Product, ProductImage, ProductTag, User

@admin.register(User)

class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ('email','password')}),
        ("Personal Info", {"fields":("first_name", "last_name")}),
        ("Permissions", {"fields":("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields":("last_login", "date_joined")}),
    )

    add_fieldsets = ((None, {"fields": ('email','password'),"classes":("wide",)}))
    
    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'in_stock', 'price')
    list_filter = ('active', 'in_stock', 'date_updated')
    list_editable = ('in_stock',)
    search_fields = ('name',)
    prepopulated_fields = {'slug':('name',)}
    autocomplete_fields = ('tags',)

class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug':('name',)}

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


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ProductTag, ProductTagAdmin)
