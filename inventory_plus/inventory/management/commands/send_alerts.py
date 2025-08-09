# inventory/management/commands/send_alerts.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import F
from datetime import timedelta

from inventory.models import Product


class Command(BaseCommand):
    help = "Send low-stock and expiry alerts for products."

    def add_arguments(self, parser):
        parser.add_argument(
            "--expiry-days",
            type=int,
            default=30,
            help="Notify for products expiring within this many days (default: 30).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force sending notifications even if they were sent recently.",
        )

    def handle(self, *args, **options):
        expiry_days = options["expiry_days"]
        force = options["force"]

        manager_email = getattr(settings, "MANAGER_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None)
        if not manager_email:
            self.stdout.write(self.style.ERROR("No manager email configured."))
            return

        now = timezone.now()
        expiry_threshold_date = timezone.localdate() + timedelta(days=expiry_days)

        # Low stock alerts
        low_products = Product.objects.filter(quantity__lte=F('low_stock_threshold')).order_by('quantity')
        low_sent = 0
        for p in low_products:
            if force or not p.last_low_stock_notified or (now - p.last_low_stock_notified > timedelta(hours=24)):
                subject = f"Low stock alert: {p.name}"
                html_content = render_to_string("inventory/emails/low_stock.html", {"product": p})
                email = EmailMessage(subject, html_content, settings.EMAIL_HOST_USER, [manager_email])
                email.content_subtype = "html"
                try:
                    email.send()
                    p.last_low_stock_notified = now
                    p.save(update_fields=["last_low_stock_notified"])
                    low_sent += 1
                    self.stdout.write(self.style.SUCCESS(f"Sent low-stock alert for: {p.name}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send low-stock alert for {p.name} — {e}"))

        # Expiry alerts
        expiry_products = Product.objects.filter(
            expiry_date__isnull=False,
            expiry_date__lte=expiry_threshold_date
        ).order_by('expiry_date')

        expiry_sent = 0
        for p in expiry_products:
            if force or not p.last_expiry_notified or (now - p.last_expiry_notified > timedelta(hours=24)):
                days_left = (p.expiry_date - timezone.localdate()).days if p.expiry_date else None
                subject = f"Expiry alert: {p.name} expires in {days_left} day(s)" if days_left is not None else f"Expiry alert: {p.name}"
                html_content = render_to_string("inventory/emails/expiry_alert.html", {"product": p, "days_left": days_left})
                email = EmailMessage(subject, html_content, settings.EMAIL_HOST_USER, [manager_email])
                email.content_subtype = "html"
                try:
                    email.send()
                    p.last_expiry_notified = now
                    p.save(update_fields=["last_expiry_notified"])
                    expiry_sent += 1
                    self.stdout.write(self.style.SUCCESS(f"Sent expiry alert for: {p.name}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send expiry alert for {p.name} — {e}"))

        self.stdout.write(self.style.WARNING(f"Low-stock alerts sent: {low_sent}, Expiry alerts sent: {expiry_sent}"))
