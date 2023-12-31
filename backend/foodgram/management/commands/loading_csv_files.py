import csv
import os

from backend_foodgram import settings
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient

CSV_PATH = os.path.join(settings.BASE_DIR, 'ingredients.csv')


class Command(BaseCommand):
    help = ('Загружает данные в БД из csv-файлов.')

    def handle(self, *args, **options):
        with open(CSV_PATH, 'r', newline='') as file_name:
            print(file_name)
            reader = csv.DictReader(file_name)
            data = []
            for row in reader:
                ingredient = Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                data.append(ingredient)
        Ingredient.objects.bulk_create(data)
