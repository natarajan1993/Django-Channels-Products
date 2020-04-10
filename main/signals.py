# from django.db.models.signals import pre_save
# from django.core.files.base import ContentFile
# from django.dispatch import receiver

# import logging
# from io import BytesIO

# from PIL import Image

# from .models import ProductImage

# logger = logging.getLogger(__name__)

# THUMBNAIL_SIZE = (300,300)

# @receiver(pre_save,sender=ProductImage)
# def generate_thumbnail(sender, instance, **kwargs):
#     logger.info(f"Generating thumbnail for image {instance.product.id}")
    

#     image = Image.open(instance.image)
#     image = image.convert("RGB")
#     image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

#     temp_thumb = BytesIO()
#     image.save(temp_thumb,'JPEG')
#     temp_thumb.seek(0) 

#     instance.thumbnail.save(instance.image.name,ContentFile(temp_thumb.read()), save=False,)
#     temp_thumb.close()