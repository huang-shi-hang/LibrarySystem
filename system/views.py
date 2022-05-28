from django.shortcuts import render,redirect,HttpResponse
from . import models
from rbac import models as rbac_models
from rbac.service.init_permission import init_permission

# Create your views here.
#用于实例化的类
class BasePermPage(object):
    def __init__(self, code_list):
        print("################",code_list)
        self.code_list = code_list

    def has_add(self):
        print("################",self.code_list)
        if "add" in self.code_list:
            return True

    def has_del(self):
        if "del" in self.code_list:
            return True

    def has_edit(self):
        if "edit" in self.code_list:
            return True

#登录界面
def login(request):
    if request.method == "GET":
        return render(request, "system/login.html")
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = rbac_models.UserInfo.objects.filter(username=username, password=password).first()
        if user:
            init_permission(request,user)
            request.session['user_nickname']=user.nickname
            request.session['username']=user.username
            return redirect("/system/index/")
        # if (username =='hsh111' and password=='111'):
        #     return redirect("/system/index/")
        else:
            return render(request, "system/login.html")
#退出界面
def logout(request):
    request.session.clear()
    rep=redirect('/login/')
    rep.cookies.clear()
    return rep

#首页
def  index(request):
    return render(request,'system/index.html')

#图书相关视图函数
#图书信息
def booklist(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))  # 实例化
    booklist=models.bookinfo.objects.all()
    return render(request,'system/bookinfo_list.html',{'booklist': booklist, "pagpermission": pagpermission})
    # return render(request, 'system/bookinfo_list.html', {'booklist': booklist})
#添加
def bookadd(request):
    if request.method == 'POST':
        book_num=request.POST.get('book_num')
        author=request.POST.get('author')
        price=request.POST.get('price')
        remarks=request.POST.get('remarks')
        status = '0'
        models.bookinfo.objects.create(book_num=book_num,author=author,price=price,remarks=remarks,status=status)
        return redirect('/system/booklist')
    return render(request,'system/bookinfo_add.html')
#修改
def bookedit(request,id):
    if request.method == 'POST':
        obj_id=request.POST.get('id')
        book_obj=models.bookinfo.objects.get(id=obj_id)
        book_num=request.POST.get('book_num')
        author=request.POST.get('author')
        price=request.POST.get('price')
        remarks=request.POST.get('remarks')
        status = request.POST.get('status')
        book_obj.book_num=book_num
        book_obj.author=author
        book_obj.price=price
        book_obj.remarks=remarks
        book_obj.status = status
        book_obj.save()

        return redirect('/system/booklist')
    book_obj=models.bookinfo.objects.get(id=id)

    return render(request,'system/bookinfo_edit.html',{'obj':book_obj})

#删除
def bookdel(request,id):
    book_obj = models.bookinfo.objects.get(id=id)
    book_obj.delete()
    return redirect('/system/booklist')

#用户信息
def userlist(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))  # 实例化
    user_list=rbac_models.UserInfo.objects.all()
    return render(request,'system/userinfo_list.html',{'user_list':user_list, "pagpermission": pagpermission})
    # return render(request, 'system/userinfo_list.html', {'user_list': user_list})

def useredit(request,id):
    if request.method == 'POST':
        obj_id=request.POST.get('id')
        user_obj=rbac_models.UserInfo.objects.get(id=obj_id)
        username=request.POST.get('username')
        password=request.POST.get('password')
        nickname=request.POST.get('nickname')
        email=request.POST.get('email')
        user_obj.username=username
        user_obj.password=password
        user_obj.nickname=nickname
        user_obj.email=email
        user_obj.save()

        return redirect('/system/userlist')
    user_obj=rbac_models.UserInfo.objects.get(id=id)

    return render(request,'system/userinfo_edit.html',{'obj':user_obj})

#借阅图书信息上报

import datetime

def borrowlist(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))  # 实例化
    tday=datetime.datetime.now().date()
    user_nickname = request.session.get('user_nickname')
    borrow_list = models.borrowinfo.objects.filter(approve_status='0',bookuser=user_nickname)
    return render(request,'system/borrow_list.html',{'borrow_list':borrow_list,"pagpermission": pagpermission})
    # return render(request, 'system/borrow_list.html', {'borrow_list': borrow_list})

