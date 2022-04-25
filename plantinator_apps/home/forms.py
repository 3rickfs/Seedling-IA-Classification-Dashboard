from .models import seedling_process_analysis
from django import forms

class SPA_Form(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(SPA_Form, self).__init__(*args, **kwargs)
		## add a "form-control" class to each form input
		## for enabling bootstrap
		for name in self.fields.keys():
			self.fields[name].widget.attrs.update({
				'class':'form-control'
				})

	class Meta:
		model = seedling_process_analysis
		fields = ("__all__")