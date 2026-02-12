from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models
from django.db.models import Q
from .models import Author, Book, Member, BorrowRecord
from .serializers import (
    AuthorSerializer,
    BookDetailSerializer,
    BookListSerializer,
    MemberDetailSerializer,
    MemberListSerializer,
    BorrowRecordSerializer,
    BorrowRecordDetailSerializer
)
from .permissions import IsLibrarianOrReadOnly, CanBorrowAndReturn


class AuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing book authors.
    
    Endpoints:
    - GET /api/authors/ - List all authors
    - POST /api/authors/ - Create a new author (Librarians only)
    - GET /api/authors/{id}/ - Retrieve author details
    - PUT /api/authors/{id}/ - Update author (Librarians only)
    - DELETE /api/authors/{id}/ - Delete author (Librarians only)
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'biography']
    ordering_fields = ['name', 'date_created']
    ordering = ['name']


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books in the library.
    
    Permissions:
    - Members: Can view books and search (read-only)
    - Librarians: Full access (create, read, update, delete)
    
    Endpoints:
    - GET /api/books/ - List all books
    - POST /api/books/ - Create a new book (Librarians only)
    - GET /api/books/{id}/ - Retrieve book details
    - PUT /api/books/{id}/ - Update book (Librarians only)
    - DELETE /api/books/{id}/ - Delete book (Librarians only)
    - GET /api/books/{id}/availability/ - Check book availability
    - GET /api/books/search/?q=query - Search for books
    """
    queryset = Book.objects.all().select_related('author')
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['title', 'isbn', 'author__name', 'category']
    ordering_fields = ['title', 'date_added', 'is_available']
    ordering = ['title']

    def get_serializer_class(self):
        """Return detailed serializer for single book, list serializer for listings"""
        if self.action == 'list':
            return BookListSerializer
        return BookDetailSerializer

    def perform_create(self, serializer):
        """Create book and update availability"""
        book = serializer.save()
        book.update_availability()

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Get the availability status of a specific book.
        
        Returns:
        - id: Book ID
        - title: Book title
        - total_copies: Total copies in library
        - available_copies: Copies available for borrowing
        - borrowed_count: Copies currently borrowed
        - is_available: Boolean indicating if book is available
        """
        book = self.get_object()
        return Response({
            'id': book.id,
            'title': book.title,
            'total_copies': book.total_copies,
            'available_copies': book.available_copies,
            'borrowed_count': book.total_copies - book.available_copies,
            'is_available': book.is_available
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for books by title, author, ISBN, or category.
        
        Query Parameters:
        - q: Search query (required)
        
        Example: /api/books/search/?q=python
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        books = self.queryset.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(isbn__icontains=query) |
            Q(category__icontains=query)
        )
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)


