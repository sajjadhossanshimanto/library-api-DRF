"""
Django management command to set up initial user groups for role-based access control.
This command creates two groups: Librarian and Member.
Run with: python manage.py setup_groups
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from books.models import Book, Author, Member, BorrowRecord


class Command(BaseCommand):
    help = 'Create initial user groups (Librarian, Member) with appropriate permissions'

    def handle(self, *args, **options):
        """
        Create and setup user groups with permissions.
        """
        # Create Librarian group
        librarian_group, created = Group.objects.get_or_create(name='Librarian')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Librarian group'))
        else:
            self.stdout.write('✓ Librarian group already exists')

        # Create Member group
        member_group, created = Group.objects.get_or_create(name='Member')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Member group'))
        else:
            self.stdout.write('✓ Member group already exists')

        # Get content types
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        member_ct = ContentType.objects.get_for_model(Member)
        borrow_ct = ContentType.objects.get_for_model(BorrowRecord)

        # Get all permissions
        all_perms = Permission.objects.filter(
            content_type__in=[book_ct, author_ct, member_ct, borrow_ct]
        )

        # Assign all permissions to Librarian group
        self.stdout.write('\n📚 Assigning permissions to Librarian group...')
        librarian_group.permissions.set(all_perms)
        self.stdout.write(self.style.SUCCESS(f'✓ Assigned {all_perms.count()} permissions to Librarian'))

        # Assign view-only permissions to Member group
        self.stdout.write('\n👥 Assigning permissions to Member group...')
        view_perms = Permission.objects.filter(codename__startswith='view_')
        member_group.permissions.set(view_perms)
        self.stdout.write(self.style.SUCCESS(f'✓ Assigned {view_perms.count()} permissions to Member'))

        self.stdout.write(self.style.SUCCESS('\n✓ User groups setup completed successfully!'))
        self.stdout.write('\nGroup Permissions Summary:')
        self.stdout.write('─' * 50)
        self.stdout.write('🔑 Librarian Group: Full access to all resources')
        self.stdout.write('   - Can create, read, update, delete books, authors, members')
        self.stdout.write('   - Can manage borrow records and view all data')
        self.stdout.write('\n👥 Member Group: Read-only access')
        self.stdout.write('   - Can view books, authors, members, and borrow records')
        self.stdout.write('   - Cannot create, update, or delete resources')
        self.stdout.write('─' * 50)
