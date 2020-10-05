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
    mac = MACAddressFormField(label='MAC address',
                              widget=forms.TextInput(attrs={
                                  'label': 'MAC',
                                  'class': 'form-control',
                                  'id': 'input_mac'
                                  }), required=False)


class CustOperations(forms.Form):
    action = forms.ChoiceField(
        choices=(
            ('add', 'Добавить пользователя'),
            ('del', 'Удалить пользователя'),
            ('new_mac', 'Новый MAC')
            ),
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    ip = forms.GenericIPAddressField(
        label='IP address',
        protocol='IPv4',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'id': 'ip_field'}),
        required=False
        )
    mac = MACAddressFormField(label='MAC address',
                              widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'id': 'input_mac'
                                  }), required=False)
    firm_name = forms.CharField(label='Название компании',
                                max_length=50,
                                min_length=3,
                                widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'id': 'firm_name'}),
                                required=False
                                )
    url = forms.URLField(label='Ссылка на заявку',
                         min_length=40,
                         max_length=60,
                         widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'id': 'url'}),
                         required=False)