class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing library members.
    
    Permissions:
    - Members: Can view members (read-only)
    - Librarians: Full access (create, read, update, delete)
    
    Endpoints:
    - GET /api/members/ - List all members
    - POST /api/members/ - Create a new member (Librarians only)
    - GET /api/members/{id}/ - Retrieve member details
    - PUT /api/members/{id}/ - Update member (Librarians only)
    - DELETE /api/members/{id}/ - Delete member (Librarians only)
    - GET /api/members/{id}/borrowing_history/ - Get member's borrowing history
    - GET /api/members/{id}/active_loans/ - Get member's current loans
    """
    queryset = Member.objects.all().prefetch_related('borrow_records')
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'membership_date', 'is_active']
    ordering = ['name']

    def get_serializer_class(self):
        """Return detailed serializer for single member, list serializer for listings"""
        if self.action == 'list':
            return MemberListSerializer
        return MemberDetailSerializer

    @action(detail=True, methods=['get'])
    def borrowing_history(self, request, pk=None):
        """
        Get the complete borrowing history of a member.
        
        Returns member details along with all borrow records.
        """
        member = self.get_object()
        borrow_records = member.borrow_records.all()
        serializer = BorrowRecordDetailSerializer(borrow_records, many=True)
        return Response({
            'member': MemberDetailSerializer(member).data,
            'borrowing_history': serializer.data,
            'total_borrowed': member.borrow_records.count(),
            'currently_borrowed': member.borrowed_books_count
        })

    @action(detail=True, methods=['get'])
    def active_loans(self, request, pk=None):
        """
        Get all active (not yet returned) loans for a member.
        
        Returns only borrow records where is_returned=False.
        """
        member = self.get_object()
        active_loans = member.borrow_records.filter(is_returned=False)
        serializer = BorrowRecordDetailSerializer(active_loans, many=True)
        return Response(serializer.data)


class BorrowRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing book borrowing records.
    
    Permissions:
    - Members: Can borrow and return books
    - Librarians: Full access to manage borrow records
    
    Endpoints:
    - GET /api/borrow-records/ - List all borrow records
    - POST /api/borrow-records/borrow/ - Borrow a book
    - GET /api/borrow-records/{id}/ - Retrieve borrow record details
    - POST /api/borrow-records/{id}/return_book/ - Return a book
    - GET /api/borrow-records/overdue/ - List overdue books
    - GET /api/borrow-records/member_loans/?member_id=X - Get member's loans
    """
    queryset = BorrowRecord.objects.all().select_related('book', 'member')
    permission_classes = [IsAuthenticated, CanBorrowAndReturn]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['member', 'book', 'is_returned']
    ordering_fields = ['borrow_date', 'due_date']
    ordering = ['-borrow_date']

    def get_serializer_class(self):
        """Always use detailed serializer for borrow records"""
        if self.action in ['list', 'create']:
            return BorrowRecordDetailSerializer
        return BorrowRecordDetailSerializer

    @action(detail=False, methods=['post'])
    def borrow(self, request):
        """
        Create a new borrow record when a member borrows a book.
        
        Request body:
        - book_id: ID of the book being borrowed
        - member_id: ID of the member borrowing the book
        
        Returns created borrow record with due date.
        """
        serializer = BorrowRecordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                book = Book.objects.get(id=request.data.get('book_id'))
                member = Member.objects.get(id=request.data.get('member_id'))

                if not member.is_active:
                    return Response(
                        {'error': 'Member is not active'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if not book.is_available:
                    return Response(
                        {'error': 'Book is not available for borrowing'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                borrow_record = serializer.save()
                book.update_availability()

                return Response(
                    BorrowRecordDetailSerializer(borrow_record).data,
                    status=status.HTTP_201_CREATED
                )
            except (Book.DoesNotExist, Member.DoesNotExist) as e:
                return Response(
                    {'error': f'{str(e.__class__.__name__)} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """
        Return a borrowed book by updating the borrow record.
        
        Updates the borrow record to mark the book as returned and records the return date.
        """
        borrow_record = self.get_object()

        if borrow_record.is_returned:
            return Response(
                {'error': 'This book has already been returned'},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrow_record.mark_as_returned()
        return Response(
            BorrowRecordDetailSerializer(borrow_record).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all overdue books (not returned and past due date).
        
        Returns list of borrow records where is_returned=False and due_date < today.
        """
        today = timezone.now().date()
        overdue_records = BorrowRecord.objects.filter(
            is_returned=False,
            due_date__lt=today
        ).select_related('book', 'member')

        serializer = BorrowRecordDetailSerializer(overdue_records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def member_loans(self, request):
        """
        Get all loans for a specific member.
        
        Query Parameters:
        - member_id: ID of the member (required)
        
        Returns all borrow records for the specified member.
        """
        member_id = request.query_params.get('member_id')
        if not member_id:
            return Response(
                {'error': 'member_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            member = Member.objects.get(id=member_id)
            records = member.borrow_records.all()
            serializer = BorrowRecordDetailSerializer(records, many=True)
            return Response(serializer.data)
        except Member.DoesNotExist:
            return Response(
                {'error': 'Member not found'},
                status=status.HTTP_404_NOT_FOUND
            )

