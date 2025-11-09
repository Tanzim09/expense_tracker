from django.test import TestCase
from django.contrib.auth.models import User
from expenses.models import Expense, Category
from datetime import date
from decimal import Decimal

class CategoryModelTest(TestCase):
    def setUp(self):
        Category.objects.all().delete()  # clear duplicates

    def test_str_method(self):
        category = Category.objects.create(name="Food")
        # when we convert category to string, it should return its name
        self.assertEqual(str(category), "Food")


class ExpenseModelTest(TestCase):
    # setting up sample data once for the class
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.category = Category.objects.create(name="Transport")
        self.expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            description="Bus fare",
            amount=Decimal("3.50"),
            date=date.today(),
        )

    def test_expense_creation_fields(self):
        # checking if all fields got saved properly
        self.assertEqual(self.expense.description, "Bus fare")
        self.assertEqual(self.expense.category.name, "Transport")
        self.assertEqual(self.expense.user.username, "testuser")
        self.assertEqual(self.expense.amount, Decimal("3.50"))

    def test_expense_str(self):
        self.assertIn("Bus fare", str(self.expense))
