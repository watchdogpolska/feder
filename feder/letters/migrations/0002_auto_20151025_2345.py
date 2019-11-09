import django
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("letters", "0001_initial"),
        ("cases", "0004_case_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="letter",
            name="author_user",
            field=models.ForeignKey(
                verbose_name="Author (if user)",
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="letter",
            name="case",
            field=models.ForeignKey(
                verbose_name="Case",
                on_delete=django.db.models.deletion.CASCADE,
                to="cases.Case",
            ),
        ),
        migrations.AddField(
            model_name="letter",
            name="message",
            field=models.ForeignKey(
                verbose_name="Message",
                on_delete=django.db.models.deletion.CASCADE,
                to="letters.Letter",
                help_text="Message registered",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attachment",
            name="record",
            field=models.ForeignKey(
                to="letters.Letter", on_delete=django.db.models.deletion.CASCADE
            ),
        ),
    ]
