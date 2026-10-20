from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.urls import reverse
from .models import SportPost


@require_GET
def feed_api(request):
    try:
        page = int(request.GET.get('page', '1'))
        before = int(request.GET.get('before', '0'))
        if page < 1 or page > 10000 or before < 0:
            raise ValueError
    except ValueError:
        return JsonResponse({'detail': 'Invalid pagination'}, status=400)
    rows = SportPost.objects.filter(is_published=True, published_at__lte=timezone.now())
    if request.GET.get('post'):
        try:
            rows = rows.filter(pk=int(request.GET['post']))
        except ValueError:
            return JsonResponse({'detail': 'Invalid post'}, status=400)
    if before:
        rows = rows.filter(pk__lte=before)
    anchor = before or (rows.order_by('-pk').values_list('pk', flat=True).first() or 0)
    records = list(rows.filter(pk__lte=anchor).prefetch_related('extra_images').order_by('-published_at', '-pk')[(page-1)*10:page*10+1])
    items = [{
        'id': p.pk, 'description': p.description,
        'imageUrl': request.build_absolute_uri(reverse('spor_feed_image', args=[p.pk, 'original'])),
        'thumbnailUrl': request.build_absolute_uri(reverse('spor_feed_image', args=[p.pk, 'preview'])),
        'width': p.width, 'height': p.height,
        'images': [{
            'imageUrl': request.build_absolute_uri(reverse('spor_feed_extra_image', args=[p.pk, im.pk, 'original'])),
            'thumbnailUrl': request.build_absolute_uri(reverse('spor_feed_extra_image', args=[p.pk, im.pk, 'preview'])),
            'width': im.width, 'height': im.height, 'updatedAt': im.updated_at.isoformat(),
        } for im in p.extra_images.all()[:9]],
        'publishedAt': p.published_at.isoformat(), 'updatedAt': p.updated_at.isoformat(),
    } for p in records[:10]]
    response = JsonResponse({'items': items, 'page': page, 'before': anchor, 'hasMore': len(records) > 10})
    response['Cache-Control'] = 'public, max-age=30'
    return response


@require_GET
def feed_image(request, pk, variant):
    post = get_object_or_404(SportPost, pk=pk, is_published=True, published_at__lte=timezone.now())
    image = post.thumbnail if variant == 'preview' and post.thumbnail else post.image
    response = HttpResponseRedirect(image.url)
    response['Cache-Control'] = 'no-store'
    return response


@require_GET
def feed_extra_image(request, pk, image_pk, variant):
    from .models import SportPostImage
    image = get_object_or_404(SportPostImage, pk=image_pk, post_id=pk, post__is_published=True, post__published_at__lte=timezone.now())
    file = image.thumbnail if variant == 'preview' and image.thumbnail else image.image
    response = HttpResponseRedirect(file.url)
    response['Cache-Control'] = 'no-store'
    return response
