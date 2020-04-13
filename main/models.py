from django.db import models
from django.db.models.signals import pre_save, post_save
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.signals import user_logged_in

import logging
from io import BytesIO

from .exceptions import BasketException

from PIL import Image

logger = logging.getLogger(__name__)

class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class ProductTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self,email, password, **extra_fields):
        if not email:
            raise ValueError("The email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email, password = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have superuser=True")

        return self._create_user(email, password, **extra_fields)

    
class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

class ProductTag(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length = 48)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    objects = ProductTagManager()

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


    def __str__(self):
        return self.name
    
    def natural_key(self):
        return (self.slug,)

class Product(models.Model):
    name = models.CharField(max_length=32)
    tags = models.ManyToManyField(ProductTag, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    slug = models.SlugField(max_length = 48)
    active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = ActiveManager()
    

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product-images")
    thumbnail = models.ImageField(upload_to="product-thumbnails", null=True)

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return self.product.name

THUMBNAIL_SIZE = (300,300)

@receiver(pre_save,sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info(f"Generating thumbnail for image {instance.product.id}")
    

    image = Image.open(instance.image)
    image = image.convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

    temp_thumb = BytesIO()
    image.save(temp_thumb,'JPEG')
    temp_thumb.seek(0) 

    instance.thumbnail.save(instance.image.name,ContentFile(temp_thumb.read()), save=False,)
    temp_thumb.close()


class Address(models.Model):
    SUPPORTED_COUNTRIES = (
        ("uk", "United Kingdom"), # First value is value stored, 2nd is value displayed
        ("usa", "United States of America")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    address1 = models.CharField("Address Line 1", max_length=60)
    address2 = models.CharField("Address Line 2", max_length=60, blank=True)
    zip_code = models.CharField("Postal/ZIP code", max_length=12)
    city = models.CharField(max_length=60)
    country = models.CharField(max_length=3, choices = SUPPORTED_COUNTRIES)

    def __str__(self):
        return ", ".join([
            self.name,
            self.address1,
            self.address2,
            self.zip_code,
            self.city,
            self.country
        ])
    

class Basket(models.Model):
    OPEN=10
    SUBMITTED=20
    STATUSES = ((OPEN, "Open"),(SUBMITTED,"Submitted"))

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    class Meta:
        verbose_name = "Basket"
        verbose_name_plural = "Baskets"

    def is_empty(self):
        return self.basketline_set.all().count() == 0

    def count(self):
        return sum(i.quantity for i in self.basketline_set.all())

    def __str__(self):
        return self.user.email

    def create_order(self, billing_address, shipping_address):
        if not self.user:
            raise BasketException("Cannot create order without user")

        logger.info(f"Creating order for basket id={self.id},shipping_address_id={shipping_address.id},billing_address_id={billing_address.id}")

        order_data = {
            "user":self.user,
            "billing_name": billing_address.name,
            "billing_address1": billing_address.address1,
            "billing_address2": billing_address.address2,
            "billing_zipcode": billing_address.zip_code,
            "billing_city": billing_address.city,
            "billing_country": billing_address.country,
            "shipping_name": shipping_address.name,
            "shipping_address1": shipping_address.address1,
            "shipping_address2": shipping_address.address2,
            "shipping_zipcode": shipping_address.zip_code,
            "shipping_city": shipping_address.city,
            "shipping_country": shipping_address.country
        }

        order = Order.objects.create(**order_data)
        c = 0
        for line in self.basketline_set.all():
            for _ in range(line.quantity):
                order_line_data = {
                    "order": order,
                    "product": line.product
                }
                order_line = OrderLine.objects.create(**order_line_data)
                c += 1
        logger.info(f"Created order with id={order.id} and lines_count={c}")
        
        self.status = Basket.SUBMITTED
        self.save()
        return order


class BasketLine(models.Model):
    """BasketLine model represents the product+quantity for each basket"""
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])


"""Signal to merge a user's previous basket with their current basket if it exists"""
@receiver(user_logged_in)
def merge_baskets_if_found(sender, user, request, **kwargs):
    anonymous_basket = getattr(request, "basket", None) # Get the basket attrib from the request if it exists or None
    if anonymous_basket:
        try:
            loggedin_basket = Basket.objects.get(user=user, status=Basket.OPEN) # Get user's current logged in basket
            for line in anonymous_basket.basketline_set.all(): # For each item in the anonymous basket add it to the current basket
                line.basket = loggedin_basket
                line.save()

            anonymous_basket.delete()
            request.basket = loggedin_basket # Set the request (session) basket to the logged in basket after adding old items
            logger.info(f"Merged basket to id {loggedin_basket.id}")

        except Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()

            logger.info(f"Assigned user to basket with id {anonymous_basket.id}")

class Order(models.Model):

    NEW = 10
    PAID = 20
    DONE = 30

    STATUSES = ((NEW,"New"),(PAID,"Paid"),(DONE,"Done"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default = NEW)

    billing_name = models.CharField(max_length=60)
    billing_address1 = models.CharField(max_length=60)
    billing_address2 = models.CharField(max_length=60, blank=True)
    billing_zipcode = models.CharField(max_length=12)
    billing_city = models.CharField(max_length=60)
    billing_country = models.CharField(max_length=3)

    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField(max_length=60)
    shipping_address2 = models.CharField(max_length=60, blank=True)
    shipping_zipcode = models.CharField(max_length=12)
    shipping_city = models.CharField(max_length=60)
    shipping_country = models.CharField(max_length=3)

    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"


class OrderLine(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40

    STATUSES = ((NEW,"New"),(PROCESSING,"Processing"),(SENT,"Sent"),(CANCELLED,"Cancelled"))

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lines") # related_name is used to refer to the Order ForeignKey queryset and can be used as order.lines.all() instead of order.orderline_set.all()
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # Protect the corresponding Product if the product instance is deleted in the order
    status = models.IntegerField(choices=STATUSES, default = NEW)


@receiver(post_save, sender=OrderLine)
def orderline_to_order_status(sender, instance, **kwargs):
    """This signal will be executed after saving instances of the OrderLine
        model. The first thing it does is check whether any order lines connected
        to the order have statuses below “sent.” If there is any, the execution is
        terminated. If there is no line below the “sent” status, the whole order is
        marked as “done.”"""
    if not instance.order.lines.filter(status__lt=OrderLine.SENT).exists():
        logger.info(f"All lines for order {instance.order.id} have been processed. Marking as done")
        instance.order.status = Order.DONE
        instance.order.save()