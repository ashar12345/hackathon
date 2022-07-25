from django import forms

SERVER = [
('', 'Select'),
('aws', 'AWS'),
('azure', 'Azure'),
]

U_D = [
    ('', 'Select'),
    ('upload', 'Upload'),
    ('download', 'Download')
]

class AzureForm(forms.Form):
    con_str = forms.CharField(required=False)
    con_name = forms.CharField(required=False)
    key_id = forms.CharField(required=False)
    key_secret = forms.CharField(required=False)
    bucket_name = forms.CharField(required=False)
    server = forms.CharField(label='Select the Server', widget=forms.Select(choices=SERVER))
    u_d = forms.CharField(label='Upload or Download?', widget=forms.Select(choices=U_D))
    document = forms.FileField(widget=forms.FileInput(attrs = {'multiple': True}), required=False)

class AzureForm2(forms.Form):
    choices = forms.CharField(widget  = forms.CheckboxSelectMultiple)