import random
import string
from django.urls import reverse
from ..models import Post

def generate_short_code(length=6):
    """Benzersiz bir kısa kod üretir."""
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        if not Post.objects.filter(link=f"rmp/{code}").exists():
            return code

def create_short_link(post, long_url):
    """Post için kısa link üretir ve kaydeder."""
    if long_url and not post.link:
        short_code = generate_short_code()
        post.link = f"rmp/{short_code}"
        post.original_link = long_url
        post.save()
    return post.link

def resolve_short_link(short_code):
    """Kısa kodu post detay URL'sine çevirir."""
    try:
        post = Post.objects.get(short_id=short_code)
        return reverse('post_detail', kwargs={'pk': post.id})
    except Post.DoesNotExist:
        return None