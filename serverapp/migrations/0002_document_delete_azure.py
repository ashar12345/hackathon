# Generated by Django 4.0.4 on 2022-07-07 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('serverapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(blank=True, upload_to='docs')),
            ],
        ),
        migrations.DeleteModel(
            name='Azure',
        ),
    ]
