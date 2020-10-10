from django import forms
from .utils import proper_mac


def ip_field(required=True):
    return forms.GenericIPAddressField(
                label='ip ad',
                protocol='IPv4',
                widget=forms.TextInput(
                    attrs={'class': 'form-control',
                           'id': 'ip_field'}
                ),
                required=required
                )


def choice_field(**kwargs):
    return forms.ChoiceField(
                choices=kwargs.get('choices'),
                widget=forms.Select(attrs={'class': 'form-control'}))


class HomeForm(forms.Form):
    ip = ip_field()


class BillForm(forms.Form):
    action = choice_field(choices=(
                    ('check', 'Проверить статус'),
                    ('block', 'Заблокировать'),
                    ('unblock', 'Разблокировать')))
    ip = ip_field()


class ConfigForm(forms.Form):
    action = choice_field(choices=(
                    ('add', 'Добавить пользователя'),
                    ('del', 'Удалить пользователя'),
                    ('update', 'Изменить данные')))

    ip = ip_field(required=False)

    mac = forms.CharField(label='MAC address',
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
                         max_length=70,
                         widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'id': 'url'}),
                         required=False)

    def clean_mac(self):
        mac = self.cleaned_data.get('mac')
        if proper_mac(mac):
            self.cleaned_data['mac'] = proper_mac(mac)
            print(self.cleaned_data['mac'])
            return self.cleaned_data['mac']
        else:
            raise forms.ValidationError('Enter valid MAC Address')

    def clean(self):
        # Receive cleaned form data after standard validation
        cleaned_data = super(ConfigForm, self).clean()
        action = cleaned_data.get('action')

        # Add customer
        if action == 'add':
            # All DISPLAYED fields are required
            if self.data.get('mac') \
               and self.data.get('firm_name') \
               and self.data.get('url'):
                return cleaned_data
            else:
                raise forms.ValidationError('Fill empty fields')

        # Delete customer
        if action == 'del':
            # Only IP field is required
            if self.data.get('ip'):
                return cleaned_data
            else:
                raise forms.ValidationError('Fill IP field')

        # Change some of customer data
        if action == 'update':
            # At least one of optional fields required
            optional = self.data.get('mac') \
                       or self.data.get('firm_name') \
                       or self.data.get('url')
            # IP is the only mandatory field in this case
            if self.data.get('ip') and optional:
                return cleaned_data
            else:
                raise forms.ValidationError('Fill IP and optional fields')
