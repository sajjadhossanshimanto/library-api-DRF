from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
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


class AuthorViewSet(viewsets.ModelViewSet):
    
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'biography']
    ordering_fields = ['name', 'date_created']
    ordering = ['name']


class BookViewSet(viewsets.ModelViewSet):
    
    queryset = Book.objects.all().select_related('author')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['title', 'isbn', 'author__name', 'category']
    ordering_fields = ['title', 'date_added', 'is_available']
    ordering = ['title']

    def get_serializer_class(self):
        
        if self.action == 'list':
            return BookListSerializer
        return BookDetailSerializer

    def perform_create(self, serializer):
        
        book = serializer.save()
        book.update_availability()

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        
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
    
    queryset = Member.objects.all().prefetch_related('borrow_records')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'membership_date', 'is_active']
    ordering = ['name']

    def get_serializer_class(self):
        
        if self.action == 'list':
            return MemberListSerializer
        return MemberDetailSerializer

    @action(detail=True, methods=['get'])
    def borrowing_history(self, request, pk=None):
        
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
        
        member = self.get_object()
        active_loans = member.borrow_records.filter(is_returned=False)
        serializer = BorrowRecordDetailSerializer(active_loans, many=True)
        return Response(serializer.data)


class BorrowRecordViewSet(viewsets.ModelViewSet):
    
    queryset = BorrowRecord.objects.all().select_related('book', 'member')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['member', 'book', 'is_returned']
    ordering_fields = ['borrow_date', 'due_date']
    ordering = ['-borrow_date']

    def get_serializer_class(self):
        
        if self.action in ['list', 'create']:
            return BorrowRecordDetailSerializer
        return BorrowRecordDetailSerializer

    @action(detail=False, methods=['post'])
    def borrow(self, request):
        
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
        
        today = timezone.now().date()
        overdue_records = BorrowRecord.objects.filter(
            is_returned=False,
            due_date__lt=today
        ).select_related('book', 'member')

        serializer = BorrowRecordDetailSerializer(overdue_records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def member_loans(self, request):
        
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

