from django import forms
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.hashers import make_password
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML, Fieldset, Button, Submit
from crispy_forms.bootstrap import FormActions

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="الصلاحيات"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "first_name", "last_name", "phone", "occupation", "is_staff", "permissions"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "اسم المستخدم"
        self.fields["email"].label = "البريد الإلكتروني"
        self.fields["first_name"].label = "الاسم"
        self.fields["last_name"].label = "اللقب"
        self.fields["is_staff"].label = "صلاحيات انشاء و تعديل المستخدمين"
        self.fields["password1"].label = "كلمة المرور"
        self.fields["password2"].label = "تأكيد كلمة المرور"

        # Split permissions queryset into two parts for 2 columns
        permissions_list = list(Permission.objects.exclude(
            codename__in=[
                'add_logentry', 'change_logentry', 'delete_logentry', 'view_logentry',
                'add_theme', 'change_theme', 'delete_theme', 'view_theme',
                'add_group', 'change_group', 'delete_group', 'view_group',
                'add_permission', 'change_permission', 'delete_permission', 'view_permission',
                'add_contenttype', 'change_contenttype', 'delete_contenttype', 'view_contenttype',
                'add_session', 'change_session', 'delete_session', 'view_session',
                'add_government', 'delete_government', 'view_government',
                'add_country', 'delete_country', 'view_country',
                'add_decreecategory', 'delete_decreecategory', 'view_decreecategory',
                'add_doctype', 'delete_doctype', 'view_doctype',
                'add_comtype', 'delete_comtype', 'view_comtype',
                'add_periodictask', 'change_periodictask', 'delete_periodictask', 'view_periodictask',
                'add_periodictasks', 'change_periodictasks', 'delete_periodictasks', 'view_periodictasks',
                'add_clockedschedule', 'change_clockedschedule', 'delete_clockedschedule', 'view_clockedschedule',
                'add_crontabschedule', 'change_crontabschedule', 'delete_crontabschedule', 'view_crontabschedule',
                'add_intervalschedule', 'change_intervalschedule', 'delete_intervalschedule', 'view_intervalschedule',
                'add_solarschedule', 'change_solarschedule', 'delete_solarschedule', 'view_solarschedule',
                'add_customuser', 'change_customuser', 'delete_customuser', 'view_customuser',
                'add_useractivitylog', 'change_useractivitylog', 'delete_useractivitylog', 'view_useractivitylog',
            ]
        ))
        mid_point = len(permissions_list) // 2
        self.permissions_right = permissions_list[:mid_point]
        self.permissions_left = permissions_list[mid_point:]

        # Create two fields with only one column of permissions each
        self.fields["permissions_right"] = forms.ModelMultipleChoiceField(
            queryset=Permission.objects.filter(id__in=[p.id for p in self.permissions_right]),
            required=False,
            widget=forms.CheckboxSelectMultiple,
            label="الصلاحيـــات"
        )
        self.fields["permissions_left"] = forms.ModelMultipleChoiceField(
            queryset=Permission.objects.filter(id__in=[p.id for p in self.permissions_left]),
            required=False,
            widget=forms.CheckboxSelectMultiple,
            label=""
        )

        # Use Crispy Forms Layout helper
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "username",
            "email",
            "password1",
            "password2",
            HTML("<hr>"),  # Separator line
            Div(
                Div(Field("first_name", css_class="col-md-6"), css_class="col-md-6"),
                Div(Field("last_name", css_class="col-md-6"), css_class="col-md-6"),
                css_class="row"
            ),
            Div(
                Div(Field("phone", css_class="col-md-6"), css_class="col-md-6"),
                Div(Field("occupation", css_class="col-md-6"), css_class="col-md-6"),
                css_class="row"
            ),
            HTML("<hr>"),  # Separator line
            Div(
                Div(Field("permissions_right", css_class="col-md-6"), css_class="col-md-6"),
                Div(Field("permissions_left", css_class="col-md-6"), css_class="col-md-6"),
                css_class="row"
            ),
            "is_staff"
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        # Manually set permissions from both fields
        user.user_permissions.set(self.cleaned_data["permissions_left"] | self.cleaned_data["permissions_right"])
        return user

