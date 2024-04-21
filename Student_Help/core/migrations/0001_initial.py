# Generated by Django 4.2.11 on 2024-04-21 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EvenClub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Evenement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intitule', models.CharField(max_length=255)),
                ('description', models.TextField(default='Non definie')),
                ('lieu', models.CharField(max_length=255)),
                ('contactinfo', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EvenSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prix', models.DecimalField(decimal_places=3, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Poste',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='')),
                ('type', models.IntegerField(choices=[(0, 'Offre'), (1, 'Demande')])),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Recommandation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texte', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('telephone', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('depart', models.CharField(max_length=255)),
                ('destination', models.CharField(max_length=255)),
                ('heuredep', models.TimeField()),
                ('nbrsieges', models.IntegerField()),
                ('contactinfo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.evenement')),
            ],
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typeStg', models.IntegerField(choices=[(1, 'Ouvrier'), (2, 'Technicien'), (3, 'PFE')])),
                ('societe', models.CharField(max_length=100)),
                ('duree', models.IntegerField()),
                ('sujet', models.CharField(max_length=200)),
                ('specialite', models.CharField(max_length=100)),
                ('contactinfo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.evenement')),
            ],
        ),
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commentaire', models.CharField(max_length=255)),
                ('like', models.BooleanField(default=False)),
                ('pst', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.poste')),
                ('usr', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.user')),
            ],
        ),
        migrations.AddField(
            model_name='poste',
            name='usr',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.user'),
        ),
        migrations.CreateModel(
            name='Logement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('localisation', models.CharField(max_length=255)),
                ('contactinfo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.evenement')),
            ],
        ),
    ]
