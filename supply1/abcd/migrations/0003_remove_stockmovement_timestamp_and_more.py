from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('abcd', '0002_order_paymenttransaction_shipment_stockmovement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='StockMovement',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='StockMovement',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='StockMovement',
            name='movement_type',
            field=models.CharField(choices=[('in', 'In'), ('out', 'Out'), ('adjust', 'Adjust')], max_length=10),
        ),
        migrations.AlterField(
            model_name='StockMovement',
            name='reason',
            field=models.TextField(blank=True),
        ),
    ]