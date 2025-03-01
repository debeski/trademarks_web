#############################################################################
# Pdf Generation Libraries
#############################################################################
import reportlab
from django.contrib.staticfiles import finders
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import arabic_reshaper
from bidi.algorithm import get_display
from decimal import Decimal
import os
from django.conf import settings
from PIL import Image

#############################################################################
# PDF Generation Fonts
#############################################################################
font_path = finders.find('fonts/Amiri-Regular.ttf')
pdfmetrics.registerFont(TTFont('Amiri', font_path))
font_path = finders.find('fonts/Amiri-Bold.ttf')
pdfmetrics.registerFont(TTFont('Amiri-bold', font_path))
font_path = finders.find('fonts/Amiri-Italic.ttf')
pdfmetrics.registerFont(TTFont('Amiri-italic', font_path))

#############################################################################

def process_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


def pub_pdf(pub_id, pub_record):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    c.setLineWidth(0)  # Ensures no border width

    # Paper header
    c.drawImage(finders.find('img/pub_pdf_logo.jpg'), width / 2.3, height - 100, width=80, height=80)
    c.setFont("Amiri-bold", 20)
    c.drawCentredString(width / 2, height - 125, process_arabic_text("حكومة الوحدة الوطنية"))
    c.drawCentredString(width / 2, height - 150, process_arabic_text("ديوان وزارة الاقتصاد والتجارة"))
    c.setFont("Amiri-bold", 14)
    c.drawCentredString(width / 2, height - 175, process_arabic_text("اشهار علامة تجارية"))

    c.line(30, height - 195, width - 30, height - 195)

    # Date and trans_id
    c.setFont("Amiri", 14)
    c.drawCentredString(width / 2, height - 225, process_arabic_text(f"طلب مقدم لتسجيل علامة تجارية رقم: ({pub_record['pub_no']})"))

    c.setFont("Amiri-bold", 15)
    c.drawRightString(565, height - 275, process_arabic_text("الرقم المسلسل للطلب كما قيد بسجل العلامات التجارية :"))
    c.drawRightString(565, height - 315, process_arabic_text("تاريخ الطلـــــب :"))
    c.drawRightString(565, height - 355, process_arabic_text("طالب التسجيل :"))
    c.drawRightString(565, height - 395, process_arabic_text("محل الاقامــــة :"))
    c.drawRightString(565, height - 435, process_arabic_text("الـــجــنــســيــــة :"))
    c.drawRightString(565, height - 475, process_arabic_text("الجهة التي يوجد بها المحل التجاري او مشروع الاستغلال :"))
    c.drawRightString(565, height - 515, process_arabic_text("العلامات التجارية المراد تسجيلها عن البضائع والمنتجات التابعة للفئة :"))
    c.drawRightString(565, height - 555, process_arabic_text("عدد النشريــــــة :"))
    c.drawRightString(565, height - 595, process_arabic_text("تاريخ النشريــــة :"))

    c.setFont("Amiri", 12)
    c.drawRightString(480, height - 317, process_arabic_text(f"{pub_record['date_applied']}"))
    c.drawRightString(480, height - 356, process_arabic_text(f"{pub_record['applicant']}"))
    c.drawRightString(480, height - 396, process_arabic_text(f"{pub_record['address']}"))
    c.drawRightString(480, height - 436, process_arabic_text(f"{pub_record['country']}"))
    c.drawRightString(270, height - 476, process_arabic_text(f"{pub_record['address']}"))
    c.drawRightString(480, height - 596, process_arabic_text(f"{pub_record['pub_date']}"))
    
    c.setFont("Amiri", 13)
    c.drawRightString(220, height - 516, process_arabic_text(f"{pub_record['category']}"))
    c.drawRightString(480, height - 556, process_arabic_text(f"{pub_record['e_number']}"))
    c.drawRightString(278, height - 276, process_arabic_text(f"{pub_record['pub_no']}"))
    
    img_filename = pub_record.get('pub_img', '').replace(settings.MEDIA_URL, '').lstrip('/')
    img_path = os.path.join(settings.MEDIA_ROOT, img_filename)

    if os.path.exists(img_path):
        try:
            with Image.open(img_path) as img:
                orig_width, orig_height = img.size  # Get original image dimensions
                
                max_height = 160  # Set max height
                aspect_ratio = orig_width / orig_height  # Calculate aspect ratio
                new_width = max_height * aspect_ratio  # Adjust width to maintain aspect ratio
                
                # Set fixed position for TOP-RIGHT corner
                fixed_right_x = width - 225 # 225 pixels from the right page border
                fixed_top_y = height - 550  # 550 pixels from the top
                
                # Calculate the correct x, y for ReportLab
                image_x = fixed_right_x - new_width  # Move left by image width
                image_y = fixed_top_y - max_height  # Move down by image height
                
                c.drawInlineImage(img_path, image_x, image_y, width=new_width, height=max_height)
        except Exception as e:
            print("Error processing image:", e)  # Debugging
    else:
        print("Image not found:", img_path)  # Debugging

    # Title
    c.setFont("Amiri-bold", 12)
    c.drawString(60, 80, process_arabic_text("مكتب العلامات التجارية"))

    # Footer
    c.setFillColor(colors.darkslategray)
    c.drawRightString(width - 70, 80, process_arabic_text("(QR)"))

    # Save PDF to the BytesIO buffer
    c.save()
    pdf_data = pdf_buffer.getvalue()  # Get PDF data from the buffer
    pdf_buffer.close()  # Close the buffer

    return pdf_data  # Return the PDF data


