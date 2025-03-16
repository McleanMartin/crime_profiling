from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import CreateView, ListView
from django.contrib.auth import login,logout,authenticate
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from .forms import *
from django.urls import reverse
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth
from .models import *
from .decorators import *


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
    for crime_type in Crime.objects.values_list('crime_type', flat=True).distinct():
        monthly_counts = []
        for month in range(1, 13):
            count = Crime.objects.filter(
                crime_type=crime_type,
                date_reported__month=month
            ).count()
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

def crime_list(request):
    form = CrimeForm()
    query = request.GET.get('q')
    crimes = Crime.objects.all()
    if query:
        crimes = crimes.filter(Q(crime_type__icontains=query) | Q(description__icontains=query))
    return render(request, 'crime_list.html', {'crimes': crimes,'form':form})

def crime_detail(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    form = CrimeForm(instance=crime)
    investigations = Investigation.objects.filter(crime=crime)
    judicial_cases = JudicialCase.objects.filter(crime=crime)
    parties = crime.parties.all()
    
    if request.method == 'POST':
        party_form = PartyForm(request.POST)
        if party_form.is_valid():
            party = party_form.save(commit=False)
            party.crime = crime
            party.save()
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


@police_officer_required
def create_crime(request):
    if request.method == 'POST':
        form = CrimeForm(request.POST, request.FILES)
        if form.is_valid():
            crime = form.save(commit=False)
            crime.date_reported = timezone.now().date()
            crime.reported_by = request.user
            crime.save()
            return redirect(reverse('crime_list'))
    return redirect(reverse('crime_list'))

@police_officer_required
def update_crime(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    if request.method == 'POST':
        form = CrimeForm(request.POST, request.FILES, instance=crime)
        if form.is_valid():
            form.save()
            return redirect(reverse('crime_list')) 
    else:
        form = CrimeForm(instance=crime) 
    return redirect(reverse('crime_list'))

@police_officer_required
def delete_crime(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    rolls = JudicialCase.objects.filter(crime=crime).delete()
    # for roll in rolls:
    #     roll.delete()
    crime.delete()
    return redirect(reverse('crime_list'))

@investigator_required
def upload_evidence(request, investigation_id):
    investigation = get_object_or_404(Investigation, id=investigation_id)
    if request.method == 'POST':
        form = EvidenceUploadForm(request.POST, request.FILES, instance=investigation)
        if form.is_valid():
            form.save()
            return redirect(reverse('investigation_detail', args=[investigation.id]))
    else:
        form = EvidenceUploadForm(instance=investigation)
    return render(request, 'partials/evidence_upload_form.html', {'form': form})


def investigation_detail(request, pk):
    investigation = get_object_or_404(Investigation, pk=pk)
    return render(request, 'investigation_detail.html', {'investigation': investigation})


def court_roll(request):
    cases = JudicialCase.objects.all().order_by('-date_heard')
    return render(request, 'court_roll.html',{'cases': cases})

@judge_required
def update_case_status(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
    case = JudicialCase.objects.get(crime=crime)
    if request.method == 'POST':
        verdict = request.POST.get('verdict')
        case.verdict = verdict
        case.save()
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
        print(case.next_hearing_date)
        case.save() 
        return redirect(reverse('crime_detail', args=[case.pk])) 
    return redirect(reverse('crime_detail', args=[case.pk]))


def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)\
        .order_by('-timestamp')[:10]
        
    return render(request, 'partials/notifications.html', {
        'notifications': notifications
    })

def mark_notification_read(request, pk):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def custom_user_list_view(request):
    users = CustomUser.objects.all().order_by('last_name')
    form = CustomUserCreationForm()
    return render(request, 'users.html', {'users': users,'form':form})

def custom_user_create_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            return redirect(reverse_lazy('users'))
    else:
        form = CustomUserCreationForm() 
    return redirect(reverse_lazy('users'))

def Logout_view(request):
    logout(request)
    return redirect('index')