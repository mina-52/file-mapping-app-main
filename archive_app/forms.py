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
    description = forms.CharField(
        label="説明", 
        max_length=500, 
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'placeholder': 'ファイルの説明やメモを入力してください（オプション）'
        })
    )
    address = forms.CharField(
        label="住所", 
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '地図上でクリックするか、手動で入力してください'})
    )
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)