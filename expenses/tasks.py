from __future__ import annotations
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Sum
from django.utils import timezone
from pathlib import Path
import csv
from .models import Expense

# Celery tasks

User = get_user_model()


@shared_task
def export_expenses_csv(user_id, start=None, end=None, category=None):

    # Export the users expenses to a CSV file. Runs in celery worker
    user = User.objects.get(pk=user_id)
    
    qs = Expense.objects.filter(user=user)

    # add filters if user applied any
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if category and category != "all":
        qs = qs.filter(category__name=category)

    exports_dir = Path(settings.MEDIA_ROOT) / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    stamp = timezone.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{user.username}-{stamp}.csv"
    path = exports_dir / filename

    # writing the  csv file manually
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Category", "Description", "Amount"])
        for e in qs.order_by("date").iterator(chunk_size=1000):
            writer.writerow([
                e.date.isoformat(),
                e.category.name if e.category else "Uncategorized",
                e.description,
                f"{e.amount}",
            ])

    
    base = getattr(settings, "BASE_URL", "http://localhost:8000").rstrip("/")
    public_url = f"{base}{settings.MEDIA_URL}exports/{filename}"

    # email the user when done (uses Gmail settings)
    send_mail(
        subject="Your Expense CSV Export is Ready",
        message=f"Your CSV export is ready.\n\nDownload here:\n{public_url}\n",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

    return str(path)


@shared_task
def send_monthly_summary():
   
    # On the 1st of each month, email users their total from last month.
    today = timezone.now().date()
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - timezone.timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    for user in User.objects.all():
        total = (
            Expense.objects
            .filter(user=user, date__gte=last_month_start, date__lte=last_month_end)
            .aggregate(total=Sum("amount"))["total"] or 0
        )
        msg = (
            f"Hi {user.username},\n\n"
            f"Your total expenses for {last_month_start.strftime('%B %Y')}: {total}\n"
        )
        send_mail(
            "Your Monthly Expense Summary",
            msg,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
