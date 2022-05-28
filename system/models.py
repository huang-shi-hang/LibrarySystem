from django.db import models
from rbac import models as rbac_models
from rbac.models import UserInfo

# Create your models here.

#书籍信息表
class bookinfo(models.Model):
    book_num = models.CharField(max_length=7,verbose_name='图书编号',unique=True)
    author = models.CharField(max_length=10,verbose_name='作者')
    price = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='单价')
    remarks = models.CharField(max_length=32,verbose_name='书籍名',blank=True,null=True)#发现没有写书籍名，临时改成书籍名字
    status = models.CharField(max_length=1, choices=(('0', '未借出'), ('1', '已借出')), verbose_name='图书状态',
                                      blank=True, null=True)
    def __str__(self):
        return self.book_num

#用户数据表，用户包括学生和老师，学生和老师都可以成为读者或者图书管理员
class loguser(models.Model):
    #user_obj和USERINFO表中的内容一一对应，便于权限管理
    user_obj = models.OneToOneField(to=rbac_models.UserInfo,on_delete=models.CASCADE,null=True,blank=True)
    head_img = models.ImageField(upload_to='headimage', blank=True, null=True, verbose_name='头像')  # 头像

    def __str__(self):
        return self.user_obj.username

#借阅信息管理
class borrowinfo(models.Model):
    bookuser = models.CharField(max_length=32,verbose_name='借阅人')
    book = models.ForeignKey(to='bookinfo',on_delete=models.CASCADE)
    # author = models.CharField(max_length=10, verbose_name='作者')
    # price = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='单价')
    time_begin = models.DateField(verbose_name='借阅开始时间',blank=True,null=True)
    time_end = models.DateField(verbose_name='借阅结束时间',blank=True,null=True)
    oprator = models.CharField(max_length=32,verbose_name='录入人员')
    approve_date=models.DateField(verbose_name='审批时间',auto_now=True,blank=True,null=True)
    approve_status=models.CharField(max_length=1,choices=(('0','借书未审批'),('1','通过审批'),('2','还书未审批'),('3','还书已审批')),verbose_name='审批状态',blank=True,null=True)

# #还书信息管理
# class returninfo(models.Model):
#     bookuser = models.CharField(max_length=32, verbose_name='借阅人')
#     book = models.ForeignKey(to='bookinfo', on_delete=models.CASCADE)
#     time_end = models.DateField(verbose_name='还书时间', auto_now=True, blank=True, null=True)
#     approve_date = models.DateField(verbose_name='登记时间', auto_now=True, blank=True, null=True)
