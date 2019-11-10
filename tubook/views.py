from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from users.models import Profile
import json
from django_project.settings import BASE_DIR, os, MEDIA_ROOT

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'tubook/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'tubook/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-eventdate']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'tubook/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'eventdate', 'eventplace']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'eventdate', 'eventplace']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'tubook/about.html', {'title': 'About'})

def json_file(request, *args, **kwargs):
    queryset = Post.objects.order_by('-eventdate')
    
    list_of_posts = []
    for query in queryset:
        
        list_of_posts.append({
            'name': Profile.objects.get(id = query.author_id).name,
            'event_name' : query.title,
            'event_date' : query.eventdate.strftime("%d-%m-%Y %H:%M"),
            'event_venue' : query.eventplace, 
            'event_des'  : query.content, 

        })

        with open(os.path.join(MEDIA_ROOT, 'test.json'), 'w') as fout:
            json.dump(list_of_posts , fout)
        
       
    return redirect("/media/test.json")
    