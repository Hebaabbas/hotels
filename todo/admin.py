from django.contrib import admin
from .models import CustomUser, Hotel, Post, Comment, Reaction, Review
from django_summernote.admin import SummernoteModelAdmin
from django import forms
from todo.models import CustomUser


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'

# Admin configuration for the Post model
@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'post_date', 'user', 'hotel')
    search_fields = ['title', 'content']
    list_filter = ('post_date', 'user')
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)
    # Custom save method to automatically assign the current user if not set
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

# Admin configuration for CustomUser model
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'firstname', 'lastname', 'is_staff','is_superuser']
    search_fields = ['username', 'email', 'firstname', 'lastname']
    list_filter = ['is_staff','is_superuser']

# Admin configuration for Hotel model
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'city', 'average_rating')
    search_fields = ['name', 'country', 'city']
    list_filter = ('country', 'city')

# Admin configuration for Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'post', 'comment_date')
    list_filter = ('comment_date', 'user')
    search_fields = ('user__username', 'content')

# Admin configuration for Reaction model
@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'is_thumb_up')
    list_filter = ('is_thumb_up', 'user')
    search_fields = ('user__username', 'post__title')

# Admin configuration for Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'user', 'review_date', 'content', 'room_type', 'duration', 'spa', 'breakfast')
    list_filter = ('hotel', 'user', 'review_date', 'spa', 'breakfast')
    search_fields = ('user__username', 'hotel__name', 'content')
