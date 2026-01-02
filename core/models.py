from django.db import models

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

class Patient(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    age = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    symptoms = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.patient.name} with {self.doctor.name}"

class Billing(models.Model):
    PAYMENT_STATUS = [
        ('paid', 'Fully Paid'),
        ('partial', 'Partial'),
        ('pending', 'Unpaid')
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    treatments = models.TextField(help_text="List treatments separated by comma")
    
    # NEW FIELDS FOR PARTIAL PAYMENT
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    date = models.DateField(auto_now_add=True)

    # Automatic Math: Calculate Pending Amount
    @property
    def pending_amount(self):
        return self.total_amount - self.amount_paid

    def __str__(self):
        return f"Bill for {self.patient.name}"