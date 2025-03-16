from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from datetime import datetime, timedelta
from faker import Faker
from profiling.models import *
import json
import random

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
        self.stdout.write(self.style.SUCCESS("Generating dummy data..."))

        # Create Groups and Permissions
        self.create_groups_and_permissions()

        # Create CustomUsers
        self.create_custom_users()

        # Create Crimes
        self.create_crimes()

        # Create Offenders
        self.create_dummy_parties()

        # Create JudicialCases
        self.create_judicial_cases()

        # Create Investigations
        self.create_investigations()

        self.stdout.write(self.style.SUCCESS("Dummy data generation complete!"))

    def create_groups_and_permissions(self):
        group_names = ['police', 'investigator', 'judge']
        for name in group_names:
            Group.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Groups and permissions created."))

    def create_custom_users(self):
        roles = ['police', 'investigator', 'judge']
        for _ in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
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
                department=department,
                first_name=first_name,
                last_name=last_name
            )
        self.stdout.write(self.style.SUCCESS("CustomUsers created."))

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
        self.stdout.write(self.style.SUCCESS("Dummy crime records with realistic descriptions created successfully."))

    def create_dummy_parties(self):
        # Fetch all crimes from the database
        crimes = list(Crime.objects.all())
        if not crimes:
            self.stdout.write(self.style.ERROR('No crimes found in the database. Please add crimes first.'))
            return

        # Number of dummy parties to create
        num_parties = 20

        for _ in range(num_parties):
            try:
                # Randomly select a crime
                crime = random.choice(crimes)

                # Randomly select a role
                role = random.choice(['victim', 'witness', 'suspect'])

                # Generate fake data
                name = fake.name()
                contact_info = fake.phone_number()
                date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)
                address = fake.address()
                relationship_to_case = fake.sentence()
                additional_info = json.dumps({
                    'occupation': fake.job(),
                    'notes': fake.text()
                })

                # Create the Party instance
                party = Party.objects.create(
                    crime=crime,
                    role=role,
                    name=name,
                    contact_info=contact_info,
                    date_of_birth=date_of_birth,
                    address=address,
                    relationship_to_case=relationship_to_case,
                    additional_info=additional_info
                )
                self.stdout.write(self.style.SUCCESS(f'Created party: {party}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating party: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_parties} dummy parties.'))

    def create_judicial_cases(self):
        judges = list(CustomUser.objects.filter(role='judge'))  # Fetch all judges
        crimes = list(Crime.objects.all())  # Fetch all crimes

        if not judges:
            self.stdout.write(self.style.ERROR('No judges found in the database. Please add judges first.'))
            return

        if not crimes:
            self.stdout.write(self.style.ERROR('No crimes found in the database. Please add crimes first.'))
            return

        # Shuffle the list of crimes to randomize assignment
        random.shuffle(crimes)

        for crime in crimes:
            if not judges:
                self.stdout.write(self.style.WARNING('No more judges available to assign to cases.'))
                break

            # Assign a judge to the case
            judge = judges.pop()  # Remove the judge from the list to ensure no reuse for this case

            JudicialCase.objects.create(
                crime=crime,
                judge=judge,
                date_heard=fake.date_between(start_date='today', end_date='+1y'),
                court_location=random.choice(ZIMBABWEAN_CITIES),  # Use Zimbabwean cities
                verdict=random.choice(['guilty', 'not_guilty', 'pending']),
                status=random.choice(['pending', 'in_progress', 'closed']),
                notes=fake.text(),
                hearing_date=fake.date_between(start_date='today', end_date='+1y'),
                next_hearing_date=fake.date_between(start_date='today', end_date='+1y')
            )
            self.stdout.write(self.style.SUCCESS(f'Created JudicialCase for crime {crime.id} with judge {judge.username}'))

        self.stdout.write(self.style.SUCCESS("JudicialCases created."))

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
        self.stdout.write(self.style.SUCCESS("Investigations created."))