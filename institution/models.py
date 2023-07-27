from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings


class UserManager(BaseUserManager):
    def _create(self, institutions_email, institutions_full_name, institutions_short_name, employee_email, password, **extra_fields):
        if not institutions_email:
            raise ValueError("Enter your institution's email")
        
        if not employee_email:
            raise ValueError("Enter your email from work for us to confirm your connection to the institution")

        institutions_email = self.normalize_email(institutions_email)
        employee_email = self.normalize_email(employee_email)
        user = self.model(institutions_email=institutions_email, institutions_full_name=institutions_full_name, institutions_short_name=institutions_short_name, employee_email=employee_email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_user(self, institutions_email, institutions_full_name, institutions_short_name, employee_email, password, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('verified_user', False)
        self._create(institutions_email, institutions_full_name, institutions_short_name, employee_email, password, **extra_fields)

    def create_superuser(self, institutions_email, institutions_full_name, employee_email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('verified_user', True)
        self._create(institutions_email, institutions_full_name, institutions_short_name="N/A", employee_email=employee_email, password=password, **extra_fields)

class User(AbstractBaseUser):
    institutions_email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=128)
    institutions_full_name = models.CharField(max_length=128)
    institutions_short_name = models.CharField(max_length=90)
    employee_email = models.EmailField()
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    verified_user = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=10, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "institutions_email"
    REQUIRED_FIELDS = ["institutions_full_name", "employee_email"]

    def __str__(self):
        return self.institutions_email

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, obj=None):
        return self.is_staff
    
    def create_activation_code(self):
        code = get_random_string(10)
        self.activation_code = code
        self.save()
    
    def send_activation_email(self, action):
        if action.lower():
            message = f"Follow this link to activate your account:\nhttp://localhost:8000/institution/activate/{self.activation_code}/"
        else:
            message = f"Your conformation code: {self.activation_code}"
        
        send_mail(
            subject="Activate your institution's account on the Digitalized Queue System",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.institutions_email],
            fail_silently=False
        )
    
    @property
    def id(self):
        return self.institutions_email