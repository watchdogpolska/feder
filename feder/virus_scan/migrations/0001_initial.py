# Generated by Django 2.2.7 on 2019-11-30 05:25

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Request",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                ("field_name", models.CharField(max_length=50)),
                (
                    "engine_name",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="Engine name"
                    ),
                ),
                (
                    "engine_id",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="External ID"
                    ),
                ),
                (
                    "engine_report",
                    jsonfield.fields.JSONField(
                        blank=True, verbose_name="Engine result"
                    ),
                ),
                (
                    "engine_link",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="Engine result URL"
                    ),
                ),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "Created"),
                            (1, "Queued"),
                            (2, "Infected"),
                            (3, "Not detected"),
                            (4, "Failed"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
            options={
                "verbose_name": "Request of virus scan",
                "verbose_name_plural": "Requests of virus scan",
                "ordering": ["created"],
            },
        ),
        migrations.AddIndex(
            model_name="request",
            index=models.Index(
                fields=["content_type", "object_id"],
                name="virus_scan__content_e045f6_idx",
            ),
        ),
    ]
