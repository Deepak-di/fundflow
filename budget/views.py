from django.shortcuts import render,redirect
from django.views.generic import View
from budget.models import Transaction
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.cache import never_cache


# decarator
def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"invalid section")
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

decs=[signin_required,never_cache]




class TransactionForm(forms.ModelForm):

    class Meta:
        model=Transaction
        exclude=("created_date","user_object")
        # fields="__all__"
        # fields=["fields1","field2"]
        widgets={
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
            "type":forms.Select(attrs={"class":"form-control form-select"}),
            "category":forms.Select(attrs={"class":"form-control form-select"})
        }




class RegistrationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password",]
        widgets={

            "username":forms.TextInput(attrs={"class":"form-control"}),
            "email":forms.EmailInput(attrs={"class":"form-control"}),
            "password":forms.PasswordInput(attrs={"class":"form-control"}),

        }





class LoginForm(forms.Form):

    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))





# view for listing all transaction
# url:localhosr/8000/transaction/all
# method:get

@method_decorator(decs,name="dispatch")
class TransactionListView(View):
    def get(self,request,*args,**kwargs):
        qs=Transaction.objects.filter(user_object=request.user)
        cu_month=timezone.now().month
        cu_year=timezone.now().year
        print(cu_month,cu_year)
        data=Transaction.objects.filter(
            created_date__month=cu_month,
            created_date__year=cu_year,
            user_object=request.user
        ).values("type").annotate(type_sum=Sum("amount"))
        print(data)

        cat_qs=Transaction.objects.filter(
            created_date__month=cu_month,
            created_date__year=cu_year,
            user_object=request.user
        ).values("category").annotate(cat_sum=Sum("amount"))
        print(cat_qs)

        # expense_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="expense",
        #     created_date__month=cu_month,
        #     created_date__year=cu_year
        # ).aggregate(Sum("amount"))
        # print(expense_total)

        # income_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="income",
        #     created_date__month=cu_month,
        #     created_date__year=cu_year
        # ).aggregate(Sum("amount"))
        # print(income_total)

        return render(request,"transation_list.html",{"data":qs,"type_total":data,"cat_total":cat_qs})
    




# view for creating Transaction
# url:localhost/8000/transaction/add/
#  method: get, post
    
@method_decorator(decs,name="dispatch")
class TransactionCreateView(View):

    def get(self,request,*args,**kwargs):
        form=TransactionForm()
        return render(request,"transaction_create.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=TransactionForm(request.POST)

        if form.is_valid():
            # form.instance(user_object=request.user)
            # form.save()
            data=form.cleaned_data
            Transaction.objects.create(**data,user_object=request.user)
            messages.success(request,"transaction added")
            return redirect("transaction-list")
        else:
            messages.error(request,"transation failed")
            return render(request,"transaction_list.html",{"form":form})
        



# view for transaction details
# url:localhost/8000/transaction/{id}
# method:get
        
@method_decorator(decs,name="dispatch")
class TransactionDetailView(View):

    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Transaction.objects.get(id=id)
        return render(request,"transaction_detail.html",{"data":qs})
    




# view for transaction delete view
# url:localhost/8000/transaction/{id}/remove
# method:get
    
@method_decorator(decs,name="dispatch")
class TransactionDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction.objects.filter(id=id).delete()
        messages.success(request,"transaction bas been removed")
        return redirect("transaction-list")
    
    




# view for transaction update
# url;loacalhost/8000/transation/id/change
# method:get,post
    
@method_decorator(decs,name="dispatch")
class TransactionUpdateView(View):

    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transaction.objects.get(id=id)
        form=TransactionForm(instance=transaction_object)
        return render(request,"transaction_update.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        transaction_object=Transaction.objects.get(id=id)
        form=TransactionForm(request.POST,instance=transaction_object)
        if form.is_valid:
            form.save()
            messages.success(request,"transaction has been updated succesfully")
            return redirect("transaction-list")
        else:
            messages.error(request,"transaction updation failed")
            return render(request,"transaction_update.html",{"form":form})
        



    




# view for signup
# url:localhost/8000/signup/
# mothod:get,post
        
   
class SignUpView(View):
    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"registratiom.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            print("account created")
            return redirect("signin")
        else:
            print("failed")
            return render(request,"registratiom.html",{"form":form})
        



# view for signin
# url:localhost:8000/signin/
# method:get,post
        

class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"signin.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form =LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect ("transaction-list")
        return render(request,"signin.html",{"form":form})
    



# view for signout 
# url:localhost/8000/signout
# method:get
    
@method_decorator(decs,name="dispatch")
class SignOutView(View):

    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")



    









    

