from django import forms


class ProfileCountForm(forms.Form):
    count = forms.IntegerField(
        min_value=1,
        max_value=5000,
        label="Количество человек для загрузки",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите число (от 1 до 5000)",
            }
        ),
    )
