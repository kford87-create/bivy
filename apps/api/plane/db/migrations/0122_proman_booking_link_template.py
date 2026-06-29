# Proman Phase 3 Step 1 (2026-06-28)
# Per ADR 0002 (Cal.com for scheduling) — adds BookingLink + BookingTemplate.
#
# Hand-written migration. After pulling, run:
#     python manage.py makemigrations --check --dry-run
# to verify this migration matches the model state. If it diverges, regenerate
# via `python manage.py makemigrations` and commit the auto-generated version
# in place of this file.

import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ("db", "0121_alter_estimate_type"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BookingTemplate",
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
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField(blank=True, default="")),
                ("work_items", models.JSONField(default=list)),
                (
                    "kickoff_message_subject",
                    models.CharField(blank=True, default="", max_length=256),
                ),
                (
                    "kickoff_message_body",
                    models.TextField(blank=True, default=""),
                ),
                ("is_default", models.BooleanField(default=False)),
                (
                    "default_assignee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
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
                        on_delete=models.deletion.CASCADE,
                        related_name="booking_templates",
                        to="db.workspace",
                    ),
                ),
            ],
            options={
                "verbose_name": "Booking template",
                "verbose_name_plural": "Booking templates",
                "db_table": "booking_templates",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="BookingLink",
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
                ("slug", models.SlugField(max_length=128)),
                ("calcom_event_type_id", models.IntegerField(blank=True, null=True)),
                (
                    "calcom_event_type_slug",
                    models.CharField(blank=True, default="", max_length=128),
                ),
                ("enabled", models.BooleanField(default=True)),
                ("last_booking_at", models.DateTimeField(blank=True, null=True)),
                ("total_bookings", models.IntegerField(default=0)),
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
                    "project",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="booking_links",
                        to="db.project",
                    ),
                ),
                (
                    "template",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.PROTECT,
                        related_name="links",
                        to="db.bookingtemplate",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="booking_links",
                        to="db.workspace",
                    ),
                ),
            ],
            options={
                "verbose_name": "Booking link",
                "verbose_name_plural": "Booking links",
                "db_table": "booking_links",
                "ordering": ("-created_at",),
                "unique_together": {("workspace", "slug")},
            },
        ),
    ]
