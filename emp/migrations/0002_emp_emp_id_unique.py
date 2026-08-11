from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emp",
            name="emp_id",
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