def borrowadd(request):
    tday = datetime.datetime.now().strftime('%Y-%m-%d')
    book_list = models.bookinfo.objects.filter(status='0')
    user_nickname = request.session.get('user_nickname')
    if request.method=='POST':
        bookuser=request.POST.get('bookuser')
        bookid = request.POST.get('book_id')
        time_begin= datetime.datetime.now()
        time_end = time_begin + datetime.timedelta(days = 90)
        models.borrowinfo.objects.create(bookuser=bookuser,book_id=bookid,
                                     time_begin=time_begin,time_end=time_end,oprator=user_nickname,approve_status='0')
        return redirect('/system/borrowlist/')

    return render(request,'system/borrow_add.html',{'booklist':book_list,'tday':tday,'nickname':user_nickname})

def borrowreturn(request):
    tday = datetime.datetime.now().strftime('%Y-%m-%d')
    user_nickname = request.session.get('user_nickname')
    borrow_list = models.borrowinfo.objects.filter(bookuser=user_nickname,approve_status='1')
    if request.method=='POST':
        borrowid = request.POST.get('borrow_id')
        models.borrowinfo.objects.filter(id=borrowid).update(approve_status='2',time_end=tday)
        return redirect('/system/borrowlist/')

    return render(request,'system/borrow_return.html',{'borrowlist':borrow_list,'tday':tday,'nickname':user_nickname})

