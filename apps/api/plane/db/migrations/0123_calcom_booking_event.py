# Proman Phase 3 Step 2 (2026-06-28)
# Per ADR 0002 — adds CalcomBookingEvent for webhook idempotency + audit log.
#
# Hand-written migration. After pulling, run:
#     python manage.py makemigrations --check --dry-run
# If output is "No changes detected", this migration matches the model state.
# Otherwise regenerate with makemigrations and commit the auto-generated version.

import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ("db", "0122_proman_booking_link_template"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CalcomBookingEvent",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Last Modified At"),
                ),
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("calcom_booking_id", models.BigIntegerField(unique=True)),
                (
                    "calcom_event_type_id",
                    models.IntegerField(blank=True, null=True),
                ),
                ("payload", models.JSONField(default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("received", "Received"),
                            ("processing", "Processing"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                            ("ignored", "Ignored"),
                        ],
                        default="received",
                        max_length=16,
                    ),
                ),
                ("created_issue_ids", models.JSONField(default=list)),
                ("error_message", models.TextField(blank=True, default="")),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created By",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Last Modified By",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.CASCADE,
                        related_name="calcom_booking_events",
                        to="db.workspace",
                    ),
                ),
                (
                    "booking_link",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="booking_events",
                        to="db.bookinglink",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cal.com booking event",
                "verbose_name_plural": "Cal.com booking events",
                "db_table": "calcom_booking_events",
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddIndex(
            model_name="calcombookingevent",
            index=models.Index(fields=["status"], name="calcom_book_status_idx"),
        ),
        migrations.AddIndex(
            model_name="calcombookingevent",
            index=models.Index(
                fields=["booking_link", "-created_at"],
                name="calcom_book_link_created_idx",
            ),
        ),
    ]
