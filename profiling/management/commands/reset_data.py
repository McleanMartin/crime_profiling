from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from profiling.models import CustomUser
from faker import Faker  # For generating fake names
import os

class Command(BaseCommand):
    help = 'Remove all data, create a default admin user, and create users for each role with one-word usernames. Export users to users.txt.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Removing all existing data..."))

        # Delete all existing data
        self.delete_all_data()

        # Create a default admin user
        self.create_default_admin()

        # Create users for each role with one-word usernames
        users = self.create_role_users()

        # Export users to users.txt
        self.export_users_to_file(users)

        self.stdout.write(self.style.SUCCESS("Default admin user and role users created successfully!"))

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
            username="admin",
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

    def create_role_users(self):
        """Create users for each role with one-word usernames."""
        fake = Faker()  # Initialize Faker for fake names
        roles = [role[0] for role in CustomUser.ROLE_CHOICES]  # Get all roles from ROLE_CHOICES
        password = "pa22w0rd"  # Same password for all users
        department = "homicide"  # Default department
        users = []  # Store user details for exporting

        for role in roles:
            email = f"{role.replace(' ', '_').lower()}@example.com"
            first_name = fake.first_name()  # Generate a fake first name
            last_name = fake.last_name()  # Generate a fake last name
            username = first_name.lower()  # Use the first name as the username (one word)

            # Check if the user already exists
            if CustomUser.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"User with email {email} already exists."))
                continue

            # Create the user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                department=department,
                first_name=first_name,
                last_name=last_name,
                is_staff=True  # Grant staff permissions
            )

            # Add user details to the list
            users.append({
                'username': username,
                'email': email,
                'password': password,
                'role': role,
                'first_name': first_name,
                'last_name': last_name
            })

            self.stdout.write(self.style.SUCCESS(f"User created for role {role}: {user.email}"))

        return users

    def export_users_to_file(self, users):
        """Export user details to a file named users.txt."""
        file_path = "users.txt"
        with open(file_path, "w") as file:
            for user in users:
                file.write(
                    f"Username: {user['username']}\n"
                    f"Email: {user['email']}\n"
                    f"Password: {user['password']}\n"
                    f"Role: {user['role']}\n"
                    f"First Name: {user['first_name']}\n"
                    f"Last Name: {user['last_name']}\n"
                    f"{'-' * 40}\n"
                )

        self.stdout.write(self.style.SUCCESS(f"User details exported to {file_path}"))