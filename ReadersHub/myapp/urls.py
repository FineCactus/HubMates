from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news/', views.news, name='news'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('post-event/', views.post_event, name='post_event'),
    path('send-otp/', views.send_otp_email, name='send_otp'),
    path('verify-otp/', views.verify_otp_and_post_event, name='verify_otp'),
]