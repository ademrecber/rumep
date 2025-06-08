from django.contrib import admin
from main.models import Post, Profile, Comment, PostVote, CommentVote, Category, Critique, CritiqueVote

admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(PostVote)
admin.site.register(CommentVote)
admin.site.register(Category)
admin.site.register(Critique)
admin.site.register(CritiqueVote)