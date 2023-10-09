import csv

from django.core.management import BaseCommand

from api_yamdb.settings import BASE_DIR
from reviews.models import (
    Category,
    Genre,
    Title,
    User,
    Comment,
    Review,
)

MODELS_DATA_FILES = {
    Genre: 'genre.csv',
    Category: 'category.csv',
    Title: 'titles.csv',
    User: 'users.csv',
    Title.genre.through: 'genre_title.csv',
    Comment: 'comments.csv',
    Review: 'review.csv',
}

CSV_FILES_DIR = f'{BASE_DIR}/static/data/'


class Command(BaseCommand):

    def handle(self, *args, **options):
        for model, csv_file in MODELS_DATA_FILES.items():
            for row in csv.DictReader(open(
                    str(CSV_FILES_DIR) + csv_file,
                    'r', encoding='utf-8',
                    newline='')
            ):
                records = []
                records.append(model(**row))
            model.objects.bulk_create(records)
            self.stdout.write("Данные загружены")
