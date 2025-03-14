from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import login,logout,authenticate
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from .forms import *
from django.urls import reverse
from django.db.models import Q, Count
from .models import *


@cache_page(60 * 15)
def dashboard(request):
    # Crime Statistics
    crime_stats = {
        'total_crimes': Crime.objects.count(),
        'crimes_by_type': Crime.objects.values('crime_type')
                             .annotate(count=Count('id'))
                             .order_by('-count')[:5],
        'status_distribution': Crime.objects.values('status')
                                 .annotate(count=Count('id')),
    }

    # Investigation Metrics
    investigation_stats = {
        'active_investigations': Investigation.objects.filter(status='active').count(),
        'recent_investigations': Investigation.objects.select_related('crime')
                                       .order_by('-date_assigned')[:5],
    }

    # Judicial Metrics
    judicial_stats = {
        'upcoming_hearings': JudicialCase.objects.filter(
            Q(next_hearing_date__gte=timezone.now()) |
            Q(date_heard__gte=timezone.now())
        ).order_by('date_heard')[:5],
        'case_status': JudicialCase.objects.values('status')
                             .annotate(count=Count('id')),
    }


    # Party Statistics
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
    query = request.GET.get('q')
    crimes = Crime.objects.all()
    if query:
        crimes = crimes.filter(Q(crime_type__icontains=query) | Q(description__icontains=query))
    return render(request, 'crime_list.html', {'crimes': crimes})

def crime_detail(request, pk):
    crime = get_object_or_404(Crime, pk=pk)
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
        'party_form': party_form
    })

class CrimeCreateView(CreateView):
    model = Crime
    form_class = CrimeForm
    template_name = 'crime_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_reported'].initial = timezone.now().date()
        return form

class CrimeUpdateView(UpdateView):
    model = Crime
    form_class = CrimeForm
    template_name = 'crime_form.html'

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
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()
    cases = JudicialCase.objects.filter(date_heard=selected_date)
    return render(request, 'court_roll.html', {'cases': cases, 'selected_date': selected_date})

def update_case_status(request, pk):
    case = get_object_or_404(JudicialCase, pk=pk)
    if request.method == 'POST':
        form = JudicialCaseStatusForm(request.POST, instance=case)
        if form.is_valid():
            form.save()
            # Send notification (see step 3)
            return redirect(reverse('judicial_case_detail', args=[case.id]))
    else:
        form = JudicialCaseStatusForm(instance=case)
    return render(request, 'partials/update_case_status_form.html', {'form': form})

def schedule_next_hearing(request, pk):
    case = get_object_or_404(JudicialCase, pk=pk)
    if request.method == 'POST':
        form = NextHearingForm(request.POST, instance=case)
        if form.is_valid():
            form.save()
            # Send notification (see step 3)
            return redirect(reverse('judicial_case_detail', args=[case.id]))
    else:
        form = NextHearingForm(instance=case)
    return render(request, 'partials/schedule_next_hearing_form.html', {'form': form})


def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)\
        .order_by('-timestamp')[:10]
        
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    })

def mark_notification_read(request, pk):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)




def Logout_view(request):
    logout(request)
    return redirect('index')