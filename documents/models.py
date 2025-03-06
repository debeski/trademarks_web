# Imports of the required python modules and libraries
######################################################
from django.db import models
import uuid
import os
import json
from django.http import JsonResponse
from datetime import datetime, time
import random
import string
from django.core.validators import FileExtensionValidator
from django.db.models import Max
from django.core.exceptions import ValidationError

# Status Choices Lists:
#######################
class DecreeStatus(models.IntegerChoices):
    ACCEPT = 1, "قبول"
    REJECT = 2, "رفض"
    WITHDRAW = 3, "سحب"
    CANCEL = 4, "الغاء"

class PublicationStatus(models.IntegerChoices):
    INITIAL = 1, "نشر مبدئي"
    CONFLICT = 2, "متنازع عليه"
    FINAL = 3, "نشر نهائي"
    WITHDRAW = 4, "مسحوب"

class ObjectionStatus(models.IntegerChoices):
    PENDING = 1, "في انتظار الدفع"
    UNCONFIRM = 2, "في انتظار التأكيد"
    PAID = 3, "تم الدفع"
    ACCEPT = 4, "موافقة"
    REJECT = 5, "رفض"


# Helper Functions:
###################
def generate_random_filename(instance, filename):
    """Generate a random filename with the same extension as the uploaded file."""
    # Get the file extension
    file_name, file_extension = os.path.splitext(filename)
    
    # Generate a random filename with the same extension
    random_filename = f"{uuid.uuid4().hex}{file_extension}"
    
    # Get the model name and format the upload path
    model_name = instance.__class__.__name__.lower()
    
    # Return the full path where the file will be uploaded
    return f'{model_name}/{random_filename}'

def default_created_at():
    today = datetime.today().date()
    return datetime.combine(today, time(15, 0))

def generate_unique_code():
    # Generate a 13-digit random number
    return ''.join(random.choices(string.digits, k=13))


# Section Models:
#################
class Country(models.Model):
    """Model representing a government entity."""
    en_name = models.CharField(max_length=255, unique=True, verbose_name="الاسم بالانجليزية")
    ar_name = models.CharField(max_length=255, unique=True, verbose_name="الاسم بالعربية")

    class Meta:
        verbose_name = "دولة"
        verbose_name_plural = "الدول"
        
    def __str__(self):
        return self.ar_name

    @classmethod
    def get_table_class(cls):
        return 'documents.tables.CountryTable'

    @classmethod
    def get_filter_class(cls):
        return 'documents.filters.CountryFilter'

    @classmethod
    def get_form_class(cls):
        return 'documents.forms.CountryForm'

class Government(models.Model):
    """Model representing a government entity."""
    name = models.CharField(max_length=255, unique=True, verbose_name="الاسم")
        
    class Meta:
        verbose_name = "حكومة"
        verbose_name_plural = "الحكومات"
        
    def __str__(self):
        return self.name

    @classmethod
    def get_table_class(cls):
        return 'documents.tables.GovernmentTable'

    @classmethod
    def get_filter_class(cls):
        return 'documents.filters.GovernmentFilter'

    @classmethod
    def get_form_class(cls):
        return 'documents.forms.GovernmentForm'

class ComType(models.Model):
    """Model representing a government entity."""
    name = models.CharField(max_length=255, unique=True, verbose_name="الاسم")

    class Meta:
        verbose_name = "نوع شركة"
        verbose_name_plural = "انواع الشركات"
        
    def __str__(self):
        return self.name

    @classmethod
    def get_table_class(cls):
        return 'documents.tables.ComTypeTable'

    @classmethod
    def get_filter_class(cls):
        return 'documents.filters.ComTypeFilter'

    @classmethod
    def get_form_class(cls):
        return 'documents.forms.ComTypeForm'

class DocType(models.Model):
    """Model representing a government entity."""
    name = models.CharField(max_length=255, unique=True, verbose_name="الاسم")

    class Meta:
        verbose_name = "نوع مستند"
        verbose_name_plural = "انواع المستندات"
        
    def __str__(self):
        return self.name

    @classmethod
    def get_table_class(cls):
        return 'documents.tables.DocTypeTable'

    @classmethod
    def get_filter_class(cls):
        return 'documents.filters.DocTypeFilter'

    @classmethod
    def get_form_class(cls):
        return 'documents.forms.DocTypeForm'

