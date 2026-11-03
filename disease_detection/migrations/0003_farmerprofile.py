from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('disease_detection', '0002_remove_persisted_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='FarmerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_number', models.CharField(blank=True, max_length=15)),
                ('district', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(default='Tamil Nadu', max_length=100)),
                ('language', models.CharField(default='English', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='farmer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
