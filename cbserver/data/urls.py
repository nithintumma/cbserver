from django.conf.urls import patterns, url
from data import views

urlpatterns = patterns('', 
	url(r'uploadanswers', views.uploadAnswers, name = "uploadAnswers"),

	# Item based collaboritive filtering
	url(r'getrecvector/(?P<user_id>\w+)/$', views.getRecVector),
	url(r'hello/$', views.hello),
	# Linear Regression
	url(r'generaterecmodel/(?P<user_id>\w+)/$', views.generateRecModel),
	url(r'updatetopfriends/(?P<user_id>\w+)/$', views.updateTopFriends, name="updateTopFriend"),
	url(r'updaterecvector/(?P<user_id>\w+)/$', views.updateRecVector, name="updaterecvector")
)
