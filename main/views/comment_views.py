from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from ..models import Comment
from .base import profile_required
import logging

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@login_required
@profile_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        post_id = comment.post.id
        comment.delete()
        logger.debug(f"Yorum silindi, comment_id: {comment_id}, post_id: {post_id}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'comment_id': str(comment_id)})
        return redirect('post_detail', pk=post_id)
    logger.warning(f"Yetkisiz yorum silme denemesi, user: {request.user.username}, comment_id: {comment_id}")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Yetkisiz işlem'}, status=403)
    return HttpResponseForbidden('Yetkisiz işlem')

def build_comment_tree(comments):
    comment_dict = {comment.id: comment for comment in comments}
    tree = []
    for comment in comments:
        if not hasattr(comment, 'children'):
            comment.children = []
        if comment.parent_id and comment.parent_id in comment_dict:
            parent = comment_dict[comment.parent_id]
            if not hasattr(parent, 'children'):
                parent.children = []
            parent.children.append(comment)
        else:
            tree.append(comment)
    return tree