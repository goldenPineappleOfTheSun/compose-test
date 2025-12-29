from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from .models import Image
import json
import os


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'image_preview', 'created_at']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('manage/', self.admin_site.admin_view(self.custom_admin_view), name='gallery_image_manage'),
            path('api/upload/', self.admin_site.admin_view(ImageUploadView.as_view()), name='gallery_image_upload'),
            path('api/update/<int:image_id>/', self.admin_site.admin_view(ImageUpdateView.as_view()), name='gallery_image_update'),
            path('api/delete/<int:image_id>/', self.admin_site.admin_view(ImageDeleteView.as_view()), name='gallery_image_delete'),
        ]
        return custom_urls + urls

    def custom_admin_view(self, request):
        images = Image.objects.all().order_by('-created_at')
        context = {
            **self.admin_site.each_context(request),
            'title': 'Управление изображениями',
            'images': images,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request, None),
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, None),
            'has_delete_permission': self.has_delete_permission(request, None),
        }
        return render(request, 'admin/gallery/image/manage.html', context)

    def changelist_view(self, request, extra_context=None):
        # Перенаправляем на кастомную страницу управления
        return redirect('admin:gallery_image_manage')


@method_decorator(csrf_exempt, name='dispatch')
class ImageUploadView(View):
    def post(self, request):
        try:
            name = request.POST.get('name', '')
            image_file = request.FILES.get('image')
            
            if not image_file:
                return JsonResponse({'error': 'Изображение не загружено'}, status=400)
            
            if not name:
                name = image_file.name
            
            image = Image.objects.create(name=name, image=image_file)
            return JsonResponse({
                'id': image.id,
                'name': image.name,
                'url': image.image.url,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ImageUpdateView(View):
    def post(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
            name = request.POST.get('name', '')
            if name:
                image.name = name
                image.save()
            return JsonResponse({
                'id': image.id,
                'name': image.name,
                'url': image.image.url,
            })
        except Image.DoesNotExist:
            return JsonResponse({'error': 'Изображение не найдено'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ImageDeleteView(View):
    def post(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
            image.delete()
            return JsonResponse({'success': True})
        except Image.DoesNotExist:
            return JsonResponse({'error': 'Изображение не найдено'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


admin.site.site_header = "Галерея изображений"
admin.site.site_title = "Админка галереи"
admin.site.index_title = "Управление галереей"
