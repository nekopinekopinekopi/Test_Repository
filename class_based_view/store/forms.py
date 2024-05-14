from django import forms
from .models import Books, Pictures
from datetime import datetime






# 作成したBooksモデルにデータを挿入する処理を書いていく

class BookForm(forms.ModelForm):  
    
    class Meta:
        model = Books
        fields = ['name', 'description', 'price']
        
        
    def save(self, *args, **kwargs):  # 通常このクラスを呼び出すと勝手にsaveメソッドが実行されるけど、今回はオーバーライドをしていく
        obj = super(BookForm, self).save(commit=False)
        obj.create_at = datetime.now()  # model.pyのBaseModelクラスの
        obj.update_at = datetime.now()  # ２つのカラムを保存する処理
        obj.save()
        return obj
    
    

# 挿入したデータを更新するフォーム
class BookUpdateForm(forms.ModelForm):  
    
    class Meta:
        model = Books
        fields = ['name', 'description', 'price']
        
        
    def save(self, *args, **kwargs):  # 通常このクラスを呼び出すと勝手にsaveメソッドが実行されるけど、今回はオーバーライドをしていく
        obj = super(BookUpdateForm, self).save(commit=False)
        obj.update_at = datetime.now()  # ２つのカラムを保存する処理
        obj.save()
        return obj
    
    
    
# 写真をアップロードするフォーム

class PictureUploadForm(forms.ModelForm):
    picture = forms.FileField(required=False)
    
    class Meta:
        model = Pictures
        fields = ['picture',]

    def save(self, *args, **kwargs):
        obj = super(PictureUploadForm, self).save(commit=False)
        obj.create_at = datetime.now()
        obj.update_at = datetime.now()
        obj.book = kwargs['book']
        obj.save()
        return obj
