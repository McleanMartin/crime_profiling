from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
import random
from datetime import datetime, timedelta
from faker import Faker
from profiling.models import CustomUser, Crime, Offender, JudicialCase, Investigation
import json

fake = Faker()

# List of Zimbabwean cities
ZIMBABWEAN_CITIES = [
    "Harare", "Bulawayo", "Chitungwiza", "Mutare", "Gweru", "Kwekwe", "Kadoma", "Masvingo",
    "Chinhoyi", "Norton", "Marondera", "Ruwa", "Chegutu", "Zvishavane", "Bindura", "Beitbridge",
    "Redcliff", "Victoria Falls", "Hwange", "Rusape", "Chiredzi", "Kariba", "Karoi", "Chipinge",
    "Gwanda", "Shurugwi", "Epworth", "Lupane", "Mazowe", "Murehwa"
]

class Command(BaseCommand):
    help = 'Generates dummy data for the crime profiling application'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating dummy data...")

        # Create Groups and Permissions
        self.create_groups_and_permissions()

        # Create CustomUsers
        self.create_custom_users()

        # Create Crimes
        self.create_crimes()

        # Create Offenders
        self.create_offenders()

        # Create JudicialCases
        self.create_judicial_cases()

        # Create Investigations
        self.create_investigations()

        self.stdout.write("Dummy data generation complete!")

    def create_groups_and_permissions(self):
        group_names = ['police', 'investigator', 'judge']
        for name in group_names:
            Group.objects.get_or_create(name=name)
        self.stdout.write("Groups and permissions created.")

    def create_custom_users(self):
        roles = ['police', 'investigator', 'judge']
        for _ in range(10):
            email = fake.email()
            username = email  # Use the email as the username
            role = random.choice(roles)
            phone_number = fake.numerify(text='###########')  # Generate a phone number with 11 digits
            phone_number = phone_number[:15]  # Ensure it doesn't exceed 15 characters
            department = fake.random_element(elements=('Homicide', 'Narcotics', 'Cyber Crime', 'Fraud', 'Traffic'))

            CustomUser.objects.create_user(
                username=username,  # Set the username to the email
                email=email,
                password='password123',
                role=role,
                phone_number=phone_number,
                department=department
            )
        self.stdout.write("CustomUsers created.")

    def create_crimes(self):
        """Generate dummy crime records with realistic descriptions."""
        users = CustomUser.objects.filter(role='police')  # Only police can report crimes
        crime_types = ['Murder', 'Theft', 'Burglary', 'Fraud', 'Assault', 'Drug Trafficking', 'Cyber Crime']
        
        # Realistic crime descriptions based on crime type
        crime_descriptions = {
            'Murder': [
                "Victim found with multiple stab wounds in a residential area. Suspect fled the scene.",
                "Body discovered in a remote location with gunshot wounds. Investigation ongoing.",
                "Domestic dispute escalated into fatal violence. Suspect in custody."
            ],
            'Theft': [
                "Jewelry and cash stolen from a residence during the daytime. No suspects identified.",
                "Vehicle broken into and valuables stolen. Security footage being reviewed.",
                "Shoplifting incident at a local supermarket. Suspect apprehended by security."
            ],
            'Burglary': [
                "Home invasion reported. Electronics and cash stolen while residents were away.",
                "Business premises broken into overnight. Safe was tampered with but not opened.",
                "Residential burglary reported. Suspects entered through an unlocked window."
            ],
            'Fraud': [
                "Elderly victim scammed out of savings through a fake investment scheme.",
                "Credit card fraud reported. Unauthorized transactions detected.",
                "Business email compromise led to a fraudulent transfer of funds."
            ],
            'Assault': [
                "Bar fight resulted in serious injuries. Suspects identified and arrested.",
                "Victim assaulted in a parking lot. Suspect fled before police arrived.",
                "Domestic assault reported. Victim sustained minor injuries."
            ],
            'Drug Trafficking': [
                "Large quantity of illegal drugs seized during a routine traffic stop.",
                "Drug bust at a suspected trafficking hub. Multiple arrests made.",
                "Undercover operation led to the discovery of a drug distribution network."
            ],
            'Cyber Crime': [
                "Phishing attack compromised sensitive company data. Investigation ongoing.",
                "Ransomware attack on a local business. Data encrypted and ransom demanded.",
                "Identity theft reported. Victim's bank accounts were accessed illegally."
            ]
        }

        for _ in range(20):  # Create 20 crimes
            crime_type = random.choice(crime_types)
            description = random.choice(crime_descriptions[crime_type])  # Select a realistic description
            location = random.choice(ZIMBABWEAN_CITIES)  # Use Zimbabwean cities for realism
            date_reported = fake.date_between(start_date='-4y', end_date='today')  # Random date within the last year
            status = random.choice(['reported', 'under_investigation', 'closed'])
            reported_by = random.choice(users)  # Assign a random police user
            tags = ', '.join(fake.words(nb=3))  # Add random tags for categorization

            Crime.objects.create(
                crime_type=crime_type,
                description=description,
                location=location,
                date_reported=date_reported,
                status=status,
                reported_by=reported_by,
                tags=tags
            )
        self.stdout.write("Dummy crime records with realistic descriptions created successfully.")

    def create_offenders(self):
        crimes = Crime.objects.all()
        for _ in range(15):
            offender = Offender.objects.create(
                name=fake.name(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=60),
                address=fake.address(),
                email=fake.email(),
                social_media_links=json.dumps({'twitter': fake.url(), 'facebook': fake.url()}),
                criminal_record=fake.text()
            )
            offender.crimes_committed.set(random.sample(list(crimes), random.randint(1, 3)))
        self.stdout.write("Offenders created.")

    def create_judicial_cases(self):
        judges = CustomUser.objects.filter(role='judge')
        crimes = Crime.objects.all()
        for crime in crimes:
            JudicialCase.objects.create(
                crime=crime,
                judge=random.choice(judges),
                date_heard=fake.date_between(start_date='today', end_date='+1y'),
                court_location=random.choice(ZIMBABWEAN_CITIES),  # Use Zimbabwean cities
                verdict=random.choice(['guilty', 'not_guilty', 'pending']),
                status=random.choice(['pending', 'in_progress', 'closed']),
                notes=fake.text(),
                hearing_date=fake.date_between(start_date='today', end_date='+1y'),
                next_hearing_date=fake.date_between(start_date='today', end_date='+1y')
            )
        self.stdout.write("JudicialCases created.")

    def create_investigations(self):
        investigators = CustomUser.objects.filter(role='investigator')
        crimes = Crime.objects.all()
        for crime in crimes:
            Investigation.objects.create(
                crime=crime,
                investigator=random.choice(investigators),
                date_assigned=fake.date_between(start_date='-1y', end_date='today'),
                notes=fake.text(),
                status=random.choice(['open', 'closed', 'pending']),
                evidence_files=None,
            )
        self.stdout.write("Investigations created.")