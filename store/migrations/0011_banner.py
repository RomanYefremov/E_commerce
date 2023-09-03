# Generated by Django 4.2.3 on 2023-08-30 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_review_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='banners/')),
                ('alt_text', models.CharField(help_text='Alt text for the image', max_length=200)),
            ],
        ),
    ]
