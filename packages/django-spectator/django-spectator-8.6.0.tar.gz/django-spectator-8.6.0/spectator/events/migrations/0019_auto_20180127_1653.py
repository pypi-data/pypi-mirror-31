# Generated by Django 2.0 on 2018-01-27 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spectator_events', '0018_remove_old_movie_play_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classicalworkselection',
            old_name='classical_work',
            new_name='work',
        ),
        migrations.RenameField(
            model_name='dancepieceselection',
            old_name='dance_piece',
            new_name='work',
        ),
        migrations.RenameField(
            model_name='movieselection',
            old_name='movie',
            new_name='work',
        ),
        migrations.RenameField(
            model_name='playselection',
            old_name='play',
            new_name='work',
        ),
    ]
