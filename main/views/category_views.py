from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from ..models import Category, Topic

def categories(request):
    categories = Category.objects.all().order_by('name')
    
    # Her kategori için topic sayısını hesapla
    for category in categories:
        category.topic_count = category.topics.count()
    
    return render(request, 'main/categories.html', {
        'categories': categories,
        'user': request.user
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    topics = Topic.objects.filter(categories=category).order_by('-updated_at')
    all_categories = Category.objects.all().order_by('name')

    # Kategori için topic sayısını hesapla
    category.topic_count = topics.count()
    
    # Sayfalama
    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'main/category_detail.html', {
        'category': category,
        'topics': page_obj,
        'all_categories': all_categories,
        'user': request.user
    })