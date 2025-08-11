from django.db import models


class UploadedItem(models.Model):
    """DBに保存するアップロード項目のメタデータ。CSVの列構成に合わせたモデル。"""

    class FileType(models.TextChoices):
        IMAGE = 'image', '画像'
        VIDEO = 'video', '動画'
        AUDIO = 'audio', '音声'
        OTHER = 'other', 'その他'

    file_path = models.URLField(max_length=1000)
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        default=FileType.OTHER,
    )
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['file_type', 'upload_date'])
        ]

    def __str__(self) -> str:
        import os
        return os.path.basename(self.file_path)
