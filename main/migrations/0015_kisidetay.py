# Generated by Django 5.1.7 on 2025-06-27 21:41

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_aiproviderconfig_provider'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KisiDetay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detay', models.TextField(max_length=20000, validators=[django.core.validators.MinLengthValidator(10)])),
                ('eklenme_tarihi', models.DateTimeField(auto_now_add=True)),
                ('kisi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detaylar', to='main.kisi')),
                ('kullanici', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Kişi Detay',
                'verbose_name_plural': 'Kişi Detayları',
                'ordering': ['-eklenme_tarihi'],
            },
        ),
    ]
