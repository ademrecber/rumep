import os
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template.loaders.app_directories import get_app_template_dirs
from django.conf import settings
import re

class Command(BaseCommand):
    help = 'Check for unused JavaScript files in the project'

    def handle(self, *args, **options):
        # Get all JS files
        js_files = set()
        js_dir = os.path.join(settings.STATICFILES_DIRS[0], 'main', 'js')
        for root, dirs, files in os.walk(js_dir):
            for file in files:
                if file.endswith('.js'):
                    relative_path = os.path.relpath(os.path.join(root, file), js_dir)
                    js_files.add(relative_path)

        # Get all template files
        template_files = []
        template_dirs = get_app_template_dirs('templates')
        for template_dir in template_dirs:
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        template_files.append(os.path.join(root, file))

        # Check JS usage in templates
        used_js = set()
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for static tag usage
                    matches = re.findall(r"{%\s*static\s*'main/js/([^']+)'\s*%}", content)
                    used_js.update(matches)
                    # Look for direct script src usage
                    matches = re.findall(r'src=[\'"]/static/main/js/([^\'"]+)[\'"]', content)
                    used_js.update(matches)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error reading {template_file}: {e}'))

        # Find unused files
        unused_js = js_files - used_js
        if unused_js:
            self.stdout.write(self.style.WARNING('Unused JavaScript files found:'))
            for js_file in sorted(unused_js):
                self.stdout.write(f'  - {js_file}')
        else:
            self.stdout.write(self.style.SUCCESS('No unused JavaScript files found.'))