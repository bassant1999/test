from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from .authen import authen_mail
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import csv
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
import requests
from bs4 import BeautifulSoup
from django.db.models import Q
from django.core import serializers
from .free_books import *
from .paid_books import *



def f_user_history(user):
    f_books = free_books_rating.objects.filter(User_id = user)
    user_hist = {}
    for f_book in f_books:
        user_hist[f_book.Book_id.title] = f_book.rating
    return user_hist

# start page
def start(request):
    if not request.user.is_authenticated:
        return render(request, "book_heaven/start.html")
    return HttpResponseRedirect(reverse("home"))
def about_us(request):
    return render(request, "book_heaven/about.html")
# home page
def home(request):
    # print(free_books_df.iloc[2])
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    R_free_books = free_books.objects.all()
    # print("hist", f_user_history(request.user))
    out = recommend_with_user_history(f_user_history(request.user), 10000)

    ids = []
    for row in out:
        ids.append(int(row["id"].lstrip("PG")))
    fbs = free_books.objects.filter(Gutenberg_id__in=ids)
    R_free_books = sorted(fbs, key=lambda x: ids.index(x.Gutenberg_id)) 
    # for f in R_free_books:
    #     print(f.Gutenberg_id)
    # print("new:")
    # print(type(n[0]))
    # for f in n:
    #     print(f.Gutenberg_id)
    # print(type(R_free_books[0]))
    paginator = Paginator(R_free_books, 10)
    page = request.GET.get('page')
    recomended_free_books = 0
    try:
        recomended_free_books = paginator.page(page)
    except PageNotAnInteger:
        recomended_free_books = paginator.page(1)
    except EmptyPage:
        recomended_free_books = paginator.page(paginator.num_pages)
    return render(request, "book_heaven/home.html", {
        "recomended_free_books": recomended_free_books
            })

#home_my_library
def my_library_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))

    user = User.objects.get(id= request.user.id) 
    pbooks = []
    fbooks = []
    paid_books_lib = paid_books_library.objects.filter(User_id = user)
    free_books_lib = free_books_library.objects.filter(User_id = user)
    for paid_book in paid_books_lib:
        b={}
        print("--------",paid_book.Book_id.id)
        book_info = paid_books.objects.get(id = paid_book.Book_id.id)
        b["index"] = "A"+ str(book_info.id)
        b["book"] = book_info
        b["cover"] = book_info.Image_url
        b["title"] = book_info.title
        b["author"] = book_info.Authors
        pbooks.append(b)

    for free_book in free_books_lib:
        b={}
        print("--------",free_book.Book_id.id)
        book_info = free_books.objects.get(id = free_book.Book_id.id)
        b["index"] = "B"+ str(book_info.id)
        b["book"] = book_info 
        b["cover"] = book_info.Image_url
        b["title"] = book_info.title
        b["author"] = book_info.Authors
        fbooks.append(b)

    print(pbooks,fbooks)

    return render(request,"book_heaven/myLibrary.html",{
        "user":user,
        "pbooks" : pbooks,
        "fbooks" : fbooks
    })

