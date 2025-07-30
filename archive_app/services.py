# archive_app/services.py

import os
import folium
from folium.plugins import MarkerCluster
from supabase import create_client
import urllib.parse
from .models import Archive  # 👈 データベースのArchiveモデルをインポート

def create_map_html() -> str:
    """
    【変更後】データベースからデータを取得し、同じ場所の情報をまとめて地図を生成する。
    """
    # --- 1. データベースから全データを取得 ---
    all_archives = Archive.objects.all()

    # --- 2. データを場所（緯度・経度）ごとにグループ化する ---
    locations = {}
    for item in all_archives:
        # (緯度, 経度) のタプルをキーとして辞書にまとめる
        coords = (item.latitude, item.longitude)
        if coords not in locations:
            locations[coords] = []
        locations[coords].append(item)

    # --- 3. 地図の中心を計算する ---
    if locations:
        # 登録されている場所の平均位置を計算
        avg_lat = sum(lat for lat, lon in locations.keys()) / len(locations)
        avg_lon = sum(lon for lat, lon in locations.keys()) / len(locations)
        map_center = [avg_lat, avg_lon]
        zoom_start = 5
    else:
        # データがなければ日本の中心を表示
        map_center = [36.204824, 138.252924]
        zoom_start = 5
    
    # --- 4. 地図オブジェクトを作成 ---
    gsi_tile_url = "https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png"
    gsi_attribution = "<a href='https://maps.gsi.go.jp/development/ichiran.html' target='_blank'>地理院タイル</a>"
    m = folium.Map(
        location=map_center,
        zoom_start=zoom_start,
        tiles=gsi_tile_url,
        attr=gsi_attribution
    )
    marker_cluster = MarkerCluster().add_to(m)
    
    icon_settings = {
        'image': {'color': 'blue', 'icon': 'camera'},
        'video': {'color': 'red', 'icon': 'video-camera'},
        'audio': {'color': 'green', 'icon': 'music'},
        'other': {'color': 'purple', 'icon': 'file'}
    }

    # --- 5. グループ化された場所ごとにマーカーを1つ作成 ---
    for coords, items_at_location in locations.items():
        # ポップアップに表示するHTMLを生成
        popup_html = f"""
        <div style="min-width:200px; max-height:400px; overflow-y:auto;">
            <b>住所:</b> {items_at_location[0].address}<br>
            <hr style="margin: 5px 0;">
        """

        # --- 6. 同じ場所にある全アイテムの情報をループで追加 ---
        for item in items_at_location:
            media_html = ""
            if item.file_type == 'image':
                media_html = f'<img src="{item.file_path}" style="max-width:380px; height:auto; display:block; margin-top:10px;">'
            elif item.file_type == 'video':
                media_html = f'<video controls style="width:100%; max-width:380px; display:block; margin-top:10px;"><source src="{item.file_path}"></video>'
            elif item.file_type == 'audio':
                media_html = f'<audio controls style="width:100%; margin-top:10px;"><source src="{item.file_path}"></audio>'
            
            description_html = f"<b>説明:</b> {item.description}<br>" if item.description else ""
            file_list_url = f"/files/#file-{urllib.parse.quote(item.file_name)}"
            
            # 各アイテムの情報をポップアップに追加
            popup_html += f"""
            <div style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <b>種類:</b> {item.file_type}<br>
                {description_html}
                {media_html}
                <div style="margin-top:10px;">
                    <a href="{file_list_url}" target="_blank" class="btn-view">ファイル一覧で見る</a>
                </div>
            </div>
            """
        
        popup_html += "</div>" # ポップアップのdivを閉じる

        # アイコンは最初のアイテムの種類で決定
        file_type = items_at_location[0].file_type
        setting = icon_settings.get(file_type, icon_settings['other'])
        
        marker = folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=400),
            icon=folium.Icon(color=setting['color'], icon=setting['icon'], prefix='fa')
        )
        marker.add_to(marker_cluster)

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
    file_bytes = local_file.read()
    
    file_options = {"upsert": "true"}
    res = supabase.storage.from_("file-mapping-bucket").upload(
        storage_file_name, file_bytes, file_options
    )
    
    public_url = supabase.storage.from_("file-mapping-bucket").get_public_url(storage_file_name)
    return public_url