from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from django.conf import settings
from io import BytesIO
from PIL import Image, ImageDraw
import os


def generate_certificate(user, course, test_result):
    """
    Generate a modern, elegant PDF certificate for course completion
    """
    buffer = BytesIO()
    
    # Create PDF in landscape mode
    width, height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Elegant gradient background
    # Main background - soft cream
    c.setFillColor(HexColor('#FAF8F3'))
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Decorative top gradient accent
    c.setFillColor(HexColor('#4F46E5'))
    c.rect(0, height-120, width, 120, fill=True, stroke=False)
    
    # Bottom accent bar
    c.setFillColor(HexColor('#10B981'))
    c.rect(0, 0, width, 15, fill=True, stroke=False)
    
    # Elegant border frame with gold accent
    c.setStrokeColor(HexColor('#D4AF37'))  # Gold
    c.setLineWidth(4)
    c.rect(25, 25, width-50, height-50, fill=False, stroke=True)
    
    # Inner decorative border
    c.setStrokeColor(HexColor('#4F46E5'))  # Indigo
    c.setLineWidth(1.5)
    c.rect(35, 35, width-70, height-70, fill=False, stroke=True)
    
    # Decorative corner elements (gold)
    c.setStrokeColor(HexColor('#D4AF37'))
    c.setLineWidth(3)
    corner_size = 40
    # Top-left
    c.line(35, height-35, 35+corner_size, height-35)
    c.line(35, height-35, 35, height-35-corner_size)
    # Top-right
    c.line(width-35, height-35, width-35-corner_size, height-35)
    c.line(width-35, height-35, width-35, height-35-corner_size)
    # Bottom-left
    c.line(35, 35, 35+corner_size, 35)
    c.line(35, 35, 35, 35+corner_size)
    # Bottom-right
    c.line(width-35, 35, width-35-corner_size, 35)
    c.line(width-35, 35, width-35, 35+corner_size)
    
    # Certificate title in elegant script style
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 56)
    c.drawCentredString(width/2, height-75, "SERTIFIKAT")
    
    # Decorative line under title
    c.setStrokeColor(HexColor('#D4AF37'))
    c.setLineWidth(2)
    c.line(width/2-120, height-85, width/2+120, height-85)
    
    # Subtitle with elegant font
    c.setFont("Helvetica-Oblique", 13)  # Italic
    c.setFillColor(HexColor('#4B5563'))
    c.drawCentredString(width/2, height-145, "Ushbu sertifikat faxr bilan quyidagi shaxsga beriladi:")
    
    # User photo or elegant initial circle
    photo_size = 100
    photo_x = width/2 - photo_size/2
    photo_y = height - 290
    
    try:
        if user.profile_picture:
            # Draw user photo with circular mask
            img_path = user.profile_picture.path
            img = Image.open(img_path)
            img = img.convert("RGB")
            
            # Create circular mask
            mask = Image.new('L', (photo_size*3, photo_size*3), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, photo_size*3, photo_size*3), fill=255)
            
            img = img.resize((photo_size*3, photo_size*3))
            output = Image.new('RGB', (photo_size*3, photo_size*3), (250, 248, 243))
            output.paste(img, (0, 0), mask)
            
            img_reader = ImageReader(output)
            c.drawImage(img_reader, photo_x-photo_size, photo_y-photo_size, 
                       width=photo_size*3, height=photo_size*3, mask='auto')
        else:
            # Elegant gradient circle for initials
            # Outer gold ring
            c.setStrokeColor(HexColor('#D4AF37'))
            c.setLineWidth(3)
            c.circle(width/2, photo_y + photo_size/2, photo_size/2 + 5, fill=False, stroke=True)
            
            # Inner gradient circle (indigo to purple)
            c.setFillColor(HexColor('#4F46E5'))
            c.circle(width/2, photo_y + photo_size/2, photo_size/2, fill=True, stroke=False)
            
            # Initials in elegant white
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont("Helvetica-BoldOblique", 48)
            initials = f"{user.first_name[0] if user.first_name else ''}{user.last_name[0] if user.last_name else ''}"
            c.drawCentredString(width/2, photo_y + photo_size/2 - 15, initials.upper())
    except Exception as e:
        print(f"Error adding photo: {e}")
        # Elegant default circle
        c.setStrokeColor(HexColor('#D4AF37'))
        c.setLineWidth(3)
        c.circle(width/2, photo_y + photo_size/2, photo_size/2 + 5, fill=False, stroke=True)
        c.setFillColor(HexColor('#4F46E5'))
        c.circle(width/2, photo_y + photo_size/2, photo_size/2, fill=True, stroke=False)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-BoldOblique", 48)
        initials = f"{user.first_name[0] if user.first_name else ''}{user.last_name[0] if user.last_name else ''}"
        c.drawCentredString(width/2, photo_y + photo_size/2 - 15, initials.upper())
    
    # User full name in elegant script with gold color - ITALIC
    c.setFillColor(HexColor('#D4AF37'))  # Gold color
    c.setFont("Helvetica-BoldOblique", 38)  # Italic
    full_name = f"{user.first_name} {user.last_name}"
    c.drawCentredString(width/2, height-320, full_name)
    
    # Decorative underline for name
    c.setStrokeColor(HexColor('#D4AF37'))
    c.setLineWidth(1.5)
    name_width = len(full_name) * 12
    c.line(width/2-name_width, height-332, width/2+name_width, height-332)
    
    # Course completion text in italic (more compact)
    c.setFont("Helvetica-Oblique", 13)
    c.setFillColor(HexColor('#6B7280'))
    c.drawCentredString(width/2, height-365, "Quyidagi onlayn ta'lim kursini muvaffaqiyatli tugatdi:")
    
    # Course name in prominent style
    c.setFont("Helvetica-BoldOblique", 22)
    c.setFillColor(HexColor('#4F46E5'))
    c.drawCentredString(width/2, height-400, f'"{course.name}"')
    
    # Test score in elegant box
    score_box_y = height - 450
    box_width = 380
    box_height = 45
    box_x = width/2 - box_width/2
    
    # Score box with gradient effect
    c.setFillColor(HexColor('#10B981'))
    c.roundRect(box_x, score_box_y, box_width, box_height, 10, fill=True, stroke=False)
    
    # Score text
    c.setFont("Helvetica-BoldOblique", 16)
    c.setFillColor(HexColor('#FFFFFF'))
    score_text = f"Natija: {test_result.percentage}%  •  {test_result.correct_answers}/{test_result.total_questions} to'g'ri javob"
    c.drawCentredString(width/2, score_box_y + 15, score_text)
    
    # Date and signature section with elegant design
    date_y = 120
    
    # Left side - Date
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(HexColor('#6B7280'))
    c.drawString(80, date_y + 20, "Berilgan sana:")
    
    # Date box
    c.setFillColor(HexColor('#F3F4F6'))
    c.roundRect(75, date_y - 15, 140, 30, 5, fill=True, stroke=False)
    c.setStrokeColor(HexColor('#4F46E5'))
    c.setLineWidth(1)
    c.roundRect(75, date_y - 15, 140, 30, 5, fill=False, stroke=True)
    
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HexColor('#1F2937'))
    c.drawCentredString(145, date_y - 5, test_result.submitted_at.strftime("%d.%m.%Y"))
    
    # Right side - Signature section
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(HexColor('#6B7280'))
    c.drawRightString(width-80, date_y + 20, "Tizim rahbari:")
    
    # Signature line (underline style)
    c.setStrokeColor(HexColor('#1F2937'))
    c.setLineWidth(1)
    sig_line_y = date_y - 5
    c.line(width-280, sig_line_y, width-80, sig_line_y)
    
    # Signature name ABOVE the line (handwriting style)
    c.setFont("Helvetica-BoldOblique", 18)  # Larger, italic for signature effect
    c.setFillColor(HexColor('#1F2937'))
    c.drawRightString(width-80, sig_line_y + 8, "X.U.Mirovna")
    
    # Seal/stamp placeholder (decorative circle)
    seal_x = width - 140
    seal_y = date_y - 10
    c.setStrokeColor(HexColor('#4F46E5'))
    c.setLineWidth(2)
    c.circle(seal_x, seal_y, 35, fill=False, stroke=True)
    c.setLineWidth(1)
    c.circle(seal_x, seal_y, 30, fill=False, stroke=True)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HexColor('#4F46E5'))
    c.drawCentredString(seal_x, seal_y + 5, "BuxDU")
    c.drawCentredString(seal_x, seal_y - 5, "2026")
    
    # Footer with source information
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(HexColor('#9CA3AF'))
    c.drawCentredString(width/2, 50, "Ushbu sertifikat Yosh Tadqiqotchi tizimidan olingan")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HexColor('#4F46E5'))
    c.drawCentredString(width/2, 38, "www.yoshtadqiqotchi.uz")
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor('#9CA3AF'))
    c.drawCentredString(width/2, 26, "Buxoro davlat universiteti • info@buxdu.uz")
    
    # Decorative elements at bottom corners
    c.setFillColor(HexColor('#D4AF37'))
    # Small decorative circles
    c.circle(60, 60, 4, fill=True, stroke=False)
    c.circle(width-60, 60, 4, fill=True, stroke=False)
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
