from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(label="ファイル")
    file_type = forms.ChoiceField(
        label="ファイルの種類",
        choices=[
            ('image', '画像'),
            ('video', '動画'),
            ('audio', '音声'),
            ('other', 'その他'),
        ]
    )
    address = forms.CharField(label="住所", max_length=255)