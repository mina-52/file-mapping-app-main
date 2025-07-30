import pandas as pd
import os
import folium
from folium.plugins import MarkerCluster
from supabase import create_client
import urllib.parse

CSV_FILE = os.path.join(os.path.dirname(__file__), 'data', 'uploaded_data.csv')
CSV_COLUMNS = ['file_path', 'file_type', 'description', 'address', 'latitude', 'longitude', 'upload_date']

def add_data_to_csv(data: dict):
    """
    受け取ったデータをCSVファイルに追記する。
    """
    # 必要なフィールドが存在することを確認
    required_fields = ['file_path', 'file_type', 'address', 'latitude', 'longitude']
    for field in required_fields:
        if field not in data:
            data[field] = ''
    
    # オプションフィールドのデフォルト値を設定
    if 'description' not in data:
        data['description'] = ''
    if 'upload_date' not in data:
        data['upload_date'] = ''
    
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

    df_new = pd.DataFrame([data])
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, index=False, header=True, encoding='utf-8-sig')
    else:
        df_new.to_csv(CSV_FILE, mode='a', index=False, header=False, encoding='utf-8-sig')

def get_dataframe_from_csv():
    """
    CSVファイルからデータを読み込み、pandasデータフレームとして返す。
    """
    if not os.path.exists(CSV_FILE):
        empty_df = pd.DataFrame()
        for column in CSV_COLUMNS:
            empty_df[column] = []
        return empty_df
    
    try:
        # CSVファイルを読み込み、エラー処理を追加
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig', dtype=str)
        
        # 古いCSVファイルの場合、新しいフィールドを追加
        for column in CSV_COLUMNS:
            if column not in df.columns:
                df[column] = ''
        
        # 不要な列を削除（CSV_COLUMNSに含まれていない列）
        columns_to_keep = [col for col in df.columns if col in CSV_COLUMNS]
        df = df[columns_to_keep]
        
        # 空の値をNaNに変換
        df = df.replace('', pd.NaT)
        
        return df
    except Exception as e:
        print(f"CSV読み込みエラー: {e}")
        # エラーの場合は空のDataFrameを返す
        empty_df = pd.DataFrame()
        for column in CSV_COLUMNS:
            empty_df[column] = []
        return empty_df

def create_map_html() -> str:
    """
    データフレームからfoliumの地図を生成し、HTML文字列として返す。
    """
    df = get_dataframe_from_csv()

    # データがあればその平均位置を、なければ日本の中心あたりを初期表示
    if not df.empty and 'latitude' in df.columns and 'longitude' in df.columns:
        # 有効な座標をフィルタリング
        valid_coords = []
        for _, row in df.iterrows():
            lat = row.get('latitude')
            lon = row.get('longitude')
            if lat is not None and str(lat).strip() != '' and str(lat).strip() != 'nan' and lon is not None and str(lon).strip() != '' and str(lon).strip() != 'nan':
                try:
                    valid_coords.append([float(lat), float(lon)])
                except (ValueError, TypeError):
                    continue
        
        if valid_coords:
            # 平均位置を計算
            avg_lat = sum(coord[0] for coord in valid_coords) / len(valid_coords)
            avg_lon = sum(coord[1] for coord in valid_coords) / len(valid_coords)
            map_center = [avg_lat, avg_lon]
            zoom_start = 5
        else:
            map_center = [36.204824, 138.252924]  # 日本の地理的中心
            zoom_start = 5
    else:
        map_center = [36.204824, 138.252924]  # 日本の地理的中心
        zoom_start = 5

    gsi_tile_url = "https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png"
    gsi_attribution = "<a href='https://maps.gsi.go.jp/development/ichiran.html' target='_blank'>地理院タイル</a>"

    # folium.Map() の引数に tiles と attr を追加
    m = folium.Map(
        location=map_center,
        zoom_start=zoom_start,
        tiles=gsi_tile_url,
        attr=gsi_attribution
    )

    # MarkerClusterのインスタンスを作成し、地図に追加
    marker_cluster = MarkerCluster().add_to(m)

    icon_settings = {
        'image': {'color': 'blue', 'icon': 'camera'},
        'video': {'color': 'red', 'icon': 'video-camera'},
        'audio': {'color': 'green', 'icon': 'music'},
        'other': {'color': 'purple', 'icon': 'file'}
    }

    # ループ処理でマーカーを生成
    for _, row in df.iterrows():
        if 'latitude' in row and 'longitude' in row:
            lat = row['latitude']
            lon = row['longitude']
            if lat is not None and str(lat).strip() != '' and str(lat).strip() != 'nan' and lon is not None and str(lon).strip() != '' and str(lon).strip() != 'nan':
                
                file_type = str(row.get('file_type', 'other'))
                file_name = os.path.basename(str(row.get('file_path', '')))
                file_url = str(row.get('file_path', ''))

                media_html = ""
                if file_type == 'image':
                    media_html = f'<img src="{file_url}" style="max-width:380px; height:auto; display:block; margin-top:10px;">'
                elif file_type == 'video':
                    media_html = f'<video controls style="width:100%; max-width:380px; display:block; margin-top:10px;"><source src="{file_url}"></video>'
                elif file_type == 'audio':
                    media_html = f'<audio controls style="width:100%; margin-top:10px;"><source src="{file_url}"></audio>'
            
                # 説明フィールドの処理
                description = str(row.get('description', '')) if row.get('description') and str(row.get('description')).strip() != '' and str(row.get('description')).strip() != 'nan' else ''
                description_html = f'<br><b>説明:</b> {description}' if description else ''
                
                # ファイル一覧ページの該当ファイルへのアンカーリンクを生成
                file_list_url = f"/files/#file-{urllib.parse.quote(file_name)}"
                # ポップアップ全体のHTMLを組み立て
                popup_html = f"""
                <div style="min-width:150px;">
                    <b>住所:</b> {row.get('address', '')}<br>
                    <b>種類:</b> {file_type}{description_html}

                    {media_html}

                    <div style="margin-top:10px; display:flex; flex-direction:column; gap:4px;">
                        <a href="{file_list_url}" target="_blank" class="btn-view">ファイル一覧で見る</a>
                    </div>
                </div>
                """
                
                # アイコンの設定を取得
                setting = icon_settings.get(file_type, icon_settings['other'])
                
                marker = folium.Marker(
                    location=[float(lat), float(lon)],
                    popup=folium.Popup(popup_html, max_width=400),
                    icon=folium.Icon(color=setting['color'], icon=setting['icon'], prefix='fa')
                )
                
                # マーカーを marker_cluster に追加する
                marker.add_to(marker_cluster)

    # 地図のHTMLを取得
    map_html = m._repr_html_()
    
    # 地図のdiv要素にIDを追加
    map_html = map_html.replace('<div class="folium-map"', '<div class="folium-map" id="map"')
    
    return map_html

def upload_file_to_supabase_storage(local_file, storage_file_name):
    """
    Supabase Storageにファイルをアップロードし、公開URLを返す
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if not supabase_url or not supabase_key:
        raise Exception("Supabaseの環境変数が設定されていません")
    supabase = create_client(supabase_url, supabase_key)
    # ファイルをバイト列に変換してアップロード
    file_bytes = local_file.read()
    res = supabase.storage.from_("file-mapping-bucket").upload(storage_file_name, file_bytes)
    # 公開URLを取得
    public_url = supabase.storage.from_("file-mapping-bucket").get_public_url(storage_file_name)
    return public_url
