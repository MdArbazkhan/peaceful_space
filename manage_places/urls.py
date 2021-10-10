from django.urls import path
from . import views

urlpatterns = [
    path('', views.landingPage, name='landing-page'),
    path('list/<str:city_name>', views.listPage, name='list-places-page'),
    path('sub/<str:place_id>', views.subConfirmPage, name='submission-page'),
    path('add', views.addNewPlaces, name='add-new-places'),
    path('up', views.placesApproval, name='approve-new-places'),
    path('upvote', views.upvoteView, name='upvote-place'),
    path('reject/<str:place_id>', views.rejectView, name='reject-place'),
    path('accept/<str:place_id>', views.acceptView, name='accept-place'),
]