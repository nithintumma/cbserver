from django.conf.urls import patterns, url
from data import views

urlpatterns = patterns('', 
	url(r'uploadanswers', views.uploadAnswers),
	url(r'getrecvector/(?P<user_id>\w+)/$', views.getRecVector),
)