class CustomUserChangeForm(UserChangeForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="الصلاحيات"
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "phone", "occupation", "is_staff",  "permissions"]

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "اسم المستخدم"
        self.fields["email"].label = "البريد الإلكتروني"
        self.fields["first_name"].label = "الاسم الاول"
        self.fields["last_name"].label = "اللقب"
        self.fields["is_staff"].label = "صلاحيات انشاء و تعديل المستخدمين"
        
        # Split permissions queryset into two parts for 2 columns
        permissions_list = list(Permission.objects.exclude(
            codename__in=[
                'add_logentry', 'change_logentry', 'delete_logentry', 'view_logentry',
                'add_theme', 'change_theme', 'delete_theme', 'view_theme',
                'add_group', 'change_group', 'delete_group', 'view_group',
                'add_permission', 'change_permission', 'delete_permission', 'view_permission',
                'add_contenttype', 'change_contenttype', 'delete_contenttype', 'view_contenttype',
                'add_session', 'change_session', 'delete_session', 'view_session',
                'add_government', 'delete_government', 'view_government',
                'add_country', 'delete_country', 'view_country',
                'add_decreecategory', 'delete_decreecategory', 'view_decreecategory',
                'add_doctype', 'delete_doctype', 'view_doctype',
                'add_comtype', 'delete_comtype', 'view_comtype',
                'add_periodictask', 'change_periodictask', 'delete_periodictask', 'view_periodictask',
                'add_periodictasks', 'change_periodictasks', 'delete_periodictasks', 'view_periodictasks',
                'add_clockedschedule', 'change_clockedschedule', 'delete_clockedschedule', 'view_clockedschedule',
                'add_crontabschedule', 'change_crontabschedule', 'delete_crontabschedule', 'view_crontabschedule',
                'add_intervalschedule', 'change_intervalschedule', 'delete_intervalschedule', 'view_intervalschedule',
                'add_solarschedule', 'change_solarschedule', 'delete_solarschedule', 'view_solarschedule',
                'add_customuser', 'change_customuser', 'delete_customuser', 'view_customuser',
                'add_useractivitylog', 'change_useractivitylog', 'delete_useractivitylog', 'view_useractivitylog',
            ]
        ))
        mid_point = len(permissions_list) // 2
        self.permissions_right = permissions_list[:mid_point]
        self.permissions_left = permissions_list[mid_point:]

        # Get user's current permissions
        if user:
            user_permissions = set(user.user_permissions.all())  # Convert to a set for easy checking

            # Set initial values based on user's existing permissions
            initial_right = [p.id for p in self.permissions_right if p in user_permissions]
            initial_left = [p.id for p in self.permissions_left if p in user_permissions]
        else:
            initial_right = []
            initial_left = []

        # Create two fields with only one column of permissions each
        self.fields["permissions_right"] = forms.ModelMultipleChoiceField(
            queryset=Permission.objects.filter(id__in=[p.id for p in self.permissions_right]),
            required=False,
            widget=forms.CheckboxSelectMultiple,
            label="الصلاحيـــات",
            initial=initial_right  # Set initial selection
        )
        self.fields["permissions_left"] = forms.ModelMultipleChoiceField(
            queryset=Permission.objects.filter(id__in=[p.id for p in self.permissions_left]),
            required=False,
            widget=forms.CheckboxSelectMultiple,
            label="",
            initial=initial_left  # Set initial selection
        )

        # Use Crispy Forms Layout helper
        self.helper = FormHelper()
        self.helper.form_tag = False  # Disable the form tag for custom modal handling
        self.helper.layout = Layout(
            "username",
            "email",
            HTML("<hr>"),  # Separator line
            Div(
                Div(Field("first_name", css_class="col-md-6"), css_class="col-md-6"),
                Div(Field("last_name", css_class="col-md-6"), css_class="col-md-6"),
                css_class="row"
            ),
            Div(
                Div(Field("phone", css_class="col-md-6"), css_class="col-md-6"),
                Div(Field("occupation", css_class="col-md-6"), css_class="col-md-6"),
                css_class="row"
            ),
            HTML("<hr>"),  # Separator line
            Div(
                Div(Field("permissions_right", css_class="col-md-6"), css_class="col-md-6"),
                Div(Field("permissions_left", css_class="col-md-6"), css_class="col-md-6"),
                css_class="row"
            ),
            "is_staff",
            Button('reset_password', 'إعادة تعيين كلمة المرور', css_class="btn btn-primary", data_bs_toggle="modal", data_bs_target="#resetPasswordModal"),
        )


    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        # Manually set permissions from both fields
        user.user_permissions.set(self.cleaned_data["permissions_left"] | self.cleaned_data["permissions_right"])
        return user

class ResetPasswordForm(SetPasswordForm):  # ✅ Change from PasswordChangeForm to SetPasswordForm
    username = forms.CharField(label="اسم المستخدم", widget=forms.TextInput(attrs={"readonly": "readonly"}))

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['username'].initial = user.username  # Ensure username is displayed
        self.helper = FormHelper()
        self.fields["new_password1"].label = "كلمة المرور الجديدة"
        self.fields["new_password2"].label = "تأكيد كلمة المرور"
        self.helper.layout = Layout(
            Div(
                Field('username', css_class='col-md-12'),
                Field('new_password1', css_class='col-md-12'),
                Field('new_password2', css_class='col-md-12'),
                css_class='row'
            ),
            Submit('submit', 'تغيير كلمة المرور', css_class='btn btn-primary'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
