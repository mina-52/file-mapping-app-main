# map_app/utils.py などに作成
import requests
import urllib.parse

def geocode_address(address):
    """
    住所を緯度・経度に変換する（ジオコーディング）
    """
    try:
        # 地理院APIを使用
        url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + address
        response = requests.get(url)
        data = response.json()
        
        if data and len(data) > 0:
            # 最初の結果を使用
            coordinates = data[0]['geometry']['coordinates']
            # 地理院APIは[経度, 緯度]の順で返すので、順序を入れ替える
            return coordinates[1], coordinates[0]  # 緯度, 経度
        else:
            return None, None
    except Exception as e:
        print(f"ジオコーディングエラー: {e}")
        return None, None

def reverse_geocode(lat, lon):
    """
    緯度・経度を住所に変換する（逆ジオコーディング）
    """
    try:
        # 地理院APIを使用して逆ジオコーディング
        url = f"https://mreverse.gsi.go.jp/reverse-geocode/cgi-bin/reversegeocode.cgi?lat={lat}&lon={lon}&zoom=18&format=json"
        response = requests.get(url)
        data = response.json()
        
        if data and 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            # 住所を組み立て
            address_parts = []
            if 'municipality' in result:
                address_parts.append(result['municipality'])
            if 'localAddress' in result:
                address_parts.append(result['localAddress'])
            
            if address_parts:
                return ' '.join(address_parts)
            else:
                return f"緯度: {lat}, 経度: {lon}"
        else:
            return f"緯度: {lat}, 経度: {lon}"
    except Exception as e:
        print(f"逆ジオコーディングエラー: {e}")
        return f"緯度: {lat}, 経度: {lon}"