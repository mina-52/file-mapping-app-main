import pandas as pd
import os
import folium
from folium.plugins import MarkerCluster

import os
CSV_FILE = os.path.join(os.path.dirname(__file__), 'data', 'uploaded_data.csv')
CSV_COLUMNS = ['file_path', 'file_type', 'address', 'latitude', 'longitude']

def add_data_to_csv(data: dict):
    """
    受け取ったデータをCSVファイルに追記する。
    """
    df_new = pd.DataFrame([data])
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, index=False, header=True, encoding='utf-8-sig')
    else:
        df_new.to_csv(CSV_FILE, mode='a', index=False, header=False, encoding='utf-8-sig')

def get_dataframe_from_csv() -> pd.DataFrame:
    """
    CSVファイルからデータを読み込み、pandasデータフレームとして返す。
    """
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=CSV_COLUMNS)
    return pd.read_csv(CSV_FILE)

def create_map_html() -> str:
    """
    データフレームからfoliumの地図を生成し、HTML文字列として返す。
    """
    df = get_dataframe_from_csv()

    # データがあればその平均位置を、なければ日本の中心あたりを初期表示
    if not df.empty and df['latitude'].notna().any():
        map_center = [df['latitude'].mean(), df['longitude'].mean()]
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
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            
            file_type = row['file_type']
            file_name = os.path.basename(row['file_path'])
            file_url = f"/media/{file_name}"

            media_html = ""
            if file_type == 'image':
            # 画像を表示する<img>タグ
                media_html = f'<img src="{file_url}" style="max-width:380px; height:auto; display:block; margin-top:10px;">'
            elif file_type == 'video':
            # 動画プレーヤーを表示する<video>タグ
                media_html = f'<video controls style="width:100%; max-width:380px; display:block; margin-top:10px;"><source src="{file_url}"></video>'
            elif file_type == 'audio':
            # 音声プレーヤーを表示する<audio>タグ
                media_html = f'<audio controls style="width:100%; margin-top:10px;"><source src="{file_url}"></audio>'
        
            # ポップアップ全体のHTMLを組み立て
            popup_html = f"""
            <div style="min-width:150px;">
                <b>住所:</b> {row['address']}<br>
                <b>種類:</b> {file_type}
            
                {media_html}
            
                <div style="margin-top:10px; display:flex; justify-content:space-between;">
                    <a href="{file_url}" download="{file_name}">ダウンロード</a>
                    <a href="{file_url}" target="_blank">別タブで開く</a>
                </div>
            </div>
            """
            
            # アイコンの設定を取得
            setting = icon_settings.get(row['file_type'], icon_settings['other'])
            
            marker = folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=400),
                icon=folium.Icon(color=setting['color'], icon=setting['icon'], prefix='fa')
            )
            
            #マーカーを marker_cluster に追加する
            marker.add_to(marker_cluster)

    return m._repr_html_()

# get_dataframe_from_csv(), os, pd などは別途インポート・定義されている必要があります。