def borrowagain(request):
    tday = datetime.datetime.now().strftime('%Y-%m-%d')
    user_nickname = request.session.get('user_nickname')
    borrow_list = models.borrowinfo.objects.filter(bookuser=user_nickname,approve_status='1')
    againtime = (datetime.datetime.now()+datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    if request.method=='POST':
        borrowid = request.POST.get('borrow_id')
        bookid = models.borrowinfo.objects.get(id=borrowid).book_id
        models.borrowinfo.objects.filter(id=borrowid).update(approve_status='0',time_end=againtime)
        models.bookinfo.objects.filter(id=bookid).update(status='0')
        return redirect('/system/borrowlist/')
    return render(request,'system/borrow_again.html',{'borrowlist':borrow_list,'tday':againtime,'nickname':user_nickname})

from django.core import exceptions
import json
def borrowdel(request,*args,**kwargs):

    ret={'status':False}
    try:
        obj = models.borrowinfo.objects.get(id=int(kwargs['id']))
        obj.delete()
        ret['status']=True
    except Exception:
        ret['status'] = False

    return HttpResponse(json.dumps(ret))


def borrowedit(request,*args,**kwargs):
    tday = datetime.datetime.now().strftime('%Y-%m-%d')
    book_list = models.bookinfo.objects.all()
    user_nickname = request.session.get('user_nickname')
    if request.method=='POST':
        borrowid=request.POST.get('id')
        bookuser=request.POST.get('bookuser')
        # booknum=request.POST.get('book_num')
        # remarks=request.POST.get('remarks')
        # author=request.POST.get('author')
        # price = request.POST.get('price')
        bookid = request.POST.get('book_id')
        time_begin=request.POST.get('time_begin')
        time_end=request.POST.get('time_end')
        models.borrowinfo.objects.filter(id=borrowid).update(bookuser=bookuser,book_id=bookid,
                                                    time_begin=time_begin,time_end=time_end,
                                                     oprator=user_nickname)
        return redirect('/system/borrowlist/')
    borrow_obj = models.borrowinfo.objects.get(id=int(kwargs['id']))
    book_list = models.bookinfo.objects.all()
    return render(request,'system/borrow_edit.html',{'obj':borrow_obj,'booklist':book_list})

from utils.paginater import Paginater
def borrowcheck(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))  # 实例化
    user_list = rbac_models.UserInfo.objects.all()
    if request.method == 'POST':
        # user_id是使用者id，borrow_date1到borrow_date2是其借阅的开始和结束记录
        user_name = request.POST.get('user', None)
        borrow_date1 = request.POST.get('borrow_date1', None)
        borrow_date2 = request.POST.get('borrow_date2', None)
        condition_dic = {}
        condition_dic['approve_status'] = '0'
        if user_name:
            condition_dic['user_name'] =user_name
        if borrow_date1:
            condition_dic['borrow_date__gte'] = borrow_date1
        if borrow_date2:
            condition_dic['borrow_date__lte'] = borrow_date2
            # print(** condition_dic)
        if len(condition_dic) > 0:
            # 取得记录总数
            total_count = models.borrowinfo.objects.filter(**condition_dic).count()
        else:
            total_count = models.borrowinfo.objects.all().count()
        cur_page_num = request.GET.get("page")
        if not cur_page_num:
            cur_page_num = "1"
        #print(cur_page_num, type(cur_page_num))

        # 设定每一页显示多少条记录
        one_page_lines = 10
        # 页面上总共展示多少页码标签
        page_maxtag = 7
        page_obj = Paginater(url_address='/system/borrowcheck/', cur_page_num=cur_page_num, total_rows=total_count,
                             one_page_lines=one_page_lines, page_maxtag=page_maxtag)
        if len(condition_dic) > 0:
            # 对记录进行切片，取出属于本页的记录
            borrow_list = models.borrowinfo.objects.filter(**condition_dic).order_by('time_begin')[page_obj.data_start:page_obj.data_end]
        else:
            borrow_list = models.borrowinfo.objects.all().order_by('time_begin')[page_obj.data_start:page_obj.data_end]
        #print(condition_dic)
        return render(request, 'system/borrowlist_check.html', {'borrow_list': borrow_list, 'page_nav': page_obj.html_page(),
                    'user_list':user_list,'conditions':condition_dic,"pagpermission": pagpermission})
        # return render(request, 'system/borrowlist_check.html',
        #               {'borrow_list': borrow_list, 'page_nav': page_obj.html_page(),
        #                'user_list':user_list,'conditions':condition_dic})
    # 从URL取参数page,这个参数是存在视图生成的HTML代码片段中
    cur_page_num = request.GET.get("page")
    if not cur_page_num:
        cur_page_num = "1"
    #print(cur_page_num, type(cur_page_num))
    # 取得记录总数,首先选择未通过审核的记录
    total_count = models.borrowinfo.objects.filter(approve_status='0').count()
    # 设定每一页显示多少条记录
    one_page_lines = 10
    # 页面上总共展示多少页码标签
    page_maxtag = 7
    page_obj = Paginater(url_address='/system/borrowcheck/', cur_page_num=cur_page_num, total_rows=total_count,
                         one_page_lines=one_page_lines, page_maxtag=page_maxtag)
    # 对记录进行切片，取出属于本页的记录
    borrow_list = models.borrowinfo.objects.filter(approve_status='0').order_by('time_begin')[page_obj.data_start:page_obj.data_end]

    return render(request, 'system/borrowlist_check.html', {'borrow_list': borrow_list, 'page_nav': page_obj.html_page(),
                                                        'user_list':user_list,"pagpermission": pagpermission})
    # return render(request, 'system/borrowlist_check.html', {'borrow_list': borrow_list, 'page_nav': page_obj.html_page(),
    #                                                         'user_list':user_list})



