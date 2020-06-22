from django.shortcuts import render, redirect, get_object_or_404
from users.models import *
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, datetime
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect
from .forms import *
from users.views import home



def doctors_page(request):
    rating = [1,2,3,4,5]

    # search:
    url_parameter = request.GET.get('q')
    url_speciality = request.GET.get('s')
    url_city = request.GET.get('c')

    if url_parameter:
        doctors = Doctor.objects.filter(Q(first_name__icontains=url_parameter) |Q(last_name__icontains=url_parameter))
    
    elif url_speciality:
        doctors = Doctor.objects.filter(specialization__icontains = url_speciality)

    elif url_city:
        doctors = Doctor.objects.filter(clinic_address__icontains=url_city)
    
    else:
        doctors = Doctor.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(doctors, 6)
    
    try:
        doctors = paginator.page(page)
    
    except PageNotAnInteger:
        doctors = paginator.page(1)
    
    except EmptyPage:
        doctors = paginator.page(paginator.num_pages)

    context = {'doctors': doctors ,"rating": rating}

    if request.is_ajax():
        html = render_to_string(

            template_name="doctors-partial.html", 
            context={'doctors': doctors ,"rating": rating}
        )

        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    return render(request, 'allDoctors.html', context)



def doctor_profile(request,id):
    doctor = Doctor.objects.get(id=id)
    rating = [1,2,3,4,5]
    rate = doctor.rate_set.all().values()
    try:
        user_rate = doctor.rate_set.get(user_id=request.user.id).rate
    except:
        user_rate = 0
    comments = Comment.objects.order_by("-id").filter(doctor=id)
    complains = Complain.objects.all()
    context = {'doctor':doctor,'rating':rating , 'comments':comments , 'complains':complains , "user_rate": user_rate ,"rate":rate}
    return render(request, 'doctorProfile.html', context)

def add_comment(request,id):
    try:
        if request.method == 'POST':
            if request.POST.get('context') == '':
                messages.error(request, "Invalid comment,Comment can't be empty")
            else:
                user_id = request.user.id
                context= request.POST.get('context')
                Comment.objects.create(context= context,user_id = user_id, doctor_id = id)
    except:
        messages.error(request ,"You have already commented to this doctor before!")
    return redirect('doctor', id)

def remove_comment(request, id):
    comment = Comment.objects.get(id=id)
    doctor_id = comment.doctor.id
    comment.delete()
    return redirect('doctor', doctor_id)

# @csrf_exempt
def edit_comment(request, id):
    if request.method == 'POST':
        comment = Comment.objects.get(id=id)
        # comment.context = request.POST.get('data')
        comment.context = request.POST.get('context')
        if comment.context == '':
            messages.error(request, "Invalid comment,Comment can't be empty")
        else:  
            comment.save()
    return redirect('doctor', comment.doctor.id)

def add_complain(request,id):
    if request.method == 'POST':
        if request.POST.get('contain') == '':
            messages.error(request, "Invalid complaint,Complaint cannot be empty")
        else:
            user_id = request.user.id
            contain = request.POST.get('contain')
            Complain.objects.create(contain= contain,user_id = user_id, doctor_id = id)
            messages.info(request,"We have received your complaint")
    return redirect('doctor', id)

def book_appointment(request,id):
    if request.user.is_authenticated:
        # doctor = Doctor.objects.get(id=id)
        user = get_user(request)
        books = user.userbook_set.all()
        books = [i.doctor_book_id for i in books]
        books_count = len(books)
        book_info = Doctor_Book.objects.filter(
            doctor_id=id, end_time__date__gte = date.today()
        )
        copoun = user.copoun.last()
        token = None
        if copoun:
            token = copoun.token
        context = {'book_info': book_info, "books": books, 'books_count': books_count, 'token': token}

        return render(request, 'book.html', context)
    else:
        return redirect('signin')

def book_redirect(request,id):
    user = get_user(request)
    obj = UserBook.objects.filter(user=user)
    if not obj:
        token = get_random_string(length=6)
        Copoun.objects.create(token=token, user=user)
    UserBook.objects.create(user=user, doctor_book_id=id)
    book_id = Doctor_Book.objects.get(id=id)
    messages.info(request,"Your book has been placed successfully")

    return redirect('appointment', book_id.doctor_id)

def delete_appointment(request, id):
    user = request.user
    appointment = UserBook.objects.get(user=user, doctor_book_id=id)
    appointment.delete()
    book_id = Doctor_Book.objects.get(id=id)
    
    return redirect('appointment', book_id.doctor_id)

