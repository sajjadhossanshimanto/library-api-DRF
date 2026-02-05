from rest_framework import serializers
from .models import Author, Book, Member, BorrowRecord


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'biography', 'date_created']
        read_only_fields = ['id', 'date_created']


class BookDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'isbn', 'author', 'author_id', 'category',
            'description', 'total_copies', 'available_copies', 'is_available',
            'date_added'
        ]
        read_only_fields = ['id', 'available_copies', 'is_available', 'date_added']


class BookListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'isbn', 'author_name', 'category',
            'available_copies', 'is_available'
        ]
        read_only_fields = ['id', 'available_copies', 'is_available']


class MemberDetailSerializer(serializers.ModelSerializer):
    borrowed_books_count = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            'id', 'name', 'email', 'phone', 'membership_date',
            'is_active', 'address', 'borrowed_books_count'
        ]
        read_only_fields = ['id', 'membership_date', 'borrowed_books_count']

    def get_borrowed_books_count(self, obj):
        return obj.borrowed_books_count


class MemberListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'membership_date', 'is_active']
        read_only_fields = ['id', 'membership_date']


class BorrowRecordSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.name', read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    member_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BorrowRecord
        fields = [
            'id', 'book', 'book_id', 'book_title', 'member', 'member_id',
            'member_name', 'borrow_date', 'due_date', 'return_date',
            'is_returned', 'fine_amount'
        ]
        read_only_fields = [
            'id', 'borrow_date', 'book_title', 'member_name', 'fine_amount'
        ]

    def create(self, validated_data):
        book_id = validated_data.pop('book_id')
        member_id = validated_data.pop('member_id')
        validated_data['book_id'] = book_id
        validated_data['member_id'] = member_id
        return super().create(validated_data)


class BorrowRecordDetailSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    member = MemberListSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    member_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BorrowRecord
        fields = [
            'id', 'book', 'book_id', 'member', 'member_id',
            'borrow_date', 'due_date', 'return_date', 'is_returned', 'fine_amount'
        ]
        read_only_fields = ['id', 'borrow_date', 'fine_amount']

    def create(self, validated_data):
        book_id = validated_data.pop('book_id', None)
        member_id = validated_data.pop('member_id', None)
        if book_id and member_id:
            validated_data['book_id'] = book_id
            validated_data['member_id'] = member_id
        return super().create(validated_data)
