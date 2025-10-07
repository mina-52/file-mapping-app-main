from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from .forms import UploadForm
from .services import add_data_to_csv, create_map_html, get_dataframe_from_csv, upload_file_to_supabase_storage
from .utils import geocode_address, reverse_geocode
from django.conf import settings
import os
import pandas as pd
from datetime import datetime
import requests
import urllib.parse
from .models import Archive
from django.utils import timezone

def map_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. ファイルをSupabase Storageに保存
            uploaded_file = request.FILES['file']
            storage_file_name = uploaded_file.name
            public_url = upload_file_to_supabase_storage(uploaded_file, storage_file_name)
            file_path = public_url

            # 2. 位置情報の取得
            lat = form.cleaned_data.get('latitude')
            lon = form.cleaned_data.get('longitude')
            address = form.cleaned_data.get('address', '')

            # 地図上でクリックされた場合
            if lat is not None and lon is not None:
                # 逆ジオコーディングで住所を取得
                if not address:
                    address = reverse_geocode(lat, lon)
            # 住所が手動入力された場合
            elif address:
                lat, lon = geocode_address(address)
            else:
                # 位置情報がない場合はエラー
                return render(request, 'archive_app/index.html', {
                    'form': form,
                    'error': '地図上でクリックするか、住所を入力してください。'
                })

            if lat is not None and lon is not None:
                # 3. データを準備してCSVに保存
                new_data = {
                    'file_path': file_path,
                    'file_type': form.cleaned_data['file_type'],
                    'description': form.cleaned_data.get('description', ''),
                    'address': address,
                    'latitude': lat,
                    'longitude': lon,
                    'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                add_data_to_csv(new_data)
            else:
                # エラーメッセージをユーザーに表示する処理
                return render(request, 'archive_app/index.html', {
                    'form': form,
                    'error': f'位置情報の取得に失敗しました: {address}'
                })

            return redirect('map_view') # 処理後に同じページにリダイレクトして再表示
    else:
        form = UploadForm()

    context = {
        'form': form,
    }
    return render(request, 'archive_app/index.html', context)

def get_markers(request):
    """
    既存のマーカーデータをJSON形式で返すAPIエンドポイント
    """
    try:
        df = get_dataframe_from_csv()
        markers = []
        
        if df.empty:
            return JsonResponse(markers, safe=False)
        
        for _, row in df.iterrows():
            # 緯度・経度の存在確認
            if 'latitude' not in row.index or 'longitude' not in row.index:
                continue
                
            lat = row['latitude']
            lon = row['longitude']
            
            # 数値の確認
            try:
                lat_val = float(lat) if lat is not None and str(lat).strip() != '' and str(lat).strip() != 'nan' else None
                lon_val = float(lon) if lon is not None and str(lon).strip() != '' and str(lon).strip() != 'nan' else None
            except (ValueError, TypeError):
                continue
                
            if lat_val is not None and lon_val is not None:
                markers.append({
                    'latitude': lat_val,
                    'longitude': lon_val,
                    'address': str(row.get('address', '')) if row.get('address') and str(row.get('address')).strip() != '' and str(row.get('address')).strip() != 'nan' else '',
                    'file_type': str(row.get('file_type', 'other')),
                    'description': str(row.get('description', '')) if row.get('description') and str(row.get('description')).strip() != '' and str(row.get('description')).strip() != 'nan' else '',
                    'file_name': os.path.basename(str(row.get('file_path', ''))),
                    'upload_date': str(row.get('upload_date', '')) if row.get('upload_date') and str(row.get('upload_date')).strip() != '' and str(row.get('upload_date')).strip() != 'nan' else ''
                })
        
        return JsonResponse(markers, safe=False)
    except Exception as e:
        print(f"マーカー取得エラー: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def file_list(request):
    """
    アップロードされたファイルの一覧を表示
    """
    try:
        df = get_dataframe_from_csv()
        files = []
        
        if df.empty:
            context = {'files': []}
            return render(request, 'archive_app/file_list.html', context)
        
        for _, row in df.iterrows():
            try:
                # 緯度・経度の処理
                lat = None
                lon = None
                if 'latitude' in row and 'longitude' in row:
                    try:
                        lat = float(row['latitude']) if row['latitude'] is not None and str(row['latitude']).strip() != '' and str(row['latitude']).strip() != 'nan' else None
                        lon = float(row['longitude']) if row['longitude'] is not None and str(row['longitude']).strip() != '' and str(row['longitude']).strip() != 'nan' else None
                    except (ValueError, TypeError):
                        pass
                
                files.append({
                    'file_name': os.path.basename(str(row.get('file_path', ''))),
                    'file_type': str(row.get('file_type', 'other')),
                    'description': str(row.get('description', '')) if row.get('description') and str(row.get('description')).strip() != '' and str(row.get('description')).strip() != 'nan' else '',
                    'address': str(row.get('address', '')) if row.get('address') and str(row.get('address')).strip() != '' and str(row.get('address')).strip() != 'nan' else '',
                    'latitude': lat,
                    'longitude': lon,
                    'upload_date': str(row.get('upload_date', '')) if row.get('upload_date') and str(row.get('upload_date')).strip() != '' and str(row.get('upload_date')).strip() != 'nan' else '',
                    'file_url': str(row.get('file_path', ''))
                })
            except Exception as e:
                print(f"ファイル処理エラー: {e}")
                continue
        
        # アップロード日時で降順ソート
        files.sort(key=lambda x: x['upload_date'], reverse=True)
        
        context = {
            'files': files
        }
        return render(request, 'archive_app/file_list.html', context)
    except Exception as e:
        print(f"ファイル一覧取得エラー: {e}")
        context = {
            'files': [],
            'error': str(e)
        }
        return render(request, 'archive_app/file_list.html', context)

def download_file(request):
    """
    SupabaseのパブリックURLからファイルを取得し、ダウンロードレスポンスとして返す
    """
    file_url = request.GET.get('url')
    filename = request.GET.get('filename')
    if not file_url:
        return HttpResponse('URLが指定されていません'.encode('utf-8'), status=400)
    file_url = urllib.parse.unquote(file_url)
    if not filename:
        # URLの最後の/以降をファイル名として利用
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
        return HttpResponse(f'ダウンロードエラー: {e}'.encode('utf-8'), status=500)