def copoun_activation(request, token):
    user = get_user(request)
    book = user.userbook_set.first()
    fees = book.doctor_book.doctor.fees
    copoun = Copoun.objects.filter(user=user, token=token).last()
    if copoun and not copoun.is_used:
        copoun.is_used = True
        copoun.save()
        new_fees = fees * 0.8
        messages.info(request, f"Your book has been placed successfully, the old fees is {fees} and the new one is {new_fees}")
    else:
        messages.info(request, "Sorry, your coupon is not valid OR may be used before,Please try again later")
    return redirect("appointment", book.doctor_book.doctor.id)

def rate_doctor(request,id):
    try:
        if request.method == 'POST':
            rate = int(request.POST.get('rate'))
            Rate.objects.create(user_id=request.user.id, doctor_id=id, rate=rate) 
    except:
        rate = Rate.objects.get(user_id= request.user.id,doctor_id=id)
        rate.rate = int(request.POST.get('rate')) 
        rate.save()
    return redirect('doctor', id)

# def filter_doctors(request):
#     url_parameter = request.GET.get('q')
#     if url_parameter:
#         doctors = Doctor.objects.filter(Q(specialization__icontains=url_parameter) | Q(clinic_address__icontains=url_parameter))
#     context = {'doctors': doctors}

#     return render(request, 'allDoctors.html', context)

@login_required
def clinic_info(request):
    form = AddDoctor()
    clinic_info = None
    if Doctor.objects.filter(user_id=request.user.id).exists():
        clinic_info = Doctor.objects.get(user_id= request.user.id)
        if request.method == 'POST':
            form = AddDoctor(request.POST , request.FILES, instance=clinic_info)
            if form.is_valid():
                doctor = form.save(commit=False)
                doctor.save()
                messages.success(request, "Your clinic information updated successfully")
                redirect('clinic')
        else:
            form = AddDoctor(initial={
                'first_name': clinic_info.first_name.capitalize(),
                'last_name': clinic_info.last_name.capitalize(),
                'bio': clinic_info.bio,
                'specialization': clinic_info.specialization,
                'image': clinic_info.image,
                'clinic_address': clinic_info.clinic_address,
                'fees': clinic_info.fees,
                'phone': clinic_info.phone,
                'waiting_time': clinic_info.waiting_time,
                })
    else:
        if request.method == 'POST':
            form = AddDoctor(request.POST , request.FILES)
            if form.is_valid():
                doctor = form.save(commit=False)
                doctor.user = request.user
                doctor.save()
                messages.success(request, "Your clinic information updated successfully")
                redirect('clinic')

    if request.user.is_doctor:
        return render(request, 'clinc_info.html', {'form': form , 'clinic_info' : clinic_info} )
    else:    
        return redirect('home')


@login_required
def add_book(request):
    books = Doctor_Book.objects.filter(doctor_id= request.user.doctor.id, end_time__gte = date.today())
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        start_time = datetime.strptime(start, "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(end, "%Y-%m-%d %H:%M")
        x = datetime.now().strftime("%Y-%m-%d %H:%M")
        today = datetime.strptime(x, "%Y-%m-%d %H:%M")

        if end_time < start_time:
            messages.error(request, "Error: End date should be after start date")
        elif start_time < today or end_time < today:
            messages.error(request, "Error: Start and end date cannot be before today")

        else:     
            Doctor_Book.objects.create(doctor_id=request.user.doctor.id, start_time=start, end_time=end) 
            messages.success(request, "Book added successfully")
        return redirect('add_book')

    if request.user.is_doctor:
        return render(request, 'add_book.html',{'books': books})
    else:    
        return redirect('home')


def delete_book(request, id):
    book = Doctor_Book.objects.get(id=id)
    book.delete()
    return redirect('add_book')


def reservation_details(request):
    url_parameter = request.GET.get('q')
    ids = Doctor_Book.objects.filter(doctor_id= request.user.doctor.id).values_list("id") 
    count = UserBook.objects.filter(doctor_book__in = ids, doctor_book__start_time__gte=date.today())
    
    if url_parameter:
        if url_parameter == 'up':
            books = count
    else:
        books = UserBook.objects.filter(doctor_book__in = ids ).order_by('doctor_book__start_time')
    
    return render(request, 'doctor_reservations.html',{'books': books, 'count': count})

