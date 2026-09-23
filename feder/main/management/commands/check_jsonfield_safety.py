import json

from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.db import connection
from tqdm import tqdm

from feder.institutions.models import Institution
from feder.letters.logs.models import LogRecord
from feder.letters.models import Letter
from feder.monitorings.models import Monitoring

CHECKS = [
    (Letter, "normalized_response"),
    (LogRecord, "data"),
    (Institution, "extra"),
    (Monitoring, "responses_chat_context"),
    (Monitoring, "normalized_response_template"),
    (Monitoring, "normalized_response_answers_categories"),
]

BATCH_SIZE = 2000


class Command(BaseCommand):
    help = (
        "Check whether the raw TEXT stored in jsonfield.JSONField-backed columns "
        "is valid JSON (or NULL), i.e. whether it's safe to swap those fields to "
        "Django's native models.JSONField and run `ALTER TABLE ... MODIFY COLUMN "
        "... JSON`. Reads raw column bytes via a cursor, bypassing jsonfield's "
        "descriptor which would otherwise hand back already-deserialized objects."
    )

    def add_arguments(self, parser):
        parser.add_argument("--no-progress", dest="progress", action="store_false")

    def check_field(self, model, field_name, progress):
        table = model._meta.db_table
        column = model._meta.get_field(field_name).column
        pk_column = model._meta.pk.column

        total = 0
        null_count = 0
        empty_string_pks = []
        bad_rows = []  # (pk, error, snippet)

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT `{pk_column}`, `{column}` FROM `{table}`")
            my_iter = tqdm if progress else lambda x, **kwargs: x
            while True:
                rows = cursor.fetchmany(BATCH_SIZE)
                if not rows:
                    break
                for pk, raw in my_iter(rows, desc=f"{table}.{column}", leave=False):
                    total += 1
                    if raw is None:
                        null_count += 1
                        continue
                    if raw == "":
                        empty_string_pks.append(pk)
                        continue
                    try:
                        json.loads(raw)
                    except (TypeError, ValueError) as exc:
                        bad_rows.append((pk, str(exc), raw[:120]))

        return {
            "label": f"{model.__name__}.{field_name} ({table}.{column})",
            "total": total,
            "null": null_count,
            "empty_string": empty_string_pks,
            "invalid": bad_rows,
        }

    def handle(self, *args, **options):
        progress = options["progress"]
        results = [
            self.check_field(model, field_name, progress)
            for model, field_name in CHECKS
        ]

        for r in results:
            self.stdout.write(f"\n=== {r['label']} ===")
            self.stdout.write(
                f"total={r['total']} null={r['null']} "
                f"empty_string={len(r['empty_string'])} "
                f"invalid_json={len(r['invalid'])}"
            )
            if r["empty_string"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"  empty-string pks (first 20): {r['empty_string'][:20]}"
                    )
                )
            if r["invalid"]:
                self.stdout.write(self.style.ERROR("  invalid rows (first 20):"))
                for pk, err, snippet in r["invalid"][:20]:
                    self.stdout.write(
                        self.style.ERROR(f"    pk={pk} error={err} value={snippet!r}")
                    )

        self.stdout.write("\n=== SUMMARY ===")
        all_safe = True
        for r in results:
            problems = len(r["empty_string"]) + len(r["invalid"])
            if problems:
                all_safe = False
                self.stdout.write(
                    self.style.ERROR(
                        f"{r['label']}: NEEDS ATTENTION ({problems} problem rows)"
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS(f"{r['label']}: OK"))

        if not all_safe:
            raise CommandError(
                "Not safe to convert to native JSONField - fix flagged rows first"
            )
        self.stdout.write(
            self.style.SUCCESS("\nSafe to convert to native JSONField: YES")
        )