class DecreeCategory(models.Model):
    """Model representing a government entity."""
    number = models.IntegerField(unique=True, verbose_name="رقم الفئة")
    name = models.CharField(max_length=999, unique=True, verbose_name="محتوى الفئة")

    class Meta:
        verbose_name = "الفئة"
        verbose_name_plural = "الفئات"
        
    def __str__(self):
        return str(self.number)

    @classmethod
    def get_table_class(cls):
        return 'documents.tables.DecreeCategoryTable'

    @classmethod
    def get_filter_class(cls):
        return 'documents.filters.DecreeCategoryFilter'

    @classmethod
    def get_form_class(cls):
        return 'documents.forms.DecreeCategoryForm'


# Primary Models:
##################
class Decree(models.Model):
    """Model representing a minister decree."""
    number = models.IntegerField(blank=False, null=False, verbose_name="رقم القرار")
    date = models.DateField(blank=False, verbose_name="تاريخ القرار")
    status = models.IntegerField(choices=DecreeStatus.choices, default=DecreeStatus.ACCEPT, verbose_name="حالة القرار")

    applicant = models.CharField(max_length=255, blank=True, null=True, verbose_name="مقدم الطلب")
    company = models.CharField(max_length=255, blank=True, null=True, verbose_name="صاحب العلامة")
    country = models.ForeignKey(Country, on_delete=models.PROTECT,  verbose_name="الدولة", blank=True, null=True)
    date_applied = models.DateField(blank=True, null=True, verbose_name="تاريخ التقديم")
    number_applied = models.IntegerField(blank=True, null=True, verbose_name="رقم القيد")

    ar_brand = models.CharField(max_length=255, blank=True, null=True, verbose_name="العلامة (عربي)")
    en_brand = models.CharField(max_length=255, blank=True, null=True, verbose_name="العلامة (انجليزي)")
    category = models.ForeignKey(DecreeCategory, on_delete=models.PROTECT, verbose_name="الفئة", blank=True, null=True)

    pdf_file = models.FileField(upload_to=generate_random_filename, blank=True, verbose_name="ملف القرار", validators=[FileExtensionValidator(allowed_extensions=['pdf'], message="يرجى رفع ملف PDF فقط.")])
    attach = models.FileField(upload_to=generate_random_filename, blank=True, verbose_name="المرفقات", validators=[FileExtensionValidator(allowed_extensions=['pdf'], message="يرجى رفع ملف PDF فقط.")])
    notes = models.TextField(max_length=999, blank=True, verbose_name="ملاحظات")

    is_published = models.BooleanField(default=False, verbose_name="تم اشهاره مبدئيا")
    is_withdrawn = models.BooleanField(default=False, verbose_name="تم سحبه")
    is_canceled = models.BooleanField(default=False, verbose_name="تم الغاءه")
    number_canceled = models.CharField(blank=True, null=True, verbose_name="رقم القرار المسحوب او الملغي")
    is_placeholder = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "قرار" 
        verbose_name_plural = "قرارات" 
        ordering = ['-is_placeholder','-id']
        permissions = [
            ("download_doc", " تحميل الملفات "),
        ]

    def __str__(self):
        return str(self.number) + ' / ' +  str(self.date.year)

    @classmethod
    def get_table_class(cls):
        return 'documents.tables.DecreeTable'

    @classmethod
    def get_filter_class(cls):
        return 'documents.filters.DecreeFilter'

    @classmethod
    def get_form_class(cls):
        return 'documents.forms.DecreeForm'

