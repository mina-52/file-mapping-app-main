from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .forms import UploadForm
from .services import add_data_to_csv, create_map_html
from .utils import geocode_address
from django.conf import settings
import os

def map_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. ファイルを保存
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()
            # ファイル名が重複しないように保存
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            # 2. 住所をジオコーディング
            address = form.cleaned_data['address']
            lat, lon = geocode_address(address)

            if lat is not None and lon is not None:
                # 3. データを準備してCSVに保存
                new_data = {
                    'file_path': file_path,
                    'file_type': form.cleaned_data['file_type'],
                    'address': address,
                    'latitude': lat,
                    'longitude': lon,
                }
                add_data_to_csv(new_data)
            else:
                # エラーメッセージをユーザーに表示する処理（オプション）
                print(f"ジオコーディングに失敗しました: {address}")

            return redirect('map_view') # 処理後に同じページにリダイレクトして再表示
    else:
        form = UploadForm()

    # 地図HTMLを生成
    map_html = create_map_html()

    context = {
        'form': form,
        'map_html': map_html,
    }
    return render(request, 'archive_app/index.html', context)

# Create your views here.
