# Library Management System - API Design Document

## Project Description

The **Library Management System API** is a RESTful web service built with Django REST Framework that enables efficient management of library operations. This system provides complete functionality for:

- **Book Management**: Add, update, view, and remove books from the library's collection
- **Author Management**: Maintain author information linked to books
- **Member Management**: Register and manage library members with their details
- **Borrowing System**: Track book borrowing and returning operations with dates and member information


---

## Database Schema (Models Definition)

### 1. Author Model
```
Fields:
- id: Primary Key (Auto-generated)
- name: CharField (max_length=255, unique)
- biography: TextField (optional)
- date_created: DateTimeField (auto_now_add)

Relationships:
- One-to-Many with Book (one author can write many books)
```

### 2. Book Model
```
Fields:
- id: Primary Key (Auto-generated)
- title: CharField (max_length=255)
- isbn: CharField (max_length=13, unique)
- author: ForeignKey to Author (related_name='books')
- category: CharField (max_length=100)
- description: TextField (optional)
- total_copies: PositiveIntegerField (default=1)
- available_copies: PositiveIntegerField (auto-calculated)
- is_available: BooleanField (auto-calculated based on available_copies)
- date_added: DateTimeField (auto_now_add)

Relationships:
- ForeignKey to Author
- One-to-Many with BorrowRecord
```

### 3. Member Model
```
Fields:
- id: Primary Key (Auto-generated)
- name: CharField (max_length=255)
- email: EmailField (unique)
- phone: CharField (max_length=15, optional)
- membership_date: DateField (auto_now_add)
- is_active: BooleanField (default=True)
- address: TextField (optional)

Relationships:
- One-to-Many with BorrowRecord
```

### 4. BorrowRecord Model
```
Fields:
- id: Primary Key (Auto-generated)
- book: ForeignKey to Book (related_name='borrow_records')
- member: ForeignKey to Member (related_name='borrow_records')
- borrow_date: DateTimeField (auto_now_add)
- due_date: DateField (auto-calculated, 14 days from borrow_date)
- return_date: DateField (null=True, optional)
- is_returned: BooleanField (default=False)
- fine_amount: DecimalField (calculated if overdue)

Relationships:
- ForeignKey to Book
- ForeignKey to Member
```

---

## API Endpoints Definition

### Books Management

| Method | Endpoint | Description | Action |
|--------|----------|-------------|--------|
| GET | `/api/books/` | Retrieve all books | List all books with pagination |
| POST | `/api/books/` | Add a new book | Create a new book record |
| GET | `/api/books/{id}/` | Retrieve book details | Get specific book with full details |
| PUT | `/api/books/{id}/` | Update book details | Modify book information |
| DELETE | `/api/books/{id}/` | Remove a book | Delete book from database |
| GET | `/api/books/search/?query=title` | Search books | Filter by title, author, category |

### Authors Management

| Method | Endpoint | Description | Action |
|--------|----------|-------------|--------|
| GET | `/api/authors/` | Retrieve all authors | List all authors |
| POST | `/api/authors/` | Add a new author | Create a new author record |
| GET | `/api/authors/{id}/` | Retrieve author details | Get author with their books |

### Members Management

| Method | Endpoint | Description | Action |
|--------|----------|-------------|--------|
| GET | `/api/members/` | Retrieve all members | List all library members |
| POST | `/api/members/` | Register new member | Create a new member |
| GET | `/api/members/{id}/` | Retrieve member details | Get member info with borrowing history |
| PUT | `/api/members/{id}/` | Update member details | Modify member information |
| DELETE | `/api/members/{id}/` | Remove a member | Deactivate member account |

### Borrowing Management

| Method | Endpoint | Description | Action |
|--------|----------|-------------|--------|
| POST | `/api/borrow/` | Borrow a book | Create borrowing record |
| POST | `/api/return/{record_id}/` | Return a book | Mark book as returned |
| GET | `/api/borrow-records/` | View all borrow records | List borrowing history |
| GET | `/api/borrow-records/?member_id=1` | Filter records by member | View member's borrowing history |
