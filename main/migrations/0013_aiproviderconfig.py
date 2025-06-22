from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_profile_preferred_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIProviderConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('deepseek', 'DeepSeek'), ('huggingface', 'Hugging Face'), ('grok', 'Grok')], default='deepseek', max_length=20, unique=True, verbose_name='AI Sağlayıcısı')),
                ('is_active', models.BooleanField(default=False, verbose_name='Aktif')),
                ('api_key', models.CharField(blank=True, max_length=256, null=True, verbose_name='API Anahtarı')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')),
            ],
            options={
                'verbose_name': 'AI Sağlayıcı Konfigürasyonu',
                'verbose_name_plural': 'AI Sağlayıcı Konfigürasyonları',
            },
        ),
    ]
