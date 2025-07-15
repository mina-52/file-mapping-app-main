# 📍 ファイルマッピングアプリ

ファイルと位置情報を地図上で管理できるWebアプリケーションです。

## ✨ 機能

- 📁 **ファイルアップロード**: 画像、動画、音声ファイルのアップロード
- 🗺️ **位置情報管理**: 住所を入力して地図上にマーカー表示
- 🎯 **インタラクティブマップ**: Foliumを使用した美しい地図表示
- 📱 **レスポンシブデザイン**: スマホ・タブレット・PCに対応
- 🎨 **モダンUI**: 美しいグラデーションとアニメーション

## 🚀 デモ

![アプリのスクリーンショット](demo-screenshot.png)

## 🛠️ 技術スタック

- **Backend**: Django 5.2.4
- **Frontend**: HTML5, CSS3, JavaScript
- **地図**: Folium (Leaflet.js)
- **データ処理**: Pandas
- **ジオコーディング**: 国土地理院API

## 📦 インストール

### 前提条件
- Python 3.11以上
- pip

### セットアップ手順

1. **リポジトリのクローン**
```bash
git clone https://github.com/yourusername/file-mapping-app.git
cd file-mapping-app
```

2. **仮想環境の作成とアクティベート**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

4. **データベースのマイグレーション**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **開発サーバーの起動**
```bash
python manage.py runserver
```

6. **ブラウザでアクセス**
```
http://127.0.0.1:8000/
```

## 📁 プロジェクト構造

```
file-mapping-app/
├── archive_app/                 # メインアプリケーション
│   ├── static/                  # 静的ファイル
│   │   └── archive_app/
│   │       └── css/
│   │           └── style.css    # メインCSS
│   ├── templates/               # HTMLテンプレート
│   │   └── archive_app/
│   │       └── index.html       # メインページ
│   ├── data/                    # データファイル
│   ├── forms.py                 # フォーム定義
│   ├── services.py              # ビジネスロジック
│   ├── utils.py                 # ユーティリティ関数
│   └── views.py                 # ビュー関数
├── archive_project/             # Djangoプロジェクト設定
│   ├── settings.py              # 開発環境設定
│   ├── settings_production.py   # 本番環境設定
│   └── urls.py                  # URL設定
├── media/                       # アップロードされたファイル
├── requirements.txt             # Python依存関係
├── Procfile                     # Herokuデプロイ設定
└── README.md                    # このファイル
```

## 🌐 デプロイ

### Herokuでのデプロイ

1. **Herokuアカウント作成**
   - [Heroku](https://heroku.com) でアカウントを作成

2. **Heroku CLIのインストール**
   ```bash
   # Windows
   winget install --id=Heroku.HerokuCLI
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

3. **Herokuにログイン**
   ```bash
   heroku login
   ```

4. **アプリの作成**
   ```bash
   heroku create your-app-name
   ```

5. **PostgreSQLアドオンの追加**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

6. **環境変数の設定**
   ```bash
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```

7. **デプロイ**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

8. **データベースのマイグレーション**
   ```bash
   heroku run python manage.py migrate
   ```

## 🔧 設定

### 環境変数

- `DEBUG`: デバッグモード（True/False）
- `ALLOWED_HOSTS`: 許可されたホスト（カンマ区切り）
- `DATABASE_URL`: データベースURL（Heroku自動設定）

### カスタマイズ

- **地図の初期位置**: `services.py`の`create_map_html()`関数で変更
- **ファイルサイズ制限**: `settings.py`で`DATA_UPLOAD_MAX_MEMORY_SIZE`を設定
- **対応ファイル形式**: `forms.py`の`choices`で変更

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

- [Django](https://www.djangoproject.com/) - Webフレームワーク
- [Folium](https://python-visualization.github.io/folium/) - 地図ライブラリ
- [国土地理院](https://maps.gsi.go.jp/) - 地図タイルとジオコーディングAPI
- [Font Awesome](https://fontawesome.com/) - アイコン

## 📞 サポート

問題や質問がある場合は、[Issues](https://github.com/yourusername/file-mapping-app/issues)でお知らせください。

---

⭐ このプロジェクトが役に立ったら、スターを付けてください！ 