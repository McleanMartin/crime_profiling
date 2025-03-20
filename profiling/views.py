from .models import *
from .decorators import *
from .forms import *
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import CreateView, ListView
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from collections import Counter
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from django.urls import reverse
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth
from profiling.utils.notifications import create_notification


def monthly_report(request):
    selected_month = int(request.GET.get('month', timezone.now().month))
    selected_year = int(request.GET.get('year', timezone.now().year))

    crimes = Crime.objects.filter(
        date_reported__month=selected_month,
        date_reported__year=selected_year
    )

    total_crimes = crimes.count()

    solved_cases = JudicialCase.objects.filter(
        crime__in=crimes,
        verdict='closed'
    ).count()


    pending_cases = JudicialCase.objects.filter(
        crime__in=crimes,
    ).filter(
        Q(verdict='pending') | Q(verdict='in progress')
    ).count()

    parties = Party.objects.filter(crime__in=crimes)
    age_distribution = Counter()
    for party in parties:
        age = (timezone.now().date() - party.date_of_birth).days // 365
        age_distribution[age] += 1

    most_committed_crimes = Counter(crime.crime_type for crime in crimes).most_common(5)
    high_crime_locations = Counter(crime.location for crime in crimes).most_common(5)

    if request.GET.get('format') == 'pdf':
        return generate_pdf(
            selected_month, selected_year, total_crimes, solved_cases, pending_cases,
            age_distribution, most_committed_crimes, high_crime_locations
        )

    context = {
        'selected_month': selected_month,
        'selected_year': selected_year,
        'total_crimes': total_crimes,
        'solved_cases': solved_cases,
        'pending_cases': pending_cases,
        'age_distribution': dict(age_distribution),
        'most_committed_crimes': most_committed_crimes,
        'high_crime_locations': high_crime_locations,
    }

    return render(request, 'reports.html', context)

def about_view(request):
    return render(request,'about.html')

def contact_view(request):
    return render(request,'contact.html')

