from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView,RedirectView
from .models import Post
from .forms import  CommentForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger




def home(request):
     posts=Post.objects.all()
     
     
     
     return render(request,'blog/home.html',{
        'posts' :posts
     })

class PostListView(ListView):
    model= Post
    template_name='blog/home.html'
    context_object_name = 'posts'
    ordering=['-date_posted']
    paginate_by=2
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            object_list = self.model.objects.filter(title__icontains=query)
            paginator = Paginator(object_list, self.paginate_by)
            

        else:
            object_list = self.model.objects.all()
            paginator = Paginator(object_list, self.paginate_by)
            

       

        
        return object_list
    
    
    

class UserPostListView(ListView):
    model= Post
    template_name='blog/user_posts.html'
    context_object_name = 'posts'
    
    paginate_by=2

    def get_queryset(self):
        user = get_object_or_404(User , username=self.kwargs.get('username')) 
        return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
    model= Post

class PostCreateView(LoginRequiredMixin,CreateView):
    model= Post
    fields=[ 'title','content']
    def form_valid(self,form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model= Post
    fields=[ 'title','content']
    def form_valid(self,form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    def test_func(self):
        post=self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model= Post
   
    success_url='/'
    def test_func(self):
        post=self.get_object()
        if self.request.user == post.author:
            return True
        return False

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post-detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

#def searchposts(request):
#    if request.method == 'GET':
#        query= request.GET.get('q')

#        submitbutton= request.GET.get('submit')

#        if query is not None:
#            lookups= Q(title__icontains=query) | Q(content__icontains=query)

#            results= Post.objects.filter(lookups).distinct()

#            context={'results': results,
#                     'submitbutton': submitbutton}

#            return render(request, 'blog/search.html', context)

#        else:
#            return render(request, 'blog/home.html')

#    else:
#        return render(request, 'blog/home.html')


#class QSearchBooks(ListView):
#    template_name = 'blog/home.html'
#    def get_queryset(self):
#        val = self.kwargs.get("qurlsearch")
#        if val:
#            queryset = Post.objects.filter(
#                Q(title__icontains=val)|
#                Q(author__first_name__icontains=val)  # | is or
#            ).distinct()
#            # distinct is used, otherwise same book will be listed
#            # twice if book has two authors
#            queryset = queryset.distinct()
#        else:
#            queryset = Post.objects.all()
#        return queryset


def search_list(request):
    posts=Post.objects.all()
    
    query=request.GET.get("q")
    if query :
        posts= posts.filter(
            Q(title__icontains=query)|
            Q(content__icontains=query)|
            Q(author__username__icontains=query)
            ).distinct()
    paginator=Paginator(posts,2)
    page_request_var="page"
    page=request.GET.get(page_request_var)
    queryset=paginator.get_page(page)
    return render(request,'blog/search.html',{
        'posts':posts.order_by('-date_posted')
        })


   # post = get_object_or_404(Post, id=request.POST.get('post_id'))
  #  post.likes.add(request.user)
   # return render(post.get_absolute_url())

def about(request):
     return render(request,'blog/about.html',{'title':'About'})