def pub_final_pdf(pub_id, pub_record):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    c.setLineWidth(0)  # Ensures no border width

    # Paper header
    c.drawImage(finders.find('img/pub_pdf_logo.jpg'), width / 2.3, height - 100, width=80, height=80)
    c.setFont("Amiri-bold", 20)
    c.drawCentredString(width / 2, height - 125, process_arabic_text("حكومة الوحدة الوطنية"))
    c.drawCentredString(width / 2, height - 150, process_arabic_text("ديوان وزارة الاقتصاد والتجارة"))
    c.setFont("Amiri-bold", 14)
    c.drawCentredString(width / 2, height - 175, process_arabic_text("شهادة تسجيل علامة تجارية"))

    c.line(30, height - 195, width - 30, height - 195)

    # Date and trans_id
    c.setFont("Amiri", 14)
    c.drawCentredString(width / 2, height - 225, process_arabic_text(f"طلب مقدم لتسجيل علامة تجارية رقم: ({pub_record['pub_no']})"))

    c.setFont("Amiri-bold", 15)
    c.drawRightString(565, height - 275, process_arabic_text("الرقم المسلسل للطلب كما قيد بسجل العلامات التجارية :"))
    c.drawRightString(565, height - 315, process_arabic_text("تاريخ الطلـــــب :"))
    c.drawRightString(565, height - 355, process_arabic_text("طالب التسجيل :"))
    c.drawRightString(565, height - 395, process_arabic_text("محل الاقامــــة :"))
    c.drawRightString(565, height - 435, process_arabic_text("الـــجــنــســيــــة :"))
    c.drawRightString(565, height - 475, process_arabic_text("الجهة التي يوجد بها المحل التجاري او مشروع الاستغلال :"))
    c.drawRightString(565, height - 515, process_arabic_text("العلامات التجارية المراد تسجيلها عن البضائع والمنتجات التابعة للفئة :"))
    c.drawRightString(565, height - 555, process_arabic_text("عدد النشريــــــة :"))
    c.drawRightString(565, height - 595, process_arabic_text("تاريخ النشريــــة :"))

    c.setFont("Amiri", 12)
    c.drawRightString(480, height - 317, process_arabic_text(f"{pub_record['date_applied']}"))
    c.drawRightString(480, height - 356, process_arabic_text(f"{pub_record['applicant']}"))
    c.drawRightString(480, height - 396, process_arabic_text(f"{pub_record['address']}"))
    c.drawRightString(480, height - 436, process_arabic_text(f"{pub_record['country']}"))
    c.drawRightString(270, height - 476, process_arabic_text(f"{pub_record['address']}"))
    c.drawRightString(480, height - 596, process_arabic_text(f"{pub_record['pub_date']}"))
    
    c.setFont("Amiri", 13)
    c.drawRightString(220, height - 516, process_arabic_text(f"{pub_record['category']}"))
    c.drawRightString(480, height - 556, process_arabic_text(f"{pub_record['e_number']}"))
    c.drawRightString(278, height - 276, process_arabic_text(f"{pub_record['pub_no']}"))
    
    img_filename = pub_record.get('pub_img', '').replace(settings.MEDIA_URL, '').lstrip('/')
    img_path = os.path.join(settings.MEDIA_ROOT, img_filename)

    if os.path.exists(img_path):
        try:
            with Image.open(img_path) as img:
                orig_width, orig_height = img.size  # Get original image dimensions
                
                max_height = 160  # Set max height
                aspect_ratio = orig_width / orig_height  # Calculate aspect ratio
                new_width = max_height * aspect_ratio  # Adjust width to maintain aspect ratio
                
                # Set fixed position for TOP-RIGHT corner
                fixed_right_x = width - 225 # 225 pixels from the right page border
                fixed_top_y = height - 550  # 550 pixels from the top
                
                # Calculate the correct x, y for ReportLab
                image_x = fixed_right_x - new_width  # Move left by image width
                image_y = fixed_top_y - max_height  # Move down by image height
                
                c.drawInlineImage(img_path, image_x, image_y, width=new_width, height=max_height)
        except Exception as e:
            print("Error processing image:", e)  # Debugging
    else:
        print("Image not found:", img_path)  # Debugging

    # Title
    c.setFont("Amiri-bold", 12)
    c.drawString(60, 80, process_arabic_text("مكتب العلامات التجارية"))

    # Footer
    c.setFillColor(colors.darkslategray)
    c.drawRightString(width - 70, 80, process_arabic_text("(QR)"))

    # Save PDF to the BytesIO buffer
    c.save()
    pdf_data = pdf_buffer.getvalue()  # Get PDF data from the buffer
    pdf_buffer.close()  # Close the buffer

    return pdf_data  # Return the PDF data


