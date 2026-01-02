from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from .models import Doctor, Patient, Appointment, Billing
import urllib.parse

class AppointmentAdminForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        if doctor and date and time:
            conflicts = Appointment.objects.filter(
                doctor=doctor, 
                date=date, 
                time=time
            ).exclude(pk=self.instance.pk)
            
            if conflicts.exists():
                raise ValidationError(f"⚠️ STOP: Dr. {doctor.name} is booked at {time} on {date}.")
        
        return cleaned_data

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentAdminForm
    list_display = ('patient_name', 'doctor', 'date', 'time', 'status', 'whatsapp_button')
    list_filter = ('status', 'date', 'doctor')
    formfield_overrides = {
        models.TimeField: {'widget': forms.TimeInput(attrs={'type': 'time'})},
        models.DateField: {'widget': forms.DateInput(attrs={'type': 'date'})},
    }

    def patient_name(self, obj):
        return obj.patient.name

    def whatsapp_button(self, obj):
        message = (
            f"Hello {obj.patient.name}, \n"
            f"Your appointment is CONFIRMED! ✅\n\n"
            f"👨‍⚕️ Dr. {obj.doctor.name}\n"
            f"📅 {obj.date} at {obj.time}\n"
            f"📍 The Smile Space, Mumbai"
        )
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/91{obj.patient.phone}?text={encoded_message}"
        
        return format_html(
            '<a href="{}" target="_blank" style="background-color:#25D366; color:white; padding:5px 10px; border-radius:5px; text-decoration:none; font-weight:bold;">Notify</a>',
            whatsapp_url
        )
    whatsapp_button.short_description = "WhatsApp"

# --- UPGRADED BILLING SECTION ---
@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    # Show the math columns in the list
    list_display = ('patient', 'total_amount', 'amount_paid', 'get_pending', 'payment_status', 'invoice_button')
    list_filter = ('payment_status', 'date')
    
    # Helper to show Pending Amount in Red if money is remaining
    def get_pending(self, obj):
        pending = obj.pending_amount
        if pending > 0:
            return format_html('<span style="color:red; font-weight:bold;">₹{}</span>', pending)
        return format_html('<span style="color:green;">Settled</span>')
    get_pending.short_description = "Balance Due"

    def invoice_button(self, obj):
        pdf_link = f"http://127.0.0.1:8000/invoice/{obj.id}/"
        
        # Smart Message Logic
        if obj.pending_amount > 0:
            status_text = f"⚠️ *Payment Pending: ₹{obj.pending_amount}*"
        else:
            status_text = "✅ *Fully Paid*"

        message = (
            f"🧾 *INVOICE: The Smile Space* \n\n"
            f"Hello {obj.patient.name}, \n"
            f"Here is your billing summary:\n"
            f"🔗 *View PDF:* {pdf_link}\n\n"
            f"Total: ₹{obj.total_amount}\n"
            f"Paid: ₹{obj.amount_paid}\n"
            f"{status_text}"
        )
        
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/91{obj.patient.phone}?text={encoded_message}"
        
        return format_html(
            '<a href="{}" target="_blank" style="background-color:#3b82f6; color:white; padding:5px 10px; border-radius:5px; text-decoration:none; font-weight:bold;">Send Bill</a>',
            whatsapp_url
        )
    invoice_button.short_description = "Action"