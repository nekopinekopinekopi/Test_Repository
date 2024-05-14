from django.shortcuts import render
from django.views.generic.base import (
    View, TemplateView, RedirectView,
)
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView,
    FormView
)
from . import forms
from datetime import datetime
from .models import Books, Pictures
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin







class IndexView(View):
    
    def get(self, request, *args, **kwargs):
        book_form = forms.BookForm()
        return render(request, 'index.html', context={
            'book_form': book_form
        })
        
    def post(self, request, *args, **kwargs):
        book_form = forms.BookForm(request.POST or None)
        if book_form.is_valid():
            book_form.save()
        return render(request, 'index.html', context={
            'book_form': book_form, 
        })
        

class HomeView(TemplateView):  # このクラスを使って、htmlを表示させるやり方
    
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):  # context={}のように値を渡して動的にページを変えたい場合の関数
        context = super().get_context_data(**kwargs)
        # print(kwargs)  # ←辞書型としてkwargsが取り出されているのが分かるよ
        context['name'] = kwargs.get('name')  # urlでname部分に名前を入れると、urls.py->このviews.pyの[]に格納されて->home.htmlに渡される
        context['time'] = datetime.now()  # []で囲んだ値がhtmlに渡される値
        return context
    
    
    
##############################################3
# BooksモデルのPK（id）ごとに詳細を表示するクラス

class BookDetailView(DetailView):
    model = Books
    template_name = 'book.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        # context['form'] = forms.BookForm()  # あくまで例ですが、このように詳細画面と一緒に入力フォームを表示することも可能ですよとのこと。
        return context
        


##############################################
# モデルのデータの一覧を表示する

class BookListView(ListView):
    model = Books
    template_name = 'book_list.html'
    
    def get_queryset(self):
        qs = super(BookListView, self).get_queryset()
        if 'name' in self.kwargs:
            qs = qs.filter(name__startswith=self.kwargs['name'] )  # urls.pyで引数をとってkwargs部分に代入するのでname部分に本の名前をurlで入力するとその本だけを表示する
        # qs = qs.filter(name__startswith='Book')  # nameがBookで始まるものだけを表示する
        qs = qs.order_by('description')  # ()の中身を基準に並び替えができる
        print(qs)
        return qs
    
    
    
    
##############################################
# 作成したテーブルにデータを挿入したい場合に用いる

class BookCreateView(CreateView):
    model = Books
    fields = ['name', 'description', 'price']
    template_name = 'add_book.html'
    success_url = reverse_lazy('store:list_books')  # CreateViewだけのかな？urlの遷移方法(ridirectみたいなやつ)
    # ↑こちらの方がget_absolute_urlメソッドよりも優先される
    
    # Booksモデルのcreate_atがNULLではまずいので処理を追加する
    def form_valid(self, form):  # form送信処理の前に実行されるメソッド
        form.instance.create_at = datetime.now()
        form.instance.update_at = datetime.now()
        return super(BookCreateView, self).form_valid(form)
    
    # 初期値を変えてる
    def get_initial(self, **kwargs):  
        initial = super(BookCreateView, self).get_initial(**kwargs)
        initial['name'] = 'sample'  # add_book画面でnameにsampleが入っている状態になる
        return initial



# 挿入したデータを更新したい場合に用いる
class BookUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'update_book.html'
    model = Books
    form_class = forms.BookUpdateForm
    success_message = '更新に成功しました'  # 静的にサクセスメッセージを表示してる

    # ↓これがなければ、models.pyのget_absolute_urlメソッドが使われる
    def get_success_url(self):
        print(self.object)
        return reverse_lazy('store:edit_book', kwargs={'pk': self.object.id})
    
    def get_success_message(self, cleaned_data):  # 動的にサクセスメッセージを表示してる
        print(cleaned_data)
        return cleaned_data.get('name') + 'を更新しました'


    # 写真をここでアップロードできるように定義した関数
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        picture_form = forms.PictureUploadForm()
        pictures = Pictures.objects.filter_by_book(book=self.object)
        context['pictures'] = pictures
        context['picture_form'] = picture_form
        return context

    # 送信されて、POST処理が実行された場合に実行されるメソッド
    def post(self, request, *args, **kwargs):
        # 本の保存は１１４行目で処理されるので、画像の保存処理のみ記載する
        picture_form = forms.PictureUploadForm(request.POST or None, request.FILES or None)
        if picture_form.is_valid() and request.FILES:
            book = self.get_object()  # 画像をどのBookとひっつけるのか、Bookを特定できる（いま更新しているBookを呼び出すことができる）
            picture_form.save(book=book)  # ()の中のbookはPictureUploadFormのbookから渡されている
        return super(BookUpdateView, self).post(request, *args, **kwargs)
        
    
    
    
#############################################
# 挿入したデータを削除する処理

class BookDeleteView(DeleteView):
    model = Books
    template_name = 'delete_book.html'  
    success_url = reverse_lazy('store:list_books')
    
    
    
    
######################################
# 一般的にformを使う使い方らしい

class BookFormView(FormView):  # ここの一番最初に定義したIndexViewクラスとよく似ている
    template_name = 'form_book.html'
    form_class = forms.BookForm
    success_url = reverse_lazy('store:list_books')

    # 初期値を変えてる
    def get_initial(self):
        initial = super(BookFormView, self).get_initial()
        initial['name'] = 'form sample'  # name欄にform sampleが入る
        return initial

    def form_valid(self, form):
        if form.is_valid():
            form.save()       # ここで保存処理！
        return super(BookFormView, self).form_valid(form)


##################################################
# 別のView、別のページにリダイレクトをしたい場合に用いられる


class BookRedirectView(RedirectView):
    url = 'https://yahoo.co.jp'  # 静的に動く

    def get_redirect_url(self, *args, **kwargs):  # 動的に動く
        book = Books.objects.first()
        if 'pk' in kwargs:
            return reverse_lazy('store:detail_book', kwargs={'pk': kwargs['pk']})

        return reverse_lazy('store:edit_book', kwargs={'pk': book.pk})