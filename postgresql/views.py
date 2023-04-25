from django.shortcuts import render,redirect
from .models import Expense
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login,authenticate
from django.contrib.auth import get_user_model
from datetime import date
import bcrypt

User = get_user_model()

def isfloat(num):
    try:
        float(num)
        return True
    except:return False 

def index(request):
    if not request.user or str(request.user)=='AnonymousUser':
        if request.method == 'POST':
            name,password = request.POST['name'], request.POST['password']
            user = authenticate(username=name,password = password)
            if user:
                login(request,user)
                return redirect('/dashboard')
        return render(request,'index.html')
    else: return redirect('/dashboard')

def create(request):
    if request.method=='POST':
        name,password,balance,pin = request.POST['name'],request.POST['password'],request.POST['balance'],request.POST['pin']
        try:user = User.objects.get(username=name)
        except User.DoesNotExist:user=None
        if not user:
            bytes = pin.encode('utf-8')
            salt=bcrypt.gensalt()
            hashed_pin = bcrypt.hashpw(bytes,salt)
            User.objects.create_user(username=name,password=password,balance=balance,pin=hashed_pin.decode('utf-8'))
            messages.add_message(request,messages.INFO,f'User {name} created successfully')
            user = User.objects.get(username=name)
            tran =Expense()
            tran.user = user
            tran.type = 'credit'
            tran.amount = float(user.balance)
            tran.balance = float(user.balance)
            tran.to = user.username
            tran.fro = user.username
            tran.date = date.today()
            tran.save()
            return redirect('/')
        else:
            messages.add_message(request,messages.INFO,f'Username: {name} already taken')
            return redirect('/create')
    return render(request,'create.html')

@login_required(login_url='/')
def dashboard(request):
    all_users = User.objects.all().values_list('username','id')
    # users = User.objects.filter(id=id).values()
    user = User.objects.get(username = str(request.user))
    # print(user)
    trans = Expense.objects.filter(user=user).values()
    context = {'trans':trans, 'all_users':all_users, 'user':user}
    return render(request,'dashboard.html',context)

@login_required(login_url='/')
def credit(request):
    if request.method == 'POST':
        amount,pin = request.POST['credit'],request.POST['pincredit']
        user = User.objects.get(username = str(request.user))
        if isfloat(amount):
            if bcrypt.checkpw(pin.encode('utf-8'),user.pin.encode('utf-8')):
                user.balance =  float(user.balance) + float(amount)
                user.save()
                tran = Expense()
                tran.user = user
                tran.type = 'credit'
                tran.amount = float(amount)
                tran.balance = float(user.balance)
                tran.to = user.username
                tran.fro = user.username
                tran.date = date.today()
                tran.save()
                messages.add_message(request, messages.INFO, f'Amount {amount} Credited Successfully')
            else:messages.add_message(request, messages.INFO, f'Incorrect PIN')
        else:messages.add_message(request, messages.INFO, 'Incorrect Input')
        return redirect('/dashboard')

@login_required(login_url='/')
def debit(request):
    if request.method == 'POST':
        amount,pin = request.POST['debit'],request.POST['pindebit']
        user = User.objects.get(username = str(request.user))
        if isfloat(amount):
            if bcrypt.checkpw(pin.encode('utf-8'),user.pin.encode('utf-8')):
                user.balance =  float(user.balance) - float(amount)
                if user.balance >= 0:
                    user.save()
                    tran = Expense()
                    tran.user = user
                    tran.type = 'debit'
                    tran.amount = float(amount)
                    tran.balance = float(user.balance)
                    tran.to = user.username
                    tran.fro = user.username
                    tran.date = date.today()
                    tran.save()
                    messages.add_message(request, messages.INFO, f'Amount {amount} Debited Successfully')
                else:messages.add_message(request, messages.INFO, f'Insufficient Funds')
            else:messages.add_message(request, messages.INFO, f'Incorrect PIN')
        else:messages.add_message(request, messages.INFO, 'Incorrect Input')
        return redirect('/dashboard')

@login_required(login_url='/')
def transfer(request):
    if request.method == 'POST':
        amount,to,pin = request.POST['transfer'], request.POST['to'], request.POST['pintransfer']
        to_user = User.objects.get(id=int(to))
        user = User.objects.get(username=str(request.user))
        if isfloat(amount):
            if bcrypt.checkpw(pin.encode('utf-8'),user.pin.encode('utf-8')):
                user.balance =  float(user.balance) - float(amount)
                if user.balance >=0:
                    user.save()
                    to_user.balance=float(to_user.balance)+float(amount)
                    to_user.save()
                    tran = Expense()
                    tran_credit = Expense()
                    tran.user = user
                    tran.type = 'debit'
                    tran.amount = float(amount)
                    tran.balance = float(user.balance)
                    tran.to = to_user.username
                    tran.fro = user.username
                    tran.date = date.today()
                    tran.save()
                    tran_credit.user = to_user
                    tran_credit.type = 'credit'
                    tran_credit.amount= float(amount)
                    tran_credit.balance = float(to_user.balance)
                    tran_credit.to = to_user.username
                    tran_credit.fro = user.username
                    tran_credit.date = date.today()
                    tran_credit.save()
                    messages.add_message(request, messages.INFO, 'Amount Transferred Successfully')
                else: messages.add_message(request, messages.INFO, 'Insufficient Funds')
            else:messages.add_message(request, messages.INFO, f'Incorrect PIN')
        else:messages.add_message(request, messages.INFO, 'Incorrect Input')
        return redirect('/dashboard')
    
def logout_view(request):
    logout(request)
    return redirect('/')