def generate_pdf(month, year, total_crimes, solved_cases, pending_cases, age_distribution, most_committed_crimes, high_crime_locations):
    # Create a BytesIO buffer to store the PDF
    buffer = BytesIO()

    # Create the PDF object
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph(f"Monthly Crime Report for {month}/{year}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # General Statistics
    elements.append(Paragraph("General Statistics", styles['Heading2']))
    data = [
        ["Total Crimes", str(total_crimes)],
        ["Solved Cases", str(solved_cases)],
        ["Pending Cases", str(pending_cases)],
    ]
    table = Table(data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Age Distribution
    elements.append(Paragraph("Age Distribution of Parties Involved", styles['Heading2']))
    data = [["Age", "Count"]]
    for age, count in age_distribution.items():
        data.append([str(age), str(count)])
    table = Table(data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Most Committed Crimes
    elements.append(Paragraph("Most Committed Crimes", styles['Heading2']))
    data = [["Crime Type", "Count"]]
    for crime, count in most_committed_crimes:
        data.append([crime, str(count)])
    table = Table(data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # High Crime Locations
    elements.append(Paragraph("Locations with High Crime Rates", styles['Heading2']))
    data = [["Location", "Count"]]
    for location, count in high_crime_locations:
        data.append([location, str(count)])
    table = Table(data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Build the PDF
    pdf.build(elements)

    # Get the PDF content and return it as a response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="monthly_report_{month}_{year}.pdf"'
    return response

def public_view(request):
    today = timezone.now().date()
    upcoming_cases = JudicialCase.objects.filter(next_hearing_date__gte=today).order_by('next_hearing_date')
    return render(request, 'public.html', {'upcoming_cases': upcoming_cases})

@login_required
@cache_page(60 * 15)
def dashboard(request):
    crime_stats = {
        'total_crimes': Crime.objects.count(),
        'active_crimes': Crime.objects.exclude(status='closed').count(),
        'closed_crimes': Crime.objects.filter(status='closed').count(),
        'crimes_by_type': Crime.objects.values('crime_type')
                             .annotate(count=Count('id'))
                             .order_by('-count')[:5],
        'status_distribution': Crime.objects.values('status')
                                 .annotate(count=Count('id')),
    }

    crimes_by_type_with_monthly_counts = []
    crime_types = Crime.objects.values_list('crime_type', flat=True).distinct()

    for crime_type in crime_types:
        monthly_counts = []
        for month in range(1, 13):
            count = Crime.objects.filter(
                crime_type=crime_type,
                date_reported__month=month
            ).aggregate(count=Count('id'))['count']
            monthly_counts.append(count)
        
        crimes_by_type_with_monthly_counts.append({
            'crime_type': crime_type,
            'monthly_counts': monthly_counts,
        })

    crime_stats['crimes_by_type_with_monthly_counts'] = crimes_by_type_with_monthly_counts

    investigation_stats = {
        'active_investigations': Investigation.objects.filter(status='open').count(),
        'recent_investigations': Investigation.objects.select_related('crime')
                                       .order_by('-date_assigned')[:5],
    }

    judicial_stats = {
        'upcoming_hearings': JudicialCase.objects.filter(
            Q(next_hearing_date__gte=timezone.now()) |
            Q(date_heard__gte=timezone.now())
        ).order_by('date_heard')[:5],
        'case_status': JudicialCase.objects.values('status')
                             .annotate(count=Count('id')),
    }


    party_stats = {
        'total_parties': Party.objects.count(),
        'party_roles': Party.objects.values('role')
                          .annotate(count=Count('id')),
    }

    context = {
        'crime_stats': crime_stats,
        'investigation_stats': investigation_stats,
        'judicial_stats': judicial_stats,
        'party_stats': party_stats,
    }
    return render(request, 'dashboard.html', context)

def index_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('crime_list')
    return render(request, 'login.html')

@login_required
def crime_list(request):
    form = CrimeForm()
    query = request.GET.get('q')
    crimes = Crime.objects.all().order_by('-case_number')
    if query:
        crimes = crimes.filter(Q(crime_type__icontains=query) | Q(description__icontains=query)).order_by('-pk')
    return render(request, 'crime_list.html', {'crimes': crimes,'form':form})

@login_required
def crime_detail(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    form = CrimeForm(instance=crime)
    investigations = Investigation.objects.filter(crime=crime)
    judicial_cases = JudicialCase.objects.filter(crime=crime)
    parties = Party.objects.filter(crime=crime)
    
    if request.method == 'POST':
        party_form = PartyForm(request.POST)
        if party_form.is_valid():
            party = party_form.save(commit=False)
            party.crime = crime
            party.save() 
            messages.success(request,f'{party.name} was add as {party.role} for case number {crime.case_number}')
            return redirect('crime_detail', pk=crime.pk)
    else:
        party_form = PartyForm()
    return render(request, 'crime_detail.html', {
        'crime': crime,
        'investigations': investigations,
        'judicial_cases': judicial_cases,
        'parties': parties,
        'party_form': party_form,
        'form':form,
    })

# @police_officer_required
def edit_party_view(request, pk):
    party = get_object_or_404(Party, pk=pk)
    if request.method == 'POST':
        form = PartyForm(request.POST, instance=party)
        if form.is_valid():
            form.save()
            messages.success(request, f'{party.name} details successfully updated.')
            return redirect('crime_detail', pk=party.crime.pk)
        else:
            messages.error(request, 'There was an error updating the party details. Please check the form.')
    else:
        form = PartyForm(instance=party)
    return redirect('crime_detail', pk=party.crime.pk)


# @police_officer_required
def delete_party_view(request, pk):
    party = get_object_or_404(Party, pk=pk)
    crime_pk = party.crime.pk
    name = party.name
    party.delete()
    messages.success(request, f'{name} was successfully deleted.')
    return redirect('crime_detail', pk=crime_pk)

# @police_officer_required
def create_crime(request):
    if request.method == 'POST':
        form = CrimeForm(request.POST, request.FILES)
        if form.is_valid():
            crime = form.save(commit=False)
            crime.date_reported = timezone.now().date()
            crime.reported_by = request.user
            crime.save()
            messages.success(request, f'Case number {crime.case_number} created successfully.')
            return redirect(reverse('crime_list'))
        else:
            messages.error(request, 'There was an error creating the crime. Please check the form.')
    return redirect(reverse('crime_list'))

# @police_officer_required
def update_crime(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    if request.method == 'POST':
        form = CrimeForm(request.POST, request.FILES, instance=crime)
        if form.is_valid():
            form.save()
            messages.success(request, f'Case {crime.case_number} updated successfully.')
            return redirect(reverse('crime_list'))
        else:
            messages.error(request, 'There was an error updating the crime. Please check the form.')
    else:
        form = CrimeForm(instance=crime)
    return redirect(reverse('crime_list'))

# @police_officer_required
def delete_crime(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    rolls = JudicialCase.objects.filter(crime=crime).delete()
    crime.delete()
    messages.success(request, f'Case {crime.case_number} deleted.')
    return redirect(reverse('crime_list'))


# @investigator_required
def upload_evidence(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    if request.method == 'POST':
        form = EvidenceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.crime = crime
            obj.investigator = request.user
            obj.save()
            messages.success(request, f'Evidence for case #{crime.case_number} updated.')
            return redirect(reverse('crime_detail', args=[pk]))
        else:
            messages.error(request, 'There was an error uploading the evidence. Please check the form.')
    else:
        form = EvidenceUploadForm()
    return redirect(reverse('crime_detail', args=[pk]))

@login_required
def investigation_detail(request, pk):
    investigation = get_object_or_404(Investigation, pk=pk)
    return render(request, 'investigation_detail.html', {'investigation': investigation})

@login_required
def court_roll(request):
    cases = JudicialCase.objects.all().order_by('-date_heard')
    return render(request, 'court_roll.html',{'cases': cases})

# @judge_required
def update_case_status(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    case = JudicialCase.objects.get(crime=crime)
    if request.method == 'POST':
        verdict = request.POST.get('verdict')
        case.verdict = verdict
        case.save()
        messages.success(request, f'Case status updated to {verdict}.')
        return redirect(reverse('crime_detail', args=[case.pk]))
    else:
        form = JudicialCaseStatusForm(instance=case)
    return redirect(reverse('crime_detail'))

@judge_required
def schedule_next_hearing(request, pk):
    case = get_object_or_404(JudicialCase, pk=pk)
    if request.method == 'POST':
        next_hearing_date = request.POST.get('next_hearing_date')
        case.next_hearing_date = next_hearing_date
        case.save()
        messages.success(request, f'Next hearing scheduled for {next_hearing_date}.')
        return redirect(reverse('crime_detail', args=[case.pk]))
    return redirect(reverse('crime_detail', args=[case.pk]))

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)\
        .order_by('-timestamp')[:10]
        
    return render(request, 'partials/notifications.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, pk):
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found.'}, status=404)
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred.'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required
def custom_user_list_view(request):
    users = CustomUser.objects.all().order_by('last_name')
    form = CustomUserCreationForm()
    return render(request, 'users.html', {'users': users,'form':form})

@login_required
def custom_user_create_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            return redirect(reverse_lazy('users'))
    else:
        form = CustomUserCreationForm() 
    return redirect(reverse_lazy('users'))


@login_required
def Logout_view(request):
    logout(request)
    return redirect('index')