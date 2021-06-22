from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .forms import ContactForm
from django.shortcuts import render,redirect, get_object_or_404
from .models import Post, Area, Attraction, Category, Like
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from functools import reduce
from operator import and_
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class IndexView(View):
    def paginate_queryset(self, request, queryset, count):
        paginator = Paginator(queryset, count)
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        # page_obj:全体何ページ中のXページ目かを定義
        return page_obj
# エリア選択
    def area_select(self, post_data, category, area, attraction):
        if area == "all" :
            post_data = post_data
        elif area != None :
            area_data = Area.objects.get(slug=area)
            post_data = post_data.filter(area=area_data)
        return post_data
# アトラクション選択
    def attraction_select(self, post_data, category, area, attraction):
        if attraction == "all" :
            post_data = post_data
        elif attraction != None :
            attraction_data = Attraction.objects.get(slug=attraction)
            post_data = post_data.filter(attraction=attraction_data)
        elif attraction is None :
            post_data = post_data
        return post_data
        # カテゴリ選択
    def category_select(self, post_data, category, area, attraction):
        if category == "all" :
            post_data = post_data
        elif category != None :
            category_data = Category.objects.get(slug=category)
            post_data = post_data.filter(category=category_data)
        elif category is None :
            post_data = post_data
        return post_data
    
    # def postcount(self, request, *args, **kwargs):
    #     counted_posts = Post.objects.count()
    #     print(counted_posts)

    def get(self, request, *args, **kwargs):
        post_data = Post.objects.filter(public=True).order_by("-id")
        area = self.kwargs.get('area')
        category = self.kwargs.get('category')
        attraction = self.kwargs.get('attraction')
        print(area)
        print(category)
        print(attraction)
        post_data = self.area_select(post_data, category, area, attraction)
        post_data = self.attraction_select(post_data, category, area, attraction)
        post_data = self.category_select(post_data, category, area, attraction)
        page_obj = self.paginate_queryset(request, post_data, 10)
        # for post in post_data:
        #     print(type(post.category))

        return render(request, 'app/index.html', {
            'post_data': page_obj.object_list,
            'page_obj': page_obj,
            'area': area,
            'attraction': attraction,
            'category': category,
        })


class PostDetailView(View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        liked_list = []

        if request.user.is_authenticated:
            liked = post_data.like_set.filter(author=request.user)
        else:
            liked = post_data.like_set.all()
    
        if liked.exists():
            liked_list.append(post_data.id)
    

        return render(request, 'app/post_detail.html', {
            'post_data': post_data,
            'liked_list': liked_list,
        })

class CreatePostView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)
        return render(request, 'app/post_form.html', {
            'form': form
        })
    
    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)

        if form.is_valid():
            post_data = Post()
            post_data.author = request.user
            post_data.title = form.cleaned_data['title']
            area = form.cleaned_data['area']
            post_data.area = Area.objects.get(name=area)
            attraction = form.cleaned_data['attraction']
            post_data.attraction = Attraction.objects.get(name=attraction)
            category = form.cleaned_data['category']
            post_data.category = Category.objects.get(name=category)
            post_data.content = form.cleaned_data['content']
            if request.FILES:
                post_data.image = request.FILES.get('image')
            post_data.save()
            # show = False
        # 120-125まで一時的に
        #     return redirect('post_detail', post_data.id)

        # return render(request, 'app/post_form.html', {
        #     'form': form
        # })
            return render(request, 'app/post_preview.html', {
                'post_data' : post_data
            })

    # 以下コードはformのvalidationが失敗したとき
        # return render(request, 'app/post_form.html', {
        return render(request, 'app/index.html', {
            'form': form
        })

class PreviewPostView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # POSTのPOST（データ入力フォームに記載された情報）の中身をリクエストして表示している。
        # print(request.POST)
        post_data = Post()
        area = request.POST.get('area')
        post_data.area = Area.objects.get(name=area)
        attraction = request.POST.get('attraction')
        post_data.attraction = Attraction.objects.get(name=attraction)
        category = request.POST.get('category')
        post_data.category = Category.objects.get(name=category)
        # request.userでログインユーザー情報を入手できる。
        post_data.author = request.user
        post_data.content = request.POST.get('content')
        post_data.image = request.POST.get('image')
        if request.FILES:
            post_data.image = request.FILES.get('image')
        post_data.title = request.POST.get('title')
        post_data.public = True
        post_data.save()
        # show = not False
        return redirect('index')

class PostEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        form = PostForm(
            request.POST or None,
            initial={
                'title': post_data.title,
                'area': post_data.area,
                'attraction': post_data.attraction,
                'category': post_data.category,
                'content': post_data.content,
                'image': post_data.image,
            }
        )

        return render(request, 'app/post_form.html', {
            'form': form
        })
    
    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST or None)
        if form.is_valid():
            post_data = Post.objects.get(id=self.kwargs['pk'])
            post_data.title = form.cleaned_data['title']
            area = form.cleaned_data['area']
            area_data = Area.objects.get(name=area)
            post_data.area = area_data
            attraction = form.cleaned_data['attraction']
            attraction_data = Attraction.objects.get(name=attraction)
            post_data.attraction = attraction_data
            category = form.cleaned_data['category']
            category_data = Category.objects.get(name=category)
            post_data.category = category_data
            post_data.content = form.cleaned_data['content']
            if request.FILES:
                post_data.image = request.FILES.get('image')
            post_data.public = True
            post_data.save()
            return redirect('post_detail', self.kwargs['pk'])

        return render(request, 'app/post_form.html', {
            'form': form
        })

