from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("teryt_tree", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="JST",
            fields=[],
            options={"proxy": True},
            bases=("teryt_tree.jednostkaadministracyjna",),
        )
    ]
