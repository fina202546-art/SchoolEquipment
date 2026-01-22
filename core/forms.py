from django import forms
from .models import User, Equipment

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    niigata_question = forms.CharField(
        label="NIIGATAで一番ハンサムなのは誰ですか？",
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        answer = cleaned_data.get("niigata_question")

        if role == 'admin' and (not answer or answer.upper() != "PHAP"):
            raise forms.ValidationError(
                "回答が正しくありません。管理者として登録することはできません。"
            )
        return cleaned_data


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'serial', 'description', 'condition', 'status', 'image']
        labels = {
            'name': '備品名',
            'serial': '管理番号（重複不可）',
            'description': '機器の詳細説明',
            'condition': '現在の状態',
            'status': '在庫状況',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'condition': forms.Textarea(attrs={'rows': 2}),
        }

class BorrowForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': '使用目的を具体的に入力してください…'
        }),
        label="設備の貸出理由"
    )
    agreement = forms.BooleanField(
        required=True,
        label="利用規則を遵守し、設備を適切に管理することを誓約します。"
    )

