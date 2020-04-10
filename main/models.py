from django.db import models
from django.db.models.signals import pre_save
from django.core.files.base import ContentFile
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, BaseUserManager

import logging
from io import BytesIO

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


