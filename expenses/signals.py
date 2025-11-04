# expenses/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category

# automatically make some default categories after migrations

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name == 'expenses':  # only run for this app
        default_categories = ["Bills", "Shopping", "Food", "Travel", "Entertainment", "Miscellaneous"]
        for name in default_categories:
            Category.objects.get_or_create(name=name)
