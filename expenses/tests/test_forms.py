# expenses/tests/test_forms.py
from django.test import TestCase
from expenses.forms import ExpenseForm
from expenses.models import Category
from datetime import date

class ExpenseFormTest(TestCase):
    # testing if our form works properly when valid data is given
    def test_valid_data(self):
        category = Category.objects.create(name="Utilities")
        form = ExpenseForm(data={
            "description": "Electricity bill",
            "amount": 120.50,
            "category": category.id,
            "date": date.today()
        })
        self.assertTrue(form.is_valid(), form.errors)
        
    # testing if form catches invalid (empty) input
    def test_invalid_data(self):
        form = ExpenseForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)
        self.assertIn("amount", form.errors)
