# --- Add these imports at the top ---
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Billing
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Doctor, Appointment, Patient

def home(request):
    doctors = Doctor.objects.all()

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        doctor_id = request.POST.get('doctor')
        symptoms = request.POST.get('symptoms')
        
        doctor_obj = Doctor.objects.get(id=doctor_id)

        # --- 1. THE SLOT BLOCKER ---
        # Check if an appointment already exists for this Doctor + Date + Time
        if Appointment.objects.filter(doctor=doctor_obj, date=date, time=time).exists():
            messages.error(request, f"⚠️ Sorry, Dr. {doctor_obj.name} is already booked at {time} on that date. Please choose another time.")
            return render(request, 'core/index.html', {'doctors': doctors})

        # --- 2. If Slot is Free, Save it ---
        patient, created = Patient.objects.get_or_create(
            phone=phone,
            defaults={'name': name, 'age': 0}
        )
        
        Appointment.objects.create(
            patient=patient,
            doctor=doctor_obj,
            date=date,
            time=time,
            symptoms=symptoms,
            status='PENDING' # Admin will confirm this later
        )

        messages.success(request, "✅ Request Sent! We will confirm your appointment shortly.")
        return redirect('home')

    return render(request, 'core/index.html', {'doctors': doctors})
# --- Add this new function at the bottom ---
def generate_invoice(request, billing_id):
    # 1. Get the billing object
    billing_obj = Billing.objects.get(id=billing_id)
    
    # 2. Context data for the invoice
    context = {
        'bill': billing_obj,
        'patient': billing_obj.patient,
        'doctor': 'Dr. Uncle (Senior Orthodontist)', # You can make this dynamic if needed
    }
    
    # 3. Load the HTML template
    template_path = 'core/invoice_pdf.html'
    template = get_template(template_path)
    html = template.render(context)
    
    # 4. Create a PDF
    response = HttpResponse(content_type='application/pdf')
    # This line makes it download with a specific filename
    response['Content-Disposition'] = f'attachment; filename="Invoice_{billing_obj.patient.name}.pdf"'
    
    # 5. Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response