class Publication(models.Model):
    """Model representing a minister decree."""
    year = models.IntegerField(null=True, blank=True)
    number = models.IntegerField(blank=False, null=False, verbose_name="ر.ت")
    decree = models.ForeignKey(Decree, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رقم القرار")
    decree_number = models.IntegerField(blank=False, null=False, verbose_name="رقم القرار")

    applicant = models.CharField(max_length=255, blank=False, verbose_name="طالب التسجيل")
    owner = models.CharField(max_length=255, blank=False, verbose_name="مالك العلامة")
    country = models.ForeignKey(Country, on_delete=models.PROTECT,  verbose_name="الدولة")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="العنوان")
    date_applied = models.DateField(blank=False, verbose_name="تاريخ التقديم")
    number_applied = models.IntegerField(blank=False, verbose_name="رقم التسجيل")
    ar_brand = models.CharField(max_length=255, blank=False, verbose_name="العلامة (عربي)")
    en_brand = models.CharField(max_length=255, blank=False, verbose_name="العلامة (انجليزي)")
    category = models.ForeignKey(DecreeCategory, on_delete=models.PROTECT, verbose_name="الفئة")
    
    img_file = models.ImageField(upload_to=generate_random_filename, blank=True, null=True, verbose_name="الصورة")
    attach = models.FileField(upload_to=generate_random_filename, blank=True, null=True, verbose_name="المرفقات", validators=[FileExtensionValidator(allowed_extensions=['pdf'], message="يرجى رفع ملف PDF فقط.")])
    e_number = models.IntegerField(blank=False, null=False, verbose_name="رقم النشرية")
    status = models.IntegerField(choices=PublicationStatus.choices, default=PublicationStatus.INITIAL, verbose_name="حالة التسجيل")
    
    is_hidden = models.BooleanField(default=False, verbose_name="مخفي")
    notes = models.TextField(max_length=999, blank=True, null=True, verbose_name="ملاحظات")
    
    objection_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الاعتراض")
    is_objected = models.BooleanField(default=False, verbose_name="تم الاعتراض عليه")
    
    created_at = models.DateTimeField(default=default_created_at, verbose_name="تاريخ النشر")
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "اشهار" 
        verbose_name_plural = "اشهارات" 
        ordering = ['-id']
        permissions = [
            ("gen_pub_pdf", " انشاء PDF اشهار مبدئي "),
            ("pub_change_status", " تغيير حالة إشهار من مبدئي الى نهائي "),
        ]

    def save(self, *args, **kwargs):
        # Check if we are updating an existing record
        if self.pk:
            # Exclude the current instance from the check
            existing_publications = Publication.objects.filter(
                number=self.number,
                created_at__year=self.created_at.year if self.created_at else datetime.now().year
            ).exclude(pk=self.pk)  # Exclude the current object
            
            if existing_publications.exists():
                raise ValidationError(f"الرقم {self.number} موجود بالفعل في السنة {self.created_at.year}. يرجى استخدام رقم مختلف.")
        
        # Call the parent save method
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.number)

    @staticmethod
    def get_table_class(context="default"):
        """Returns the appropriate table class based on context."""
        if context == "objection_pub_pick":
            return "documents.tables.ObjectionPubPickTable"
        return "documents.tables.PublicationTable"

    @staticmethod
    def get_filter_class(context="default"):
        """Returns the appropriate table class based on context."""
        if context == "objection_pub_pick":
            return "documents.filters.ObjectionPubPickFilter"
        return "documents.filters.PublicationFilter"

    @classmethod
    def get_form_class(cls):
        return 'documents.forms.PublicationForm'

