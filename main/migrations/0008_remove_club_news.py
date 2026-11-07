from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('main', '0007_club_news')]
    operations = [
        migrations.DeleteModel(name='ClubNews'),
        migrations.DeleteModel(name='ClubNewsSync'),
    ]