class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        return render(request, 'app/post_delete.html', {
            'post_data': post_data
        })

    def post(self, request, *args, **kwargs):
        post_data = Post.objects.get(id=self.kwargs['pk'])
        post_data.delete()
        return redirect('index')

# class AreaView(View):
#     def get(self, request, *args, **kwargs):
#         area_data = Area.objects.get(name=self.kwargs['area'])
#         post_data = Post.objects.order_by('-id').filter(area=area_data)
#         return render(request, 'app/index.html', {
#             'post_data': post_data
#         })

# class AttractionView(View):
#     def get(self, request, *args, **kwargs):
#         attraction_data = Attraction.objects.get(name=self.kwargs['attraction'])
#         post_data = Post.objects.order_by('-id').filter(attraction=attraction_data)
#         return render(request, 'app/index.html', {
#             'post_data': post_data
#         })

# class CategoryView(View):
#     def get(self, request, *args, **kwargs):
#         category = self.kwargs.get('category')
#         post_data = Category.objects.get(name=self.kwargs['category'])
#         return render(request, 'app/index.html', {
#             'post_data': post_data
#         })

class AboutView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app/about.html')

# class MypageView(View):
#     def paginate_queryset(self, request, queryset, count):
#         paginator = Paginator(queryset, count)
#         page = request.GET.get('page')
#         try:
#             page_obj = paginator.page(page)
#         except PageNotAnInteger:
#             page_obj = paginator.page(1)
#         except EmptyPage:
#             page_obj = paginator.page(paginator.num_pages)
#         return page_obj

#     def get(self, request, *args, **kwargs):
#         like_data = Like.objects.order_by('-id').filter(author=request.user)
#         mypost_data = Post.objects.order_by('-id').filter(author=request.user)
        
#         page_obj_like = self.paginate_queryset(request, like_data, 3)
#         page_obj_mypost = self.paginate_queryset(request, mypost_data, 5)
        
#         return render(request, 'app/mypage.html', {
#             'like_data': page_obj_like.object_list,
#             'mypost_data': page_obj_mypost.object_list,
#             'page_obj_like': page_obj_like,
#             'page_obj_mypost': page_obj_mypost
#         })

class FavoriteView(View):
    def paginate_queryset(self, request, queryset, count):
        paginator = Paginator(queryset, count)
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get(self, request, *args, **kwargs):
        like_data = Like.objects.order_by('-id').filter(author=request.user)
        mypost_data = Post.objects.order_by('-id').filter(author=request.user)
        
        page_obj_like = self.paginate_queryset(request, like_data, 3)
        page_obj_mypost = self.paginate_queryset(request, mypost_data, 5)
        
        return render(request, 'app/favorite.html', {
            'like_data': page_obj_like.object_list,
            'mypost_data': page_obj_mypost.object_list,
            'page_obj_like': page_obj_like,
            'page_obj_mypost': page_obj_mypost
        })
class MyPostView(View):
    def paginate_queryset(self, request, queryset, count):
        paginator = Paginator(queryset, count)
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get(self, request, *args, **kwargs):
        like_data = Like.objects.order_by('-id').filter(author=request.user)
        mypost_data = Post.objects.order_by('-id').filter(author=request.user)
        
        page_obj_like = self.paginate_queryset(request, like_data, 3)
        page_obj_mypost = self.paginate_queryset(request, mypost_data, 5)
        
        return render(request, 'app/mypost.html', {
            'like_data': page_obj_like.object_list,
            'mypost_data': page_obj_mypost.object_list,
            'page_obj_like': page_obj_like,
            'page_obj_mypost': page_obj_mypost
        })


class CategoryNameView(View):
    def get(self, request, *args, **kwargs):
        #self.kwargsでurlから値を取得する
        # path('category/<str:category>/'の<str:category>に動的に入る値を獲得する
        # inputボタンは押してないので、.getは不要
        category_data = Category.objects.get(name=self.kwargs['category'])
        post_data = Post.objects.filter(category=category_data)
        return render(request, 'app/index.html', {
            'post_data' : post_data
        })

class SearchView(View):
    def get(self, request, *args, **kwargs):
        post_data = Post.objects.order_by('-id')
        keyword = request.GET.get('keyword')

        if keyword:
            exclusion_list = set([' ', ' '])
            query_list = ''
            for word in keyword:
                if not word in exclusion_list:
                    # スペースを除いたリストを抽出
                    query_list += word
            # Qオブジェクトを使用して、投稿データをキーワードでフィルターがけする。キーワードをQオブジェクトでor検索
            query = reduce(and_, [Q(title__icontains=q) | Q(content__icontains=q) for q in query_list])
            post_data = post_data.filter(query)
        
        return render(request, 'app/search.html', {
            'keyword' : keyword,
            'post_data' : post_data
        })

def LikeView(request):
    if request.method =="POST":
        if request.user.is_authenticated:
            post = get_object_or_404(Post, pk=request.POST.get("post_id"))
            user = request.user
            liked = False
            like = Like.objects.filter(post=post, author=user)
            if like.exists():
                like.delete()
            else:
                like.create(post=post, author=user)
                liked = True
            
            context={
                'post_id': post.id,
                'liked': liked,
                'count': post.like_set.count(),
            }

            if request.is_ajax():
                return JsonResponse(context)
        # elifでlikeボタン押下後、サインアップ画面に誘導させることは可能

class ContactFormView(FormView):
    template_name = 'app/contact_form.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact_result')

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)

class ContactResultView(TemplateView):
    template_name = 'app/contact_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = "お問い合わせは正常に送信されました。"
        return context