# remove books from library
def remove_lib(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    print("*******")
    result_ = request.GET.getlist('result_lib[]', None)  
    # result_[2] = User(result_[2])
    print("*******",result_)
    user = User.objects.get(id = int(result_[2]))
    if (int(result_[0]) == 1) :
        pbook = paid_books.objects.get(id = int(result_[1]))
        paid_books_library.objects.filter(User_id = user, Book_id = pbook).delete()

    elif (int(result_[0]) == 0) :
        fbook = free_books.objects.get(id = int(result_[1]))
        free_books_library.objects.filter(User_id = user, Book_id = fbook).delete()

    return  HttpResponseRedirect(reverse("my_library"))        

    
    

# home_paid_books
def home_paid_books(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    R_paid_books = []
    p_out = get_new_user_book_embeddings(book_df, model1_path, model2_path,p_user_history(request.user), 30)

    for row in p_out:
        R_paid_books.append(paid_books.objects.get(title=row["title"] ,Authors=row["author"]))
    paginator = Paginator(R_paid_books, 10)
    page = request.GET.get('page')
    recomended_paid_books = 0
    try:
        recomended_paid_books = paginator.page(page)
    except PageNotAnInteger:
        recomended_paid_books = paginator.page(1)
    except EmptyPage:
        recomended_paid_books = paginator.page(paginator.num_pages)
    return render(request, "book_heaven/home_paid_books.html", {
        "recomended_paid_books": recomended_paid_books
            })

# login page
def login_view(request):
    #hereeeeeeeeee
    if request.method =="POST":
        
        email = request.POST["email"]
        password = request.POST["password"]
        validation = authen_mail()
        user = validation.authenticate(request, username =email, password=password)

        if user:
            login(request,user)
            return HttpResponseRedirect(reverse("home"))
        
        else:
            return render(request, "book_heaven/login.html", {
                "message": "Invalid login"
            })
    return render(request, "book_heaven/login.html")


def logout_view(request):
    logout(request)
    return render(request, "book_heaven/login.html")

# signup page
def signup_view_1(request):
    if request.method =="POST":
        newUser = {}
        newUser['username']= request.POST["username"]
        newUser['email'] = request.POST["email"]
        newUser['Birthday'] = request.POST["birth"]
        newUser['password'] = make_password(request.POST["password"])
        nuser= User(username = newUser['username'], email= newUser['email'], Birthday=newUser['Birthday'],password =newUser['password'])
        try:
            nuser.full_clean()
        except ValidationError as e:        
            print(e)
            return render(request, "book_heaven/signup.html", {
                "message": e
            })
        else:
            # newUser.save()
            request.session["user"]=newUser
            return HttpResponseRedirect(reverse("signup_helper"))

    else:
       return render(request, "book_heaven/signup.html") 
    
def signup_view_2(request):
    pbooks = list(paid_books.objects.all())
    result_ = request.GET.getlist('result[]', None)      
    u= request.session["user"]
    print("****",u)
    User.objects.create(username = u['username'], email= u['email'], Birthday=u['Birthday'],password =u['password'])
    user_id = User.objects.get(email = u['email'])
    
    print("fffffffffffffff",result_)
    for i in range(0,5,2):
        print("title",result_[i])        
        book_id = paid_books.objects.filter(title = result_[i]).first()
        paid_books_rating.objects.create(User_id= user_id,Book_id = book_id,rating = int(result_[i+1]))
    for i in range(6,11,2):
        print("title",result_[i])    
        book_id = free_books.objects.filter(title = result_[i]).first()        
        free_books_rating.objects.create(User_id= user_id,Book_id = book_id,rating = int(result_[i+1]))
    return  HttpResponseRedirect(reverse("login"))
   

def signup_helper(request):
    pbooks = list(paid_books.objects.values_list('title', flat=True))
    fbooks = list(free_books.objects.all().order_by('-Download_count').values_list('title', flat=True))[0:50000]
    # fbook_html = serializers.serialize("json",fbooks)
    # pbook_html = serializers.serialize("json",pbooks)
    return render(request, "book_heaven/signup_continue.html",{
        "pbooks" : pbooks,
        "fbooks" : fbooks,
        "fbooks_js": json.dumps(fbooks),
        "pbooks_js": json.dumps(pbooks)
    }) 



# account page
def myAccount_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    username = request.user.username
    email =  request.user.email
    birthday = request.user.Birthday 

    return render(request,"book_heaven/myAccount.html",{
        "username" :username ,
        "email" :email ,
        "birthday" :birthday
    })

def book_to_library(request,paid_book_id):  
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))  
    user = User.objects.get(id= request.user.id)
    book = paid_books.objects.get(id = paid_book_id) 
    try:
        paid_books_library.objects.get(User_id = user, Book_id = book)
    except paid_books_library.DoesNotExist:    
        paid_books_library.objects.create(User_id = user, Book_id = book)
    
    return  HttpResponseRedirect(reverse("paid_book", kwargs={'paid_book_id':paid_book_id}))

def fbook_to_library(request,free_book_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))    
    user = User.objects.get(id= request.user.id)
    book = free_books.objects.get(id = free_book_id) 
    try:
        free_books_library.objects.get(User_id = user, Book_id = book)
    except free_books_library.DoesNotExist:    
        free_books_library.objects.create(User_id = user, Book_id = book)
    
    return  HttpResponseRedirect(reverse("free_book", kwargs={'free_book_id':free_book_id}))