def borrowreturncheck(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))  # 实例化
    user_list = rbac_models.UserInfo.objects.all()
    if request.method == 'POST':
        # user_id是使用者id，borrow_date1到borrow_date2是其借阅的开始和结束记录
        user_name = request.POST.get('user', None)
        borrow_date1 = request.POST.get('borrow_date1', None)
        borrow_date2 = request.POST.get('borrow_date2', None)
        condition_dic = {}
        condition_dic['approve_status'] = '2'
        if user_name:
            condition_dic['user_name'] =user_name
        if borrow_date1:
            condition_dic['borrow_date__gte'] = borrow_date1
        if borrow_date2:
            condition_dic['borrow_date__lte'] = borrow_date2
            # print(** condition_dic)
        if len(condition_dic) > 0:
            # 取得记录总数
            total_count = models.borrowinfo.objects.filter(**condition_dic).count()
        else:
            total_count = models.borrowinfo.objects.all().count()
        cur_page_num = request.GET.get("page")
        if not cur_page_num:
            cur_page_num = "1"
        #print(cur_page_num, type(cur_page_num))

        # 设定每一页显示多少条记录
        one_page_lines = 10
        # 页面上总共展示多少页码标签
        page_maxtag = 7
        page_obj = Paginater(url_address='/system/borrowreturncheck/', cur_page_num=cur_page_num, total_rows=total_count,
                             one_page_lines=one_page_lines, page_maxtag=page_maxtag)
        if len(condition_dic) > 0:
            # 对记录进行切片，取出属于本页的记录
            borrow_list = models.borrowinfo.objects.filter(**condition_dic).order_by('time_begin')[page_obj.data_start:page_obj.data_end]
        else:
            borrow_list = models.borrowinfo.objects.all().order_by('time_begin')[page_obj.data_start:page_obj.data_end]
        #print(condition_dic)
        return render(request, 'system/borrowreturnlist_check.html', {'borrow_list': borrow_list, 'page_nav': page_obj.html_page(),
                    'user_list':user_list,'conditions':condition_dic,"pagpermission": pagpermission})
        # return render(request, 'system/borrowlist_check.html',
        #               {'borrow_list': borrow_list, 'page_nav': page_obj.html_page(),
        #                'user_list':user_list,'conditions':condition_dic})
    # 从URL取参数page,这个参数是存在视图生成的HTML代码片段中
    cur_page_num = request.GET.get("page")
    if not cur_page_num:
        cur_page_num = "1"
    #print(cur_page_num, type(cur_page_num))
    # 取得记录总数,首先选择未通过审核的记录
    total_count = models.borrowinfo.objects.filter(approve_status='2').count()
    # 设定每一页显示多少条记录
    one_page_lines = 10
    # 页面上总共展示多少页码标签
    page_maxtag = 7
    page_obj = Paginater(url_address='/system/borrowreturncheck/', cur_page_num=cur_page_num, total_rows=total_count,
                         one_page_lines=one_page_lines, page_maxtag=page_maxtag)
    # 对记录进行切片，取出属于本页的记录
    borrow_list = models.borrowinfo.objects.filter(approve_status='2').order_by('time_begin')[page_obj.data_start:page_obj.data_end]

    return render(request, 'system/borrowreturnlist_check.html', {'borrow_list': borrow_list, 'page_nav': page_obj.html_page(),
                                                        'user_list':user_list,"pagpermission": pagpermission})

def borrow_approve(request,ids):
    vids=ids.split(',')
    print('@@@@@@@',vids)
    int_ids=[]
    for i in vids:
        ii=int(i)
        int_ids.append(ii)
    ret = {'status': False}
    for i in int_ids:
        try:
            obj = models.borrowinfo.objects.get(id=i)
            print('#########')
            if(obj.approve_status == '0' and obj.book.status == '0'):
                print('#########1111')
                models.borrowinfo.objects.filter(id=i).update(approve_status='1')
                models.bookinfo.objects.filter(id=obj.book_id).update(status='1')
                ret['status'] = True
            elif(obj.approve_status == '2' and obj.book.status == '1'):
                models.borrowinfo.objects.filter(id=i).update(approve_status='3')
                models.bookinfo.objects.filter(id=obj.book_id).update(status='0')
                ret['status'] = True
            else:
                print('重复，不能加')
                ret['status'] = False
                break
        except Exception:
            ret['status'] = False
    return HttpResponse(json.dumps(ret))

def allborrow(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))  # 实例化
    borrow_list = models.borrowinfo.objects.all()
    return render(request,'system/allborrow_list.html',{'borrow_list':borrow_list,"pagpermission": pagpermission})

def myborrow(request):
    pagpermission = BasePermPage(request.session.get('permission_codes'))  # 实例化
    user_nickname = request.session.get('user_nickname')
    borrow_list = models.borrowinfo.objects.filter(bookuser=user_nickname)
    return render(request,'system/myborrow_list.html',{'borrow_list':borrow_list,"pagpermission": pagpermission})