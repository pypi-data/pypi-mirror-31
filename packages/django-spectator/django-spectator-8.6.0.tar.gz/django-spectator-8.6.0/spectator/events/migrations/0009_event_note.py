# Generated by Django 2.0 on 2018-01-18 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spectator_events', '0008_venue_slug_20180102_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='note',
            field=models.TextField(blank=True, help_text='Optional. Paragraphs will be surrounded with <p></p> tags. HTML allowed.'),
        ),
    ]
