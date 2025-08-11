from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def notify_manager(subject, message):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.MANAGER_EMAIL],
        fail_silently=False,
    )


def send_stock_alert(product, alert_type):
    subject = f"Stock Alert: {product.name}"
    message = render_to_string('inventory/emails/stock_alert.html', {
        'product': product,
        'alert_type': alert_type,
    })

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.MANAGER_EMAIL]
    )
    email.content_subtype = "html"
    email.send()
