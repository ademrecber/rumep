from django.db import migrations, models
import random

def generate_codes(apps, schema_editor):
    Topic = apps.get_model('main', 'Topic')
    Entry = apps.get_model('main', 'Entry')
    
    # Generate codes for existing topics
    used_codes = set()
    for topic in Topic.objects.all():
        while True:
            code = str(random.randint(100000000, 999999999))
            if code not in used_codes:
                topic.code = code
                used_codes.add(code)
                topic.save()
                break
    
    # Generate codes for existing entries
    for entry in Entry.objects.all():
        while True:
            code = str(random.randint(100000000, 999999999))
            if code not in used_codes:
                entry.code = code
                used_codes.add(code)
                entry.save()
                break

def reverse_codes(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_alter_topic_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='code',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='topic',
            name='code',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.RunPython(generate_codes, reverse_codes),
        migrations.AlterField(
            model_name='entry',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]