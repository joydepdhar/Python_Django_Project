from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, email = None, password = None, **kwargs):
        # return super().authenticate(request, username, password, **kwargs)
        User=get_user_model()
        try:
            user=User.objects.get(email=email)
            if user.check_password(password):
                return 
        except User.DoesNotExsit as e:
            print("not a User",e)
            return None