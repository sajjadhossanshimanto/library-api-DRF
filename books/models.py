from django.db import models
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.utils import timezone


class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)
    biography = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author.name}"

    def save(self, *args, **kwargs):
        # Update available_copies on save
        if not self.pk:
            # New book
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)
        self.update_availability()

    def update_availability(self):
        borrowed_count = self.borrow_records.filter(is_returned=False).count()
        self.available_copies = self.total_copies - borrowed_count
        self.is_available = self.available_copies > 0
        Book.objects.filter(pk=self.pk).update(
            available_copies=self.available_copies,
            is_available=self.is_available
        )


class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    membership_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def borrowed_books_count(self):
        return self.borrow_records.filter(is_returned=False).count()


class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    is_returned = models.BooleanField(default=False)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['-borrow_date']
        indexes = [
            models.Index(fields=['member', 'is_returned']),
            models.Index(fields=['book', 'is_returned']),
        ]

    def __str__(self):
        return f"{self.member.name} borrowed {self.book.title}"

    def save(self, *args, **kwargs):
        # Set due date to 14 days from borrow_date if not set
        if not self.due_date:
            self.due_date = (timezone.now() + timedelta(days=14)).date()
        super().save(*args, **kwargs)

    def calculate_fine(self):
        if self.is_returned:
            if self.return_date > self.due_date:
                overdue_days = (self.return_date - self.due_date).days
                # Fine: 5 per day
                self.fine_amount = overdue_days * 5
            else:
                self.fine_amount = 0
        return self.fine_amount

    def mark_as_returned(self, return_date=None):
        self.is_returned = True
        self.return_date = return_date or timezone.now().date()
        self.calculate_fine()
        self.save()
        # Update book availability
        self.book.update_availability()
