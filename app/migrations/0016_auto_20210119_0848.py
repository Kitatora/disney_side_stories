# Generated by Django 2.2 on 2021-01-18 23:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20210119_0845'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='エリア')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='カテゴリ')),
            ],
        ),
        migrations.CreateModel(
            name='Attraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='アトラクション')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Area', verbose_name='エリア')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='area',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Area', verbose_name='エリア'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='attraction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Attraction', verbose_name='アトラクション'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Category', verbose_name='カテゴリ'),
            preserve_default=False,
        ),
    ]
