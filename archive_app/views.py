# archive_app/views.py

# --- DjangoとPythonの基本ライブラリ ---
import os
import requests
import urllib.parse
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from pathlib import Path
import uuid

# --- このアプリケーションで作成したもの ---
from .forms import UploadForm
from .models import Archive  # データベースと連携するためのモデル
from .services import upload_file_to_supabase_storage # Supabaseアップロード用関数
from .utils import geocode_address, reverse_geocode # ジオコーディング用関数


def map_view(request):
    """
    メインの地図ページを表示、およびファイルアップロードを処理するビュー
    """
    # --- POSTリクエスト（フォームが送信された）場合の処理 ---
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # 1. ファイルをSupabase Storageにアップロードし、公開URLを取得
            original_extension = Path(uploaded_file.name).suffix
            storage_file_name = f"{uuid.uuid4()}{original_extension}"
            public_url = upload_file_to_supabase_storage(uploaded_file, storage_file_name)

            # 2. フォームから送信された緯度・経度・住所を取得
            lat = form.cleaned_data.get('latitude')
            lon = form.cleaned_data.get('longitude')
            address = form.cleaned_data.get('address', '')

            # 3. 緯度・経度と住所を相互に補完
            #    - 住所だけ入力されていれば、緯度・経度を検索
            #    - 緯度・経度だけ入力されていれば、住所を検索
            if not lat and not lon and address:
                lat, lon = geocode_address(address)
            elif lat and lon and not address:
                address = reverse_geocode(lat, lon)
            
            # 4. 最終的な位置情報をもとに、データベースへ保存
            if lat is not None and lon is not None:
                # Archiveモデルのインスタンス（データ1行分）を作成
                archive_data = Archive(
                    file_path=public_url,
                    file_type=form.cleaned_data['file_type'],
                    description=form.cleaned_data.get('description', ''),
                    address=address,
                    latitude=lat,
                    longitude=lon,
                )
                # データベースに保存を実行
                archive_data.save()
            else:
                # 住所から位置が特定できなかった場合のエラー表示
                context = {'form': form, 'error': '位置情報が取得できませんでした。'}
                return render(request, 'archive_app/index.html', context)

            # 処理完了後、同じページにリダイレクトしてフォームの二重送信を防ぐ
            return redirect('map_view')
            
    # --- GETリクエスト（初めてページが表示された）場合の処理 ---
    else:
        form = UploadForm()

    context = {'form': form}
    return render(request, 'archive_app/index.html', context)


def get_markers(request):
    """
    地図に表示するマーカー情報をJSON形式で提供するAPIビュー
    （JavaScriptから非同期で呼び出される）
    """
    # データベースのArchiveテーブルから全てのデータを取得
    all_archives = Archive.objects.all()
    
    markers = []
    # 取得した各データを、JavaScriptで扱いやすい辞書の形に変換
    for item in all_archives:
        markers.append({
            'latitude': item.latitude,
            'longitude': item.longitude,
            'address': item.address,
            'file_type': item.file_type,
            'description': item.description,
            'file_name': os.path.basename(item.file_path),
            'file_url': item.file_path,
            'upload_date': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
        
    return JsonResponse(markers, safe=False)


def file_list(request):
    """
    アップロードされたファイルの一覧ページを表示するビュー
    """
    # データベースから作成日時が新しい順に全てのデータを取得
    files_from_db = Archive.objects.order_by('-created_at')
    
    # 取得したデータをテンプレートに渡す
    context = {
        'files': files_from_db
    }
    return render(request, 'archive_app/file_list.html', context)


def download_file(request):
    """
    SupabaseのURLからファイルを取得し、ダウンロードさせるためのビュー
    （この関数のロジックは変更不要）
    """
    file_url = request.GET.get('url')
    filename = request.GET.get('filename')

    if not file_url:
        return HttpResponse('URLが指定されていません', status=400)
    
    file_url = urllib.parse.unquote(file_url)
    if not filename:
        parsed_url = urllib.parse.urlparse(file_url)
        filename = os.path.basename(parsed_url.path)
        
    try:
        r = requests.get(file_url, stream=True)
        r.raise_for_status()
        
        response = StreamingHttpResponse(r.iter_content(chunk_size=8192), content_type=r.headers.get('Content-Type', 'application/octet-stream'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        if 'Content-Length' in r.headers:
            response['Content-Length'] = r.headers['Content-Length']
            
        return response
    except Exception as e:
        return HttpResponse(f'ダウンロードエラー: {e}', status=500)