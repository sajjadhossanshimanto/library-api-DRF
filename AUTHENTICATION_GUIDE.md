# Authentication, Permissions & API Documentation Implementation Guide

## ✅ Completed Tasks

### 1. Authentication Setup with Djoser & JWT ✓
- **Installed packages:**
  - `djangorestframework-simplejwt` - Token-based JWT authentication
  - `djoser` - User registration and authentication endpoints
  - `drf-yasg` - API documentation (Swagger UI & ReDoc)

- **Configured Settings:**
  - Updated `INSTALLED_APPS` with new packages
  - Set up JWT authentication with 1-hour access token lifetime and 7-day refresh token
  - Configured Djoser with email-login and custom serializers

### 2. Authentication Endpoints ✓
The following authentication endpoints are now available:

- **POST** `/auth/users/` - Register a new user
  - Required fields: `email`, `username`, `password`, `first_name`, `last_name`
  - Returns: User ID and created user data

- **POST** `/auth/jwt/create/` - Login and get JWT tokens
  - Required fields: `email`, `password`
  - Returns: `access` and `refresh` tokens

- **POST** `/auth/jwt/refresh/` - Refresh access token
  - Required fields: `refresh` token
  - Returns: New `access` token

- **POST** `/auth/jwt/verify/` - Verify token validity
  - Required fields: `token`
  - Returns: Token validation result

### 3. User Groups & Role-Based Permissions ✓
Two user groups have been created with different permission levels:

#### **Librarian Group** (Full Access)
- ✅ Can create, read, update, and delete books
- ✅ Can create, read, update, and delete authors
- ✅ Can manage members
- ✅ Can manage all borrow records
- ✅ Can view all data

#### **Member Group** (Read-Only)
- ✅ Can view books (read-only)
- ✅ Can view authors (read-only)
- ✅ Can view other members (read-only)
- ✅ Can view borrow records (read-only)
- ❌ Cannot create, update, or delete data

### 4. Custom Permission Classes ✓
Created `books/permissions.py` with the following permission classes:

- `IsLibrarian` - Only librarians can access
- `IsMember` - Only members can access
- `IsLibrarianOrReadOnly` - Librarians have full access, others read-only
- `IsLibrarianOrIsOwner` - Librarians can access all, members their own objects
- `CanBorrowAndReturn` - Members can borrow/return books

### 5. Protected API Endpoints ✓
All API endpoints are now protected with authentication and permissions:

```
Books Endpoints:
├─ GET/POST /api/books/ - Librarians can modify, Members can view
├─ GET /api/books/{id}/ - Authenticated users only
├─ PUT/DELETE /api/books/{id}/ - Librarians only
├─ GET /api/books/{id}/availability/ - Authenticated users
└─ GET /api/books/search/?q=query - Authenticated users

Authors Endpoints:
├─ GET/POST /api/authors/ - Librarians can modify, Members can view
├─ PUT/DELETE /api/authors/{id}/ - Librarians only
└─ GET /api/authors/{id}/ - Authenticated users

Members Endpoints:
├─ GET/POST /api/members/ - Librarians can modify, Members can view
├─ GET /api/members/{id}/borrowing_history/ - Authenticated users
└─ GET /api/members/{id}/active_loans/ - Authenticated users

Borrow Records Endpoints:
├─ GET /api/borrow-records/ - Authenticated users
├─ POST /api/borrow-records/borrow/ - Members can borrow books
├─ POST /api/borrow-records/{id}/return_book/ - Members can return
├─ GET /api/borrow-records/overdue/ - Authenticated users
└─ GET /api/borrow-records/member_loans/?member_id=X - Authenticated users
```

### 6. API Documentation with drf-yasg ✓
Swagger UI and ReDoc documentation are available:

- **Swagger UI:** http://127.0.0.1:8000/swagger/
- **ReDoc:** http://127.0.0.1:8000/redoc/

All endpoints include comprehensive docstrings explaining:
- What the endpoint does
- Required parameters
- Expected responses
- Permission requirements

## 📝 Steps to Test the API

### 1. Register a New User

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/auth/users/ \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"librarian@example.com\",
    \"username\": \"librarian\",
    \"password\": \"securepass123\",
    \"first_name\": \"John\",
    \"last_name\": \"Librarian\"
  }"
