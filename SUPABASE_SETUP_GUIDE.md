# Supabase セットアップガイド

このガイドでは、DjangoアプリケーションをSupabaseと統合する手順を説明します。

## 1. Supabaseプロジェクトの作成

### 1.1 Supabaseアカウントの作成
1. [Supabase](https://supabase.com)にアクセス
2. GitHubまたはGoogleアカウントでサインアップ
3. 新しいプロジェクトを作成

### 1.2 プロジェクト設定
1. プロジェクト名を入力（例：`file-mapping-app`）
2. データベースパスワードを設定（重要：忘れないようにメモ）
3. リージョンを選択（日本なら`Asia Pacific (Tokyo)`推奨）
4. プロジェクトを作成

## 2. データベース接続情報の取得

### 2.1 接続情報の確認
1. プロジェクトダッシュボードで「Settings」→「Database」をクリック
2. 「Connection string」セクションで以下を確認：
   - Host: `db.[PROJECT-REF].supabase.co`
   - Database name: `postgres`
   - Port: `5432`
   - User: `postgres`
   - Password: プロジェクト作成時に設定したパスワード

### 2.2 DATABASE_URLの構築
```
postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

## 3. 環境変数の設定

### 3.1 ローカル開発環境
1. プロジェクトルートに`.env`ファイルを作成
2. 以下の内容を追加：

```env
# Django Settings
SECRET_KEY=django-insecure-j%)np(faguein(=1bu!4&8hx4#+rrp7g6+_+(w1zch)(00d6gn
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Supabase Database Configuration
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Optional: Supabase API Keys (if you want to use Supabase Auth or Storage)
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### 3.2 本番環境（Heroku等）
環境変数として設定：
```bash
heroku config:set DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
heroku config:set DEBUG=False
```

## 4. データベースマイグレーション

### 4.1 ローカル開発
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4.2 本番環境
```bash
heroku run python manage.py migrate
```

## 5. アプリケーションの起動

### 5.1 ローカル開発
```bash
python manage.py runserver
```

### 5.2 本番環境
```bash
git push heroku main
```

## 6. トラブルシューティング

### 6.1 接続エラー
- ファイアウォールの設定を確認
- SupabaseプロジェクトのIP制限を確認
- 接続文字列の形式を確認

### 6.2 認証エラー
- データベースパスワードを確認
- Supabaseプロジェクトの設定を確認

## 7. セキュリティ注意事項

- `.env`ファイルをGitにコミットしない
- 本番環境では`DEBUG=False`に設定
- 強力なパスワードを使用
- 定期的にパスワードを変更

## 8. 追加機能（オプション）

### 8.1 Supabase Storage
ファイルストレージとしてSupabase Storageを使用する場合：
1. SupabaseプロジェクトでStorageを有効化
2. バケットを作成
3. 適切な権限を設定

### 8.2 Supabase Auth
認証システムとしてSupabase Authを使用する場合：
1. SupabaseプロジェクトでAuthを有効化
2. 認証設定を構成
3. Djangoアプリケーションと統合 