def obj_pdf(obj_id, obj_record):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    c.setLineWidth(0)  # Ensures no border width

    # Paper header
    c.drawImage(finders.find('img/pub_pdf_logo.jpg'), width / 2.3, height - 100, width=80, height=80)
    c.setFont("Amiri-bold", 20)
    c.drawCentredString(width / 2, height - 125, process_arabic_text("حكومة الوحدة الوطنية"))
    c.drawCentredString(width / 2, height - 150, process_arabic_text("ديوان وزارة الاقتصاد والتجارة"))
    c.setFont("Amiri-bold", 14)
    c.drawCentredString(width / 2, height - 175, process_arabic_text("مكتب العلامات التجارية"))

    c.line(30, height - 195, width - 30, height - 195)

    # Date and trans_id
    c.setFont("Amiri", 14)
    c.drawCentredString(width / 2, height - 230, process_arabic_text("اخطار بالمعارضة في تسجيل علامة تجارية"))

    c.setFont("Amiri-bold", 13)
    c.drawRightString(565, height - 275, process_arabic_text("بيــانــات مقدم المعارضــة :"))
    c.drawRightString(565, height - 315, process_arabic_text("رقم طلب التسجيل كما هو مقيد بمكتب العلامات التجارية :"))
    c.drawRightString(565, height - 355, process_arabic_text("اسم طالب التسجيل :"))
    c.drawRightString(565, height - 395, process_arabic_text("رقم النشرية الالكترونية التي اشهر فيها قبول تسجيل العلامة المعترض عليها :"))
    c.drawRightString(565, height - 435, process_arabic_text("تاريخ النشر :"))
    c.drawRightString(565, height - 475, process_arabic_text("اسم المعارض في تسجيل العلامة ولقبه :"))
    c.drawRightString(565, height - 515, process_arabic_text("مهنته :"))
    c.drawRightString(565, height - 555, process_arabic_text("جنسيته :"))
    c.drawRightString(565, height - 595, process_arabic_text("محل اقامته :"))
    c.drawRightString(565, height - 435, process_arabic_text("اسم الشركة (اذا كان المعارض شركة) :"))
    c.drawRightString(565, height - 475, process_arabic_text("عنوانها :"))
    c.drawRightString(565, height - 515, process_arabic_text("الغرض من الشركة :"))
    c.drawRightString(565, height - 555, process_arabic_text("عنوان مقرها الرئيسي :"))
    c.drawRightString(565, height - 595, process_arabic_text("عنوان البريد الرئيسي لاستلام المكاتبات المتعلقة بالمعارضة :"))
    c.drawRightString(565, height - 595, process_arabic_text("تاريخ تقديم المعارضة :"))

    # c.setFont("Amiri", 12)
    # c.drawRightString(480, height - 356, process_arabic_text(f"{obj_record['applicant']}"))
    # c.drawRightString(480, height - 396, process_arabic_text(f"{obj_record['address']}"))
    # c.drawRightString(480, height - 436, process_arabic_text(f"{obj_record['country']}"))
    # c.drawRightString(270, height - 476, process_arabic_text(f"{obj_record['address']}"))
    # c.drawRightString(480, height - 596, process_arabic_text(f"{obj_record['pub_date']}"))
    # c.drawRightString(220, height - 516, process_arabic_text(f"{obj_record['category']}"))
    # c.drawRightString(480, height - 556, process_arabic_text(f"{obj_record['e_number']}"))
    # c.drawRightString(278, height - 276, process_arabic_text(f"{obj_record['pub_no']}"))
    # c.drawRightString(480, height - 396, process_arabic_text(f"{obj_record['address']}"))
    # c.drawRightString(480, height - 436, process_arabic_text(f"{obj_record['country']}"))
    # c.drawRightString(270, height - 476, process_arabic_text(f"{obj_record['address']}"))
    # c.drawRightString(480, height - 596, process_arabic_text(f"{obj_record['pub_date']}"))
    # c.drawRightString(220, height - 516, process_arabic_text(f"{obj_record['category']}"))
    # c.drawRightString(480, height - 556, process_arabic_text(f"{obj_record['e_number']}"))

    c.line(30, height - 555, width - 30, height - 195)

    # Title
    c.setFont("Amiri-bold", 12)
    c.drawString(60, 80, process_arabic_text("مكتب العلامات التجارية"))

    # Footer
    c.setFillColor(colors.darkslategray)
    c.drawRightString(width - 70, 80, process_arabic_text("(QR)"))

    # Save PDF to the BytesIO buffer
    c.save()
    pdf_data = pdf_buffer.getvalue()  # Get PDF data from the buffer
    pdf_buffer.close()  # Close the buffer

    return pdf_data  # Return the PDF data
