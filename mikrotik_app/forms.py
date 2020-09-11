from django import forms

ACTIONS = (
            ('check', 'Проверить статус'),
            ('block', 'Заблокировать'),
            ('unblock', 'Разблокировать'),
            ('new_mac', 'Новый MAC'),
            ('delete_ip', 'Удалить IP')
          )


class IPOperations(forms.Form):
    ip = forms.GenericIPAddressField(
        label='IP address',
        protocol='IPv4',
        widget=forms.TextInput(attrs={'class': 'form-control'})
        )
    action = forms.ChoiceField(
        choices=ACTIONS,
        widget=forms.Select(attrs={'class': 'form-control'})
        )
