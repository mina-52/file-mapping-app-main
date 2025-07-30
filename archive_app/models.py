# archive_app/models.py

from django.db import models
from django.utils import timezone # 日付を扱うために追加

class Archive(models.Model):
    # ファイルの種類（画像、動画など）
    file_type = models.CharField(max_length=50)
    
    # Supabase上のファイルパス（公開URL）
    file_path = models.URLField(max_length=1024)

    # 説明文
    description = models.TextField(blank=True, null=True) 

    # 住所
    address = models.CharField(max_length=255)

    # 緯度
    latitude = models.FloatField()

    # 経度
    longitude = models.FloatField()
    
    # 登録日（自動で現在日時が記録される）
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        # 管理サイトなどで表示されるときの名前
        return f"{self.description[:20]} at {self.address}"

# Create your models here.
