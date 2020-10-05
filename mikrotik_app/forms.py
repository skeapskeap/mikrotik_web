from django import forms
from macaddress.fields import MACAddressFormField


class CheckIP(forms.Form):
    ip = forms.GenericIPAddressField(
        label='IP address',
        protocol='IPv4',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class IPOperations(forms.Form):
    action = forms.ChoiceField(
        choices=(
                    ('check', 'Проверить статус'),
                    ('block', 'Заблокировать'),
                    ('unblock', 'Разблокировать')
                ),
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    ip = forms.GenericIPAddressField(
        label='IP address',
        protocol='IPv4',
        widget=forms.TextInput(attrs={'class': 'form-control'})
        )


class CustOperations(forms.Form):
    action = forms.ChoiceField(
        choices=(
            ('add', 'Добавить пользователя'),
            ('del', 'Удалить пользователя'),
            ('new_mac', 'Новый MAC')
            ),
        widget=forms.Select(attrs={'class': 'form-control'}))

    ip = forms.GenericIPAddressField(
        label='IP address',
        protocol='IPv4',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'id': 'ip_field'}),
        required=False)

    mac = MACAddressFormField(label='MAC address',
                              widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'id': 'input_mac'
                                  }),
                              required=False)

    firm_name = forms.CharField(label='Название компании',
                                max_length=50,
                                min_length=3,
                                widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'id': 'firm_name'}),
                                required=False)

    url = forms.URLField(label='Ссылка на заявку',
                         min_length=40,
                         max_length=60,
                         widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'id': 'url'}),
                         required=False)
    '''
    def clean(self):
        cleaned_data = super(CustOperations, self).clean()
        if cleaned_data.get('action') == 'add':
            return cleaned_data
        else:
            raise forms.ValidationError('wrong action')
    '''
    def clean(self):
        cleaned_data = super(CustOperations, self).clean()
        action = cleaned_data.get('action')
        if action == 'add':
            if self.data.get('mac') and self.data.get('firm_name') and self.data.get('url'):
                return cleaned_data
            else:
                raise forms.ValidationError('Fill empty fields')
        
        if action == 'del':
            if self.data.get('ip'):
                return cleaned_data
            else:
                raise forms.ValidationError('Fill IP field')

        if action == 'new_mac':
            if self.data.get('ip') and self.data.get('mac'):
                return cleaned_data
            else:
                raise forms.ValidationError('Fill IP and MAC fields')
