from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_kategori_kisi'),  # Replace with the name of your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='account_status',
            field=models.CharField(
                choices=[('active', 'Active'), ('frozen', 'Frozen'), ('deletion_scheduled', 'Scheduled for Deletion')],
                default='active',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='scheduled_deletion_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
