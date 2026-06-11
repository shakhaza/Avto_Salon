from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.models import User
from contacts.models import Contact
from django.contrib.auth.decorators import login_required

# Create your views here.

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

def register(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists!')
                    return redirect('register')
                else:
                    user = User.objects.create_user(first_name=firstname, last_name=lastname, email=email, username=username, password=password)
                    auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, 'You are now logged in.')
                    return redirect('dashboard')
        else:
            messages.error(request, 'Password do not match')
            return redirect('register')
    else:
        return render(request, 'accounts/register.html')


from .models import Purchase, Profile, Notification
from cars.models import Car
from django.db.models import Sum

@login_required(login_url = 'login')
def dashboard(request):
    user_inquiry = Contact.objects.order_by('-create_date').filter(user=request.user)
    purchases = Purchase.objects.filter(user=request.user).order_by('-purchase_date')
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    # Analytics
    total_spent = purchases.aggregate(Sum('final_price'))['final_price__sum'] or 0
    cars_count = purchases.count()
    active_installments = purchases.filter(status='ACTIVE')
    
    monthly_total = 0
    for p in active_installments:
        monthly_total += p.monthly_payment

    data = {
        'inquiries': user_inquiry,
        'purchases': purchases,
        'notifications': notifications,
        'total_spent': total_spent,
        'cars_count': cars_count,
        'monthly_total': monthly_total,
    }
    return render(request, 'accounts/dashboard.html', data)

@login_required(login_url='login')
def purchase(request):
    if request.method == 'POST':
        car_id = request.POST['car_id']
        payment_type = request.POST['payment_type']
        installment_months = request.POST.get('installment_months')
        
        car = get_object_or_404(Car, pk=car_id)
        user = request.user

        # Check if car is already sold
        if car.is_sold:
            messages.error(request, 'Sorry, this car has already been sold.')
            return redirect('cars')
        
        # Check if card is registered
        if not user.profile.card_number:
            messages.error(request, 'Please register a card in your profile first.')
            return redirect('dashboard')

        status = 'PAID' if payment_type == 'FULL' else 'ACTIVE'
        
        purchase = Purchase.objects.create(
            user=user,
            car=car,
            payment_type=payment_type,
            status=status,
            final_price=car.price,
            installment_months=installment_months if payment_type == 'INSTALLMENT' else None
        )

        # Mark car as sold
        car.is_sold = True
        car.save()

        # Create notification
        Notification.objects.create(
            user=user,
            title='Purchase Successful',
            message=f'Congratulations! You have successfully purchased the {car.car_title}. You can find more details in your purchases list.'
        )
        
        messages.success(request, f'Congratulations! You have purchased the {car.car_title}.')
        return redirect('dashboard')
    return redirect('cars')

@login_required(login_url='login')
def update_profile(request):
    if request.method == 'POST':
        card_number = request.POST['card_number']
        card_expiry = request.POST['card_expiry']
        card_holder = request.POST['card_holder']
        
        profile = request.user.profile
        profile.card_number = card_number
        profile.card_expiry = card_expiry
        profile.card_holder = card_holder
        profile.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard')
    return redirect('dashboard')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')
    return redirect('home')