```

### 2. Get JWT Tokens

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"librarian@example.com\",
    \"password\": \"securepass123\"
  }"
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Add User to Librarian Group

Use Django admin or manage.py to add the user to the Librarian group:

**Via Django Admin:**
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to Users
3. Select the user
4. Add them to the Librarian group

**Via Django Shell:**
```bash
python manage.py shell
from django.contrib.auth.models import User, Group
user = User.objects.get(email='librarian@example.com')
group = Group.objects.get(name='Librarian')
user.groups.add(group)
```

### 4. Access Protected Endpoints with JWT Token

**Add Authorization Header:**
```bash
curl -X GET http://127.0.0.1:8000/api/books/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5. Test Permission Restrictions

**As Librarian (should succeed):**
```bash
curl -X POST http://127.0.0.1:8000/api/books/ \
  -H "Authorization: Bearer <librarian-token>" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"New Book\",
    \"isbn\": \"1234567890123\",
    \"author_id\": 1,
    \"category\": \"Fiction\"
  }"
```

**As Member (should fail with 403 Forbidden):**
```bash
curl -X POST http://127.0.0.1:8000/api/books/ \
  -H "Authorization: Bearer <member-token>" \
  -H "Content-Type: application/json" \
  -d "{...}"
```

## 🔧 Setup Groups Command

The `setup_groups` management command has been created to automatically set up user groups:

```bash
python manage.py setup_groups
```

**Output:**
```
✓ Created Librarian group
✓ Created Member group
📚 Assigning permissions to Librarian group...
✓ Assigned 16 permissions to Librarian
👥 Assigning permissions to Member group...
✓ Assigned 10 permissions to Member
✓ User groups setup completed successfully!
```

## 💾 File Structure

```
books/
├── models.py - Book, Author, Member, BorrowRecord models
├── views.py - ViewSets with authentication & permissions
├── serializers.py - Serializers including custom Djoser ones
├── permissions.py - Custom permission classes
├── urls.py - API routing
├── admin.py
└── management/
    └── commands/
        └── setup_groups.py - Group creation command

library_api/
├── settings.py - Installed apps, REST framework, JWT, Djoser config
├── urls.py - Main URL routing with Djoser, JWT, and drf-yasg
└── wsgi.py

manage.py - Django management script
```

## 🔐 Security Features Implemented

1. **JWT Token Authentication**
   - Short-lived access tokens (1 hour)
   - Refresh token rotation enabled
   - Token blacklisting support

2. **Role-Based Permission System**
   - Librarian: Full access to all resources
   - Member: Read-only access
   - Custom permission classes for specialized access

3. **Endpoint Protection**
   - All API endpoints require authentication
   - Write operations restricted by role
   - Display different response based on user role

## 📚 API Examples Using DRF Browsable API

1. Navigate to http://127.0.0.1:8000/api/books/
2. If not authenticated, click "Log in" in the top right
3. Enter JWT token in the format: `Bearer <token>`
4. Browse and test endpoints with authentication

## ✨ Swagger Documentation Features

The API documentation includes:
- ✅ All endpoints listed with descriptions
- ✅ Request/response schemas
- ✅ Authentication section showing JWT setup
- ✅ Try-it-out feature to test endpoints
- ✅ Field-level documentation
- ✅ Permission requirements for each endpoint

## 🚀 Next Steps (Optional)

1. **Email Verification:** Enable `SEND_CONFIRMATION_EMAIL` in settings
2. **Token Blacklist:** Implement token blacklisting for logout
3. **Social Authentication:** Add Google/GitHub login
4. **Rate Limiting:** Add throttling to prevent abuse
5. **CORS:** Configure CORS for frontend applications
6. **Tests:** Add unit and integration tests
7. **Deployment:** Deploy to production with proper security settings

## ⚠️ Important Notes

- **Development Only:** Current settings have `DEBUG=True` and use SQLite
- **Secret Key:** Change `SECRET_KEY` in production
- **Allowed Hosts:** Update `ALLOWED_HOSTS` for production
- **CORS:** Add CORS configuration if serving from different domain
- **HTTPS:** Always use HTTPS in production

## 📞 Support

For issues or questions:
1. Check the Swagger documentation at `/swagger/`
2. Review the ReDoc documentation at `/redoc/`
3. Check Django/DRF documentation
4. Review Djoser documentation: https://djoser.readthedocs.io/
5. Review drf-yasg documentation: https://drf-yasg.readthedocs.io/

---

**Module 2 Implementation Complete!** 🎉
