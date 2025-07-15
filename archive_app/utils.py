# map_app/utils.py などに作成
import requests
import urllib.parse

def geocode_address(address: str) -> tuple[float | None, float | None]:
    """
    国土地理院APIを使い、住所文字列を緯度・経度に変換する。

    Args:
        address: 変換したい住所文字列。

    Returns:
        (緯度, 経度) のタプル。失敗した場合は (None, None)。
    """
    encoded_address = urllib.parse.quote(address)
    url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={encoded_address}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーの場合に例外を発生させる
        data = response.json()
        if data and len(data) > 0:
            # APIのレスポンスは [経度, 緯度] の順なので注意
            lon, lat = data[0]["geometry"]["coordinates"]
            return lat, lon
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
    except (KeyError, IndexError):
        print("レスポンスの形式が不正です。")

    return None, None