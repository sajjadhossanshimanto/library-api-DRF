from django.contrib import admin
from .models import Author, Book, Member, BorrowRecord


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_created')
    search_fields = ('name', 'biography')
    ordering = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'available_copies', 'is_available', 'date_added')
    list_filter = ('category', 'is_available', 'date_added')
    search_fields = ('title', 'isbn', 'author__name', 'category')
    readonly_fields = ('available_copies', 'is_available', 'date_added')
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'isbn', 'author', 'category', 'description')
        }),
        ('Inventory', {
            'fields': ('total_copies', 'available_copies', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('date_added',),
            'classes': ('collapse',)
        }),
    )
    ordering = ('title',)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'membership_date', 'is_active', 'borrowed_books_count')
    list_filter = ('is_active', 'membership_date')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('membership_date',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Membership', {
            'fields': ('membership_date', 'is_active')
        }),
    )
    ordering = ('name',)


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'borrow_date', 'due_date', 'return_date', 'is_returned', 'fine_amount')
    list_filter = ('is_returned', 'borrow_date', 'due_date')
    search_fields = ('member__name', 'book__title', 'member__email')
    readonly_fields = ('borrow_date', 'fine_amount')
    fieldsets = (
        ('Borrowing Information', {
            'fields': ('book', 'member', 'borrow_date')
        }),
        ('Dates', {
            'fields': ('due_date', 'return_date', 'is_returned')
        }),
        ('Fines', {
            'fields': ('fine_amount',),
        }),
    )
    ordering = ('-borrow_date',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:  # Update operation
            obj.book.update_availability()
