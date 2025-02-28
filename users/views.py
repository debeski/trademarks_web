from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django_tables2 import RequestConfig
from .tables import UserTable, UserActivityLogTable
from .forms import CustomUserCreationForm, CustomUserChangeForm, PasswordChangeForm, ResetPasswordForm
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

User = get_user_model()

def is_staff(user):
    return user.is_staff

def is_superuser(user):
    return user.is_superuser 

class UserListView(SingleTableMixin, FilterView):
    table_class = UserTable
    model = User
    template_name = "users/manage_users.html"
    filterset_class = UserFilter
    paginate_by = 10  # Show 10 users per page

    def get_queryset(self):
        return User.objects.order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = self.get_queryset()  # Ensure 'users' is available in the template
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to view this page.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        if not request.user.is_staff:
            messages.error(request, "ليس لديك الصلاحية الكافية لزيارة هذا القسم!.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super().dispatch(request, *args, **kwargs)


@user_passes_test(is_staff)
def create_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("manage_users")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/user_form.html", {"form": form})

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
        form = CustomUserChangeForm(instance=user)
    return render(request, "users/user_form.html", {"form": form, "edit_mode": True, "form_reset": form_reset})

@user_passes_test(is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
        return redirect("manage_users")
    return redirect("manage_users")  # Redirect instead of rendering a separate page

class UserActivityLogView(LoginRequiredMixin, UserPassesTestMixin, SingleTableView):
    model = UserActivityLog
    table_class = UserActivityLogTable
    template_name = "user_activity_log.html"

    def test_func(self):
        return self.request.user.is_staff  # Only staff can access logs


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
