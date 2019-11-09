import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Email",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        unique=True, max_length=254, verbose_name="E-mail"
                    ),
                ),
            ],
            options={"verbose_name": "Email", "verbose_name_plural": "Emails"},
        ),
        migrations.CreateModel(
            name="Institution",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=250, verbose_name="Name")),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        editable=False,
                        populate_from=b"name",
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "address",
                    models.EmailField(
                        help_text="E-mail address used to contact with institutions",
                        max_length=254,
                        verbose_name="E-mail",
                    ),
                ),
            ],
            options={
                "verbose_name": "Institution",
                "verbose_name_plural": "Institution",
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=15, verbose_name="Name")),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        populate_from=b"name", verbose_name="Slug", editable=False
                    ),
                ),
            ],
            options={"verbose_name": "Tag", "verbose_name_plural": "Tags"},
        ),
    ]
