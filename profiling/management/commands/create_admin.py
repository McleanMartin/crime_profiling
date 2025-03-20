from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from profiling.models import CustomUser

class Command(BaseCommand):
    help = 'Remove all data and create a default admin user'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Removing all existing data..."))

        # Delete all existing data
        self.delete_all_data()

        # Create a default admin user
        self.create_default_admin()

        self.stdout.write(self.style.SUCCESS("Default admin user created successfully!"))

    def delete_all_data(self):
        """Delete all data from the database."""
        # Delete all users except the superuser (if any)
        CustomUser.objects.all().delete()

        # Delete all groups
        Group.objects.all().delete()

        # Delete all other models (Crime, Party, JudicialCase, Investigation, etc.)
        from profiling.models import Crime, Party, JudicialCase, Investigation
        Crime.objects.all().delete()
        Party.objects.all().delete()
        JudicialCase.objects.all().delete()
        Investigation.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("All existing data deleted."))

    def create_default_admin(self):
        """Create a default admin user."""
        email = "mypolicetxt@gmail.com"
        password = "pa22w0rd"
        role = "magistrate"
        department = "homicide"

        # Check if the user already exists
        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User with email {email} already exists."))
            return

        # Create the user
        user = CustomUser.objects.create_user(
            username="Admin",
            email=email,
            password=password,
            role=role,
            department=department,
            first_name="Admin",
            last_name="User",
            is_staff=True,  # Grant staff permissions
            is_superuser=True  # Grant superuser permissions
        )

        self.stdout.write(self.style.SUCCESS(f"Default admin user created: {user.email}"))