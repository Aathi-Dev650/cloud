from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('disease_detection', '0001_initial')]

    operations = [
        migrations.RemoveField(model_name='diseasedetection', name='image'),
        migrations.AddField(model_name='diseasedetection', name='crop', field=models.CharField(default='', max_length=100)),
        migrations.AddField(model_name='diseasedetection', name='status', field=models.CharField(default='', max_length=100)),
        migrations.RemoveField(model_name='diseasedetection', name='remedy'),
    ]
