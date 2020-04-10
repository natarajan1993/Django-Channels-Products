from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.core.files.images import ImageFile
from main.models import Product, ProductTag, ProductImage

from collections import Counter
import csv
import os

class Command(BaseCommand): # Command is a reserved name (it has to be named 'Command')
    help = 'Import Products into the database'

    def add_arguments(self, parser):
        """add_arguments() is a default method we are overloading that inherits from the argparse package
        The extra arguments we add to the cmdline command are the path to the import csv and the images base directory"""
        parser.add_argument("csvfile", type = open)
        parser.add_argument("image_basedir", type = str)

    def handle(self, *args, **options): # overlaod the handle method in BaseCommand
        self.stdout.write("Importing Products...")

        counter = Counter()

        reader = csv.DictReader(options.pop("csvfile"))

        for row in reader:
            product, created = Product.objects.get_or_create(name=row['name'], price=row['price']) 
            product.description = row["description"]
            product.slug = slugify(row["name"])

            for book_tag in row["tags"].split("|"):
                tag, tag_created =  ProductTag.objects.get_or_create(name=book_tag)

                product.tags.add(tag)

                counter["tags"] += 1

                if tag_created:
                    counter["tags_created"] += 1 
            
            with open(os.path.join(options['image_basedir'],row['image_filename']), "rb") as f:
                image = ProductImage(product = product,image = ImageFile(f,name=row['image_filename']))
                image.save()

                counter["images"] += 1
            
            product.save()
            counter["products"] += 1

            if created:
                counter["products_created"] += 1
            
            self.stdout.write(f"Products processed = {counter['products']} (created={counter['products_created']})")
            self.stdout.write(f"Tags processed = {counter['tags']} (created={counter['tags_created']})")
            self.stdout.write(f"Images processed = {counter['images']}")