class Objection(models.Model):
    """Model representing a minister decree."""
    number = models.IntegerField(blank=False, null=False, verbose_name="ر.ت")
    pub = models.ForeignKey(Publication, on_delete=models.PROTECT, verbose_name="الاشهار")
    name = models.CharField(max_length=64, blank=False, null=False, verbose_name="اسم ولقب مقدم الشكوى")
    job = models.CharField(max_length=24, blank=False, null=False, verbose_name="المهنة")
    nationality = models.ForeignKey(Country, on_delete=models.PROTECT,  verbose_name="الجنسية")
    address = models.CharField(max_length=255, blank=False, verbose_name="محل الاقامة")
    phone = models.CharField(max_length=10, blank=False, verbose_name="رقم الهاتف")
    
    com_name = models.CharField(max_length=255, blank=False, verbose_name="اسم الشركة المقدمة للشكوى")
    com_job = models.ForeignKey(ComType, on_delete=models.PROTECT,  verbose_name="غرض الشركة")
    com_address = models.CharField(max_length=255, blank=False, verbose_name="عنوان الشركة")
    com_og_address = models.CharField(max_length=255, blank=False, verbose_name="عنوان المقر الرئيسي للشركة")
    com_mail_address = models.CharField(max_length=255, blank=False, verbose_name="عنوان البريد الرئيسي لاستلام المكاتبات المتعلقة بالمعارضة")
    
    status = models.IntegerField(choices=ObjectionStatus.choices, default=ObjectionStatus.PENDING, verbose_name="حالة الاعتراض")
    reason = models.CharField(max_length=100, verbose_name="اسباب الرفض", blank=True)
    pdf_file = models.FileField(upload_to=generate_random_filename, blank=True, verbose_name="ملف الاعتراض", validators=[FileExtensionValidator(allowed_extensions=['pdf'], message="يرجى رفع ملف PDF فقط.")])
    notes = models.TextField(max_length=999, blank=True, verbose_name="تفاصيل")
    
    is_paid = models.BooleanField(default=False, verbose_name="تم دفع الرسوم")
    receipt_file = models.FileField(upload_to=generate_random_filename, blank=True, verbose_name="ايصال الدفع")
    unique_code = models.CharField(max_length=13, unique=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ تقديم الاعتراض")
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "اعتراض" 
        verbose_name_plural = "اعتراضات" 
        ordering = ['-id']
        permissions = [
            ("confirm_objection_fee", " قبول او رفض ايصال رسوم اعتراض "),
            ("confirm_objection_status", " قبول او رفض اعتراض "),
        ]

    def save(self, *args, **kwargs):
        self.created_at = datetime.now()
        if not self.number:
            current_year = self.created_at.year  # Extract the year from the created_at field
            
            # Get the maximum number for the current year
            last_objection = Objection.objects.filter(created_at__year=current_year).aggregate(Max('number'))['number__max']
            
            # If there are objections for the current year, increment the highest number, otherwise start at 1
            if last_objection:
                self.number = last_objection + 1
            else:
                self.number = 1
                
        super().save(*args, **kwargs)

        # Generate a unique code only if the object is being created (not updated)
        if not self.unique_code:
            self.unique_code = generate_unique_code()
            # Ensure the code is unique
            while Objection.objects.filter(unique_code=self.unique_code).exists():
                self.unique_code = generate_unique_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.number)

    @classmethod
    def get_table_class(cls):
        return 'documents.tables.ObjectionTable'

    @classmethod
    def get_filter_class(cls):
        return 'documents.filters.ObjectionFilter'

    @staticmethod
    def get_form_class(context="default"):
        """Returns the appropriate form class based on context."""
        if context == "objection_pub_pick":
            return "documents.forms.ObjectionPubPickForm"
        return "documents.forms.ObjectionForm"

class FormPlus(models.Model):
    """Ambiguous Model representing a report of some sort."""
    number = models.CharField(max_length=20, blank=True, null=True, verbose_name="الرقم")
    date = models.DateField(verbose_name="التاريخ")
    government = models.ForeignKey(Government, on_delete=models.PROTECT, verbose_name="الحكومة", blank=True, null=True,)
    type = models.ForeignKey(DocType, on_delete=models.PROTECT,  verbose_name="النوع")
    title = models.CharField(max_length=255, blank=False, verbose_name="العنوان")
    keywords = models.TextField(max_length=999, blank=True, verbose_name="التفاصيل")
    pdf_file = models.FileField(upload_to=generate_random_filename, blank=False, verbose_name="ملف PDF", validators=[FileExtensionValidator(allowed_extensions=['pdf'], message="يرجى رفع ملف PDF فقط.")])
    word_file = models.FileField(upload_to=generate_random_filename, blank=True, verbose_name="ملف Word", validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx'], message="يرجى رفع ملف Word فقط.")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "تشريع او نموذج" 
        verbose_name_plural = "تشريعات و نماذج" 
        ordering = ['-id']
        permissions = [
            ("download_doc", " تحميل الملفات "),
        ]
    
    def __str__(self):
        return self.number

    @classmethod
    def get_table_class(cls):
        return 'documents.tables.FormPlusTable'

    @classmethod
    def get_filter_class(cls):
        return 'documents.filters.FormPlusFilter'

    @classmethod
    def get_form_class(cls):
        return 'documents.forms.FormPlusForm'
