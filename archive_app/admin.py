from django.contrib import admin
from .models import UploadedItem


@admin.register(UploadedItem)
class UploadedItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'file_name',
        'file_type',
        'address',
        'latitude',
        'longitude',
        'upload_date',
    )
    list_filter = ('file_type', 'upload_date')
    search_fields = ('file_path', 'description', 'address')
    readonly_fields = ('upload_date',)

    def file_name(self, obj):
        import os
        return os.path.basename(obj.file_path)

    file_name.short_description = 'File Name'