def rating_stars(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    result_ = request.GET.getlist('result[]', None)
    user = User.objects.get(id= request.user.id) 
    book = paid_books.objects.get(id = result_[0])
    rating_ = int(result_[1]) 
    exists = False
    try:
        e = paid_books_rating.objects.get(User_id = user, Book_id = book)
        exists = True
    except paid_books_rating.DoesNotExist:    
        paid_books_rating.objects.create(User_id = user, Book_id = book, rating=rating_)  
    if(exists):
        
        if((e.rating) != rating_):
            e.delete()
            paid_books_rating.objects.create(User_id = user, Book_id = book, rating=rating_)
    return  HttpResponseRedirect(reverse("paid_book", kwargs={'paid_book_id':result_[0]}))        

def frating_stars(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    result_ = request.GET.getlist('result[]', None)
    user = User.objects.get(id= request.user.id) 
    book = free_books.objects.get(id = result_[0])
    rating_ = int(result_[1]) 
    exists = False
    try:
        e = free_books_rating.objects.get(User_id = user, Book_id = book)
        exists = True
    except free_books_rating.DoesNotExist:    
        free_books_rating.objects.create(User_id = user, Book_id = book, rating=rating_)  
    if(exists):
        if((e.rating) != rating_):
            e.delete()
            free_books_rating.objects.create(User_id = user, Book_id = book, rating=rating_)
    return  HttpResponseRedirect(reverse("free_book", kwargs={'free_book_id':result_[0]}))  

def search_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    # out list is the output of recommendation fn of free books
    # print("Aya",book2book_encoded)
    aya = { "The Fault in Our Stars":5, "Pride and Prejudice": 4, "Little Women (Little Women, #1)": 3}
    
    if request.method =="POST":
        searched = request.POST["searched"]
        fbooks = []
        pbooks = []
        psearched = list(paid_books.objects.filter(Q(title__contains = searched) | Q(Authors__contains=searched)))
        psearched_title = list(paid_books.objects.filter(Q(title__contains = searched) | Q(Authors__contains=searched)).values_list('title', flat=True))
        psearched_author = list(paid_books.objects.filter(Q(title__contains = searched) | Q(Authors__contains=searched)).values_list('Authors', flat=True))
        fsearched = list(free_books.objects.filter(Q(title__contains = searched) | Q(Authors__contains=searched)).values_list('Gutenberg_id', flat=True))
        dbfbooks_ = list(free_books.objects.filter(Q(title__contains = searched) | Q(Authors__contains=searched)))
        ptest = psearched[10:20]
        # print("*****************",fsearched)
        out = recommend_with_user_history(f_user_history(request.user), 700)
        p_out = get_new_user_book_embeddings(book_df, model1_path, model2_path,p_user_history(request.user), 30)
        # print("out     :", out)
        for i in range(0,len(out)):
            if int(out[i]["id"].lstrip("PG")) in fsearched :              
                fbooks.append(free_books.objects.get(Gutenberg_id = int(out[i]["id"].lstrip("PG"))))
        for i in range(0,len(p_out)):
            if ((p_out[i]["title"] in psearched_title ) and (p_out[i]["author"] in psearched_author)):              
                pbooks.append(paid_books.objects.get(title = p_out[i]["title"] , Authors = p_out[i]["author"]))        
        
        j =0
        if(len(fbooks)<10):
            j = 10-len(fbooks)
        k = 0
        if(len(pbooks)<10):
            k = 10-len(pbooks)
        print("888888",len(fbooks))
        print("999999",len(pbooks))
        rdbfbooks = dbfbooks_[j:]
        rdbpbooks = psearched[k:]
        return render(request,"book_heaven/search.html",{
            "searched_value" : searched,
            "pbooks" : pbooks[0:10],
            "fbooks" : fbooks[0:10],
            "dbfbooks": dbfbooks_[0:j],
            "dbpbooks": psearched[0:k],
            "fall" :  json.dumps([fbook.serialize() for fbook in fbooks]),
            "pall" : json.dumps([pbook.serialize() for pbook in pbooks]),
            "dbfall" : json.dumps([dbfbook.serialize() for dbfbook in rdbfbooks]),
            "dbpall" : json.dumps([dpbook.serialize() for dpbook in rdbpbooks])

        })
    else:
        return render(request,"book_heaven/search.html",{
        })

# def fsearch_helper(request):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("start"))
#     searched = str(request.GET.get("searched"))
#     fbooks_ = []
#     # out = recommend_with_user_history(f_user_history(request.user), 100)
#     fsearched = list(free_books.objects.filter(Q(title__contains = searched) | Q(Authors__contains=searched)).values_list('Gutenberg_id', flat=True))
#     # print("*****************",fsearched)
#     out = recommend_with_user_history(f_user_history(request.user), 100)
#     for i in range(0,len(out)):
#         if int(out[i]["id"].lstrip("PG")) in fsearched :              
#             fbooks_.append(free_books.objects.get(Gutenberg_id = int(out[i]["id"].lstrip("PG"))))
#     start = int(request.GET.get("start") or 0)
#     end = int(request.GET.get("end") or (len(out)))
#     fbooks = fbooks_[start:end]
#     return JsonResponse([fbook.serialize() for fbook in fbooks], safe=False)

# def psearch_helper(request):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("start"))
#     searched = str(request.GET.get("searched"))
#     pbooks = []
#     psearched = list(paid_books.objects.filter(Q(title__contains = searched) | Q(Authors__contains=searched))) 
#     start = int(request.GET.get("start") or 0)
#     end = int(request.GET.get("end") or (len(out)))
#     for i in range(start, end):
#         if out[i]["id"] in psearched :
#             pbooks.append(paid_books.objects.get(Goodread_id = out[i]["id"]))
#     return JsonResponse([pbook.serialize() for pbook in pbooks], safe=False)


def upload_library(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    user_id = request.user
    if 'library' in request.FILES:
        library= request.FILES['library']
        fs = FileSystemStorage()
        filename = fs.save(library.name, library)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url[1:] == "media/"+filename)
        f = 0
        try:
            f = open (uploaded_file_url[1:], encoding="utf8")     
        except FileNotFoundError:
            f = open ("media/"+filename , encoding="utf8")
        csvreader = csv.reader(f)
        header = []
        header = next(csvreader)
        for row in csvreader: 
            rating = row[7]
            goodreads_id = int(row[0])
            if (paid_books.objects.filter(Goodread_id = goodreads_id).exists()):
                book = paid_books.objects.get(Goodread_id = goodreads_id)
                if not (paid_books_rating.objects.filter(User_id = user_id, Book_id =book).exists()):
                    if(rating != "0"):
                            p_book_rating = paid_books_rating(User_id = user_id, Book_id = book, rating = rating)
                            p_book_rating.save()  
                else:
                    if not (paid_books_rating.objects.filter(User_id = user_id, Book_id = book, rating = rating).exists()):
                        prev_rating = paid_books_rating.objects.filter(User_id = user_id, Book_id = book)
                        prev_rating.delete()
                        p_book_rating = paid_books_rating(User_id = user_id, Book_id = book, rating = rating)
                        p_book_rating.save()  
        messages.success(request, 'Changes successfully saved.')
    return HttpResponseRedirect(reverse("my_account"))

# free book page
@login_required
def free_book(request, free_book_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    free_book = free_books.objects.get(id = free_book_id) 
    reviews = free_books_review.objects.filter(Book_id = free_book)
    rating = 0
    try:
        e = free_books_rating.objects.get(User_id = request.user, Book_id = free_book)
        rating = e.rating
    except free_books_rating.DoesNotExist:  
        rating = 0
    return render(request, "book_heaven/free_book.html", {
        "free_book":free_book,
        "reviews":reviews,
        "book_rating" : rating
    })

def free_book_read(request, free_book_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    free_book = free_books.objects.get(id = free_book_id) 
    frmt = 4 #0: html, 1: txt, 2: pdf, 4:None
    url = ""
    formats = json.loads(free_book.formats.replace("\'", "\""))
    for key in formats:
        if 'text/html' in key or 'text/plain' in key or 'pdf' in key:
            if ('htm' in formats[key]):
                frmt = 0
                url = formats[key]
                break
            elif ('txt'  in formats[key]):
                frmt = 1
                url = formats[key]
            elif ('pdf'  in formats[key]):
                frmt = 2
                url = formats[key]
    if(frmt == 0):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        while(soup.img):
            s= soup.img.extract()
        soup.title.string.replace_with(free_book.title)
        nav = soup.new_tag("nav")
        nav['class'] = "hi"
        ul = soup.new_tag("ul")
         # about us
        li0 = soup.new_tag("li")
        a0 = soup.new_tag("a")
        a0['href'] = "../../about_us"
        a0.string = "About us"
        li0.insert(0, a0)
        ul.insert(0, li0)
        # home
        li1 = soup.new_tag("li")
        a1 = soup.new_tag("a")
        a1['href'] = "../../"
        a1.string = "Home"
        li1.insert(0, a1)
        ul.insert(1, li1)
        # account
        li2 = soup.new_tag("li")
        a2 = soup.new_tag("a")
        a2['href'] = "../../myAccount"
        a2.string = "My Account"
        li2.insert(0, a2)
        ul.insert(2, li2)
        # library
        li3 = soup.new_tag("li")
        a3 = soup.new_tag("a")
        a3['href'] = "../../home/my_library"
        a3.string = "My Library"
        li3.insert(0, a3)
        ul.insert(3, li3)
        # Search
        li4 = soup.new_tag("li")
        a4 = soup.new_tag("a")
        a4['href'] = "../../home/search"
        a4.string = "Search"
        li4.insert(0, a4)
        ul.insert(4, li4)
        # log out
        li5 = soup.new_tag("li")
        a5 = soup.new_tag("a")
        a5['href'] = "../../logout"
        a5.string = "Log Out"
        li5.insert(0, a5)
        ul.insert(5, li5)
        nav.insert(0, ul)
        soup.html.body.insert(0, nav)
        # lk = soup.new_tag("link")
        # lk['rel'] = "stylesheet"
        # lk['href'] = "../../static/book_heaven/styles.css"
        # soup.html.head.insert(0, lk)
        return HttpResponse(soup.prettify())
    elif(frmt == 1):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        return render(request, "book_heaven/read.html", {
            "title": free_book.title,
            "story":soup.prettify().split("\n")})
    elif(frmt == 2):
        return redirect(url)
    else:
        return redirect(formats[key])

    return HttpResponse("read")

# review free book
@csrf_exempt
@login_required
def review_free_book(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    if request.method == "POST":
        data = json.loads(request.body)
        free_book_id = data.get("free_book_id")
        review = data.get("review")
        free_book = free_books.objects.get(id = free_book_id)
        print(review)
        print(request.user.id)
        new_review = free_books_review(User_id = request.user, Book_id = free_book, review = review)
        new_review.save()
        return JsonResponse({"success": "added", "user":request.user.username}, status=400)
    return JsonResponse({"error": "invalid request"}, status=400)


# Paid book page
@login_required
def paid_book(request, paid_book_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    paid_book = paid_books.objects.get(id = paid_book_id) 
    reviews = paid_books_review.objects.filter(Book_id = paid_book)
    rating = 0
    try:
        e = paid_books_rating.objects.get(User_id = request.user, Book_id = paid_book)
        rating = e.rating
    except paid_books_rating.DoesNotExist:  
        rating = 0
    return render(request, "book_heaven/paid_book.html", {
        "paid_book":paid_book,
        "reviews":reviews,
        "book_rating" : rating
    })

# review paid books
@csrf_exempt
@login_required
def review_paid_book(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("start"))
    if request.method == "POST":
        data = json.loads(request.body)
        paid_book_id = data.get("paid_book_id")
        review = data.get("review")
        paid_book = paid_books.objects.get(id = paid_book_id)
        new_review = paid_books_review(User_id = request.user, Book_id = paid_book, review = review)
        new_review.save()
        return JsonResponse({"success": "added", "user":request.user.username}, status=400)
    return JsonResponse({"error": "invalid request"}, status=400)
