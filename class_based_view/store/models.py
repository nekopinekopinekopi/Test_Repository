from django.db import models
from django.urls import reverse_lazy




class BaseModel(models.Model):
    create_at = models.DateTimeField()
    update_at = models.DateTimeField()

    class Meta:
        abstract = True  # 抽象クラス
        
        
class Books(BaseModel):  # 抽象クラスを継承することで、BaseModelに定義したカラム２つをこのクラスで定義しなくてよくなる
        name = models.CharField(max_length=255)
        description = models.CharField(max_length=1000)
        price = models.IntegerField()

        class Meta:
            db_table = 'books'
            
        # absoluteは絶対という意味らしい
        def get_absolute_url(self):  # CreateViewだけのかな？urlの遷移方法(ridirectみたいなやつ)->BookUpdateViewもこの方法で'store:detail_book'に遷移した。**kwargsにpkが入ったら遷移するってことなのかな。
            return reverse_lazy('store:detail_book', kwargs={'pk':self.pk})



###############################################
# 演習問題


# 本の画像一覧を取ってくる
class PicturesManager(models.Manager):
    
    def filter_by_book(self, book):
        return self.filter(book=book).all()




class Pictures(BaseModel):
    picture = models.FileField(upload_to='picture/')
    book = models.ForeignKey(
        'books', on_delete=models.CASCADE
    )
    objects = PicturesManager()
    
            



    
    

