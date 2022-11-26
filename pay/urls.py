from django.urls    import path 

from pay.views import PayView

urlpatterns = [
    path('', PayView.as_view()),
]