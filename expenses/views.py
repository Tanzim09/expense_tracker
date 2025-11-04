from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from .forms import ExpenseForm, RegisterForm
import csv
import json
from .models import Expense, Category
from datetime import date, timedelta
from django.db.models import Sum
from django.shortcuts import get_object_or_404
import csv
from django.http import HttpResponse
from .tasks import export_expenses_csv


# Create your views here.

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created! You can log in now.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'expenses/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Welcome back!')
            
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'expenses/login.html')


def logout_user(request):
    logout(request)
    messages.info(request, 'Logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    qs = Expense.objects.filter(user=request.user) # Only for the currently logged in user

    # Gets the filter values: start_date, end_date, category
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    cat = request.GET.get('category')

    # Filters accordign to values
    if start:
        qs = qs.filter(date__gte=start) # From this date (Inclusive)
    if end:
        qs = qs.filter(date__lte=end) # Upto this date (Inclusive)
    if cat and cat != 'all':
        qs = qs.filter(category__name=cat)

    # totals
    total_all = qs.aggregate(total=Sum('amount'))['total'] or 0

    today = date.today()
    # month_qs = qs.filter(date__year=today.year, date__month=today.month)
    # leaving monthly option for now

    # PIE CHART
    # group by category and sum
    by_cat = (qs
          .values('category__name')
          .annotate(total=Sum('amount'))
          .order_by('-total'))
    
    # extract data for Chart.js
    labels = [r['category__name'] or 'Uncategorized' for r in by_cat]
    data = [float(r['total']) for r in by_cat]

    # BAR PLOT
    # last 6 days totals for bar plot
    last_days = [today - timedelta(days=i) for i in range(5,-1,-1)]
    daily_labels, daily_values = [], []
    for d in last_days:
        day_total = qs.filter(date=d).aggregate(total=Sum('amount'))['total'] or 0
        daily_labels.append(d.strftime('%b %d'))
        daily_values.append(float(day_total))

    categories = Category.objects.order_by('name')

    context = {
        'expenses': qs.order_by('-date','-id')[:50],  # recent 50
        'categories': categories,
        'selected_category': cat or 'all',
        'start_date': start or '',
        'end_date': end or '',

        # KPI card
        'total_all': total_all,

        # charts payloads
        'pie_labels': json.dumps(labels),
        'pie_data': json.dumps(data),
        'bar_labels': json.dumps(daily_labels),
        'bar_data': json.dumps(daily_values),
    }
    return render(request, 'expenses/dashboard.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})


@login_required
def update_expense(request, pk):
    # 404 if not owned by user
    exp = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated.')
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=exp)
    return render(request, 'expenses/add_expense.html', {'form': form, 'update': True})


@login_required
def delete_expense(request, pk):
    exp = get_object_or_404(Expense, pk=pk, user=request.user)
    # one-click delete
    exp.delete()
    messages.warning(request, 'Expense deleted.')
    return redirect('dashboard')


@login_required
def export_csv(request):
    """
    Start a background Celery task to export users expenses and email the link.
    """

    # (None = task will export everything for the user)
    start = request.GET.get('start_date') or None
    end = request.GET.get('end_date') or None
    category = request.GET.get('category') or None

    export_expenses_csv.delay(request.user.id, start, end, category)
    messages.info(request, "Export started… you’ll receive an email with your CSV file when it’s ready.")
    return redirect('dashboard')