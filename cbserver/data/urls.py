from django.conf.urls import patterns, url
from data import views

urlpatterns = patterns('', 
	url(r'uploadanswers', views.uploadAnswers, name = "uploadAnswers"),
	url(r'getrecvector/(?P<user_id>\w+)/$', views.getRecVector),
	url(r'updatetopfriends/(?P<user_id>\w+)/$', views.updateTopFriends, name="updateTopFriend"),
)
