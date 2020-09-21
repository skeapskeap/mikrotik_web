from django import forms
from macaddress.fields import MACAddressFormField

ACTIONS = (
            ('check', 'Проверить статус'),
            ('block', 'Заблокировать'),
            ('unblock', 'Разблокировать'),
            ('new_mac', 'Новый MAC'),
            ('delete_ip', 'Удалить IP')
          )


class IPOperations(forms.Form):
    action = forms.ChoiceField(
        choices=ACTIONS,
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    ip = forms.GenericIPAddressField(
        label='IP address',
        protocol='IPv4',
        widget=forms.TextInput(attrs={'class': 'form-control'})
        )
    mac = MACAddressFormField(label='MAC address',
                              widget=forms.TextInput(attrs={
                                  'class': 'mac_hidden_field',
                                  'id': 'input_mac'
                                  }))
