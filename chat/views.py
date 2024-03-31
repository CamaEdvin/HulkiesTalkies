from django.shortcuts import render
from django.contrib.auth.models import User
from django.views import View
from django.shortcuts import redirect


class NewRoomView(View):
    def get(self, request):
        users = User.objects.all()
        context = {'users': users}
        return render(request, 'chat.html', context)

    def post(self, request):
        selected_user_id = request.POST.get('recipient')
        return redirect('chat')
    

def dashboard(request):
    users = User.objects.all()
    context = {'users': users}
    print("context: ", context)
    return render(request, 'dashboard.html', context)