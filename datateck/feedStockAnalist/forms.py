from django import forms

class CreateAnalyzeForm(forms.Form):
    production_orders_list = forms.CharField()
