from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import EventForm
from .models import Event
import random
import json
import time

# Create your views here.

def index(request):
    return render(request, 'index.html')

def news(request):
    # Fetch all verified and active events, ordered by creation date (newest first)
    events = Event.objects.filter(is_verified=True, is_active=True).order_by('-created_at')
    return render(request, 'news.html', {'events': events})

def post_event(request):
    if request.method == 'POST':
        if 'send_otp' in request.POST:
            return send_otp_email(request)
        elif 'verify_otp' in request.POST:
            return verify_otp_and_post_event(request)
    
    form = EventForm()
    return render(request, 'post_event.html', {'form': form})

@csrf_exempt
@require_http_methods(["POST"])
def send_otp_email(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Generate 6-digit OTP
        otp = random.randint(100000, 999999)
        
        # Store OTP in session with timestamp
        request.session['otp'] = str(otp)
        request.session['otp_email'] = email
        request.session['otp_timestamp'] = time.time()
        
        # Email content
        subject = 'ReadersHub Event Posting - Organizer Identity Verification'
        message = f'''
        Hello,
        
        Thank you for posting an event on ReadersHub!
        
        To ensure our platform maintains authentic and reliable events, we need to verify your identity as an event organizer.
        
        Your verification code is: {otp}
        
        This code will expire in 5 minutes for security purposes.
        
        If you didn't request this verification, please ignore this email.
        
        Best regards,
        ReadersHub Team
        '''
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return JsonResponse({'success': True, 'message': 'OTP sent successfully to your email'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Failed to send OTP: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
def verify_otp_and_post_event(request):
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            entered_otp = data.get('otp')
            event_data = data.get('event_data')
            poster_file = None
        else:
            entered_otp = request.POST.get('otp')
            event_data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'date': request.POST.get('date'),
                'time': request.POST.get('time'),
                'venue': request.POST.get('venue'),
                'college_name': request.POST.get('college_name')
            }
            poster_file = request.FILES.get('poster')
        
        # Check if OTP exists in session
        session_otp = request.session.get('otp')
        session_email = request.session.get('otp_email')
        otp_timestamp = request.session.get('otp_timestamp')
        
        if not session_otp or not otp_timestamp:
            return JsonResponse({'success': False, 'message': 'OTP not found or expired'})
        
        # Check if OTP is expired (5 minutes)
        if time.time() - otp_timestamp > 300:
            # Clear expired OTP
            request.session.pop('otp', None)
            request.session.pop('otp_email', None)
            request.session.pop('otp_timestamp', None)
            return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'})
        
        # Verify OTP
        if entered_otp != session_otp:
            return JsonResponse({'success': False, 'message': 'Invalid OTP. Please try again.'})
        
        # OTP is valid, clear from session
        request.session.pop('otp', None)
        request.session.pop('otp_email', None)
        request.session.pop('otp_timestamp', None)
        
        # Save event to database
        try:
            event = Event.objects.create(
                title=event_data.get('title'),
                description=event_data.get('description'),
                date=event_data.get('date'),
                time=event_data.get('time'),
                venue=event_data.get('venue'),
                college_name=event_data.get('college_name'),
                organizer_email=session_email,
                is_verified=True  # Mark as verified since OTP was successful
            )
            
            # Handle poster file upload if present
            if 'poster_file' in locals() and poster_file:
                event.poster = poster_file
            
            event.save()
        except Exception as db_error:
            return JsonResponse({'success': False, 'message': f'Failed to save event: {str(db_error)}'})
        
        # Send confirmation email
        try:
            send_mail(
                subject='Event Posted Successfully - ReadersHub',
                message=f'''
                Hello,
                
                Your event "{event_data.get('title', 'Untitled Event')}" has been successfully posted on ReadersHub!
                
                Event Details:
                - Title: {event_data.get('title', 'N/A')}
                - Date: {event_data.get('date', 'N/A')}
                - Time: {event_data.get('time', 'N/A')}
                - Venue: {event_data.get('venue', 'N/A')}
                - College/Institution: {event_data.get('college_name', 'N/A')}
                - Poster: {'Uploaded' if poster_file else 'N/A'}
                
                Thank you for using ReadersHub!
                
                Best regards,
                HubMates Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[session_email],
                fail_silently=True,
            )
        except:
            pass  # Don't fail if confirmation email fails
        
        return JsonResponse({'success': True, 'message': 'Event posted successfully!'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Verification failed: {str(e)}'})