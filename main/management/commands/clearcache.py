from django.core.management.base import BaseCommand
from django.core.cache import cache
import os
import shutil
from pathlib import Path

def remove_pycache_dirs(root_dir='.'):
    """Remove all __pycache__ directories recursively"""
    root_path = Path(root_dir)
    
    for pycache_dir in root_path.rglob('__pycache__'):
        if pycache_dir.is_dir():
            print(f"Removing: {pycache_dir}")
            shutil.rmtree(pycache_dir)


class Command(BaseCommand):
    help = 'Clears the cache.'

    def handle(self, *args, **kwargs):
        cache.clear()
        remove_pycache_dirs()
        self.stdout.write(self.style.SUCCESS("✅ Cache cleared successfully."))
