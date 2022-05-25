from django import forms

class InitialDatePickerInput(forms.DateInput):
    input_type = 'date'

class FinalDatePickerInput(forms.DateInput):
    input_type = 'date'
