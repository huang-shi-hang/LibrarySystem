from django.urls import path,include
from . import views


urlpatterns = [
    path('index/',views.index ),
    #图书信息
    path('booklist/',views.booklist),
    path('bookadd/',views.bookadd),
    path('bookedit/<int:id>/',views.bookedit),
    path('bookdel/<int:id>/',views.bookdel),
    #用户信息,包含读者和管理员,这里只允许图书管理员查看用户信息
    path('userlist/',views.userlist),
    path('useredit/<int:id>/',views.useredit),
    #借书上报
    path('borrowlist/',views.borrowlist),
    path('borrowadd/',views.borrowadd),
    path('borrowedit/<int:id>/',views.borrowedit),
    path('borrowdel/<int:id>/',views.borrowdel),
    path('borrowreturn/',views.borrowreturn),
    path('borrowagain/',views.borrowagain),
    #借书审批
    path('borrowcheck/',views.borrowcheck),
    path('borrowreturncheck/',views.borrowreturncheck),
    path('borrow_approve/<str:ids>/',views.borrow_approve),
    #借阅记录查看
    path('allborrow/',views.allborrow),
    path('myborrow/',views.myborrow),
]