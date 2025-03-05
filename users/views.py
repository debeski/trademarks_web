# Imports of the required python modules and libraries
######################################################
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from django_tables2 import RequestConfig
from .tables import UserTable, UserActivityLogTable
from .forms import CustomUserCreationForm, CustomUserChangeForm, ArabicPasswordChangeForm, ResetPasswordForm, UserProfileEditForm
from .filters import UserFilter
from .models import UserActivityLog
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django_tables2 import SingleTableView
from django.contrib.auth.views import PasswordChangeView
from django.utils import timezone
from users.signals import get_client_ip

User = get_user_model() # Use custom user model


# Function to recognize staff
def is_staff(user):
    return user.is_staff


# Function to recognize superuser
def is_superuser(user):
    return user.is_superuser 


# Class Function to display users in a table
@login_required
def user_list(request):

    if not request.user.is_staff:
        messages.error(request, "ليس لديك الصلاحية الكافية لزيارة هذا القسم!.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    # Get all users
    qs = User.objects.all()
    
    # Apply filter
    user_filter = UserFilter(request.GET, queryset=qs)
    
    # Create table
    table = UserTable(user_filter.qs)
    
    # Paginate table (10 users per page)
    RequestConfig(request, paginate={'per_page': 10}).configure(table)
    return render(request, "users/manage_users.html", {
        "table": table,
        "filter": user_filter,
        "users": user_filter.qs
    })


# Function for creating a new User
@user_passes_test(is_staff)
def create_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect("manage_users")
        else:
            return render(request, "users/user_form.html", {"form": form})
    else:
        form = CustomUserCreationForm()
    return render(request, "users/user_form.html", {"form": form})


# Function for editing an existing User
@user_passes_test(is_staff)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form_reset = ResetPasswordForm(user, data=request.POST or None)

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("manage_users")
        else:
            # Validation errors will be automatically handled by the form object
            return render(request, "users/user_form.html", {"form": form, "edit_mode": True, "form_reset": form_reset})

    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, "users/user_form.html", {"form": form, "edit_mode": True, "form_reset": form_reset})


# Function for deleting a User
@user_passes_test(is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
        UserActivityLog.objects.create(
            user=request.user,
            action="DELETE",
            model_name='مستخدم',
            object_id=user.pk,
            number=user.username,  # Save the relevant number
            timestamp=timezone.now(),
            ip_address=get_client_ip(request),  # Assuming you have this function
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return redirect("manage_users")
    return redirect("manage_users")  # Redirect instead of rendering a separate page


# Class Function for the Log
class UserActivityLogView(LoginRequiredMixin, UserPassesTestMixin, SingleTableView):
    model = UserActivityLog
    table_class = UserActivityLogTable
    template_name = "user_activity_log.html"

    def test_func(self):
        return self.request.user.is_staff  # Only staff can access logs


# Function that resets a user password
@user_passes_test(is_staff)
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = ResetPasswordForm(user=user, data=request.POST)  # ✅ Correct usage with SetPasswordForm
        if form.is_valid():
            form.save()
            return redirect("manage_users")  # Redirect after successful reset
        else:
            print("Form errors:", form.errors)  # Debugging
            return redirect("edit_user", user_id=user_id)  # Redirect to edit user on failure
    
    return redirect("manage_users")  # Fallback redirect


# Main Function for user profile
@login_required
def user_profile(request):
    user = request.user
    password_form = ArabicPasswordChangeForm(user)
    if request.method == 'POST':
        password_form = ArabicPasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Prevent user from being logged out
            messages.success(request, 'تم تغيير كلمة المرور بنجاح!')
            return redirect('user_profile')
        else:
            # Log form errors
            messages.error(request, "هناك خطأ في البيانات المدخلة")
            print(password_form.errors)  # You can log or print errors here for debugging

    return render(request, 'users/profile.html', {
        'user': user,
        'password_form': password_form
    })


# Function for editing user details
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ التغييرات بنجاح')
            return redirect('user_profile')
        else:
            messages.error(request, 'حدث خطأ أثناء حفظ التغييرات')

    else:
        form = UserProfileEditForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})

