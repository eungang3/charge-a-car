# Generated by Django 4.1.3 on 2022-11-26 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('coupons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('merchant_uid', models.CharField(max_length=250, unique=True)),
                ('imp_uid', models.CharField(max_length=250, null=True)),
                ('status', models.CharField(max_length=250)),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
            ],
            options={
                'db_table': 'payments',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=250)),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('actual_amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('name', models.CharField(max_length=200)),
                ('card', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.card')),
                ('coupon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='coupons.coupon')),
                ('payment_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pay.payment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
            ],
            options={
                'db_table': 'orders',
            },
        ),
    ]
