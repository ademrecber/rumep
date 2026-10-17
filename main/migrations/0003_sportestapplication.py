from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('main', '0002_wallpaper')]
    operations = [migrations.CreateModel(
        name='SporTestApplication',
        fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('email', models.EmailField(max_length=254, unique=True, verbose_name='Google Play Gmail adresi')),
            ('added_to_test', models.BooleanField(default=False, verbose_name='Teste eklendi')),
            ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Başvuru tarihi')),
        ],
        options={'ordering': ['added_to_test', '-created_at'], 'verbose_name': 'Spor test başvurusu', 'verbose_name_plural': 'Spor test başvuruları'},
    )]
