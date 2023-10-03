import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

# from user.serializers import UserSerializer
# from user.models import User


# class RegisterView(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")

#         user = User.objects.filter(email=email).first()

#         if user is None:
#             raise AuthenticationFailed("User not found!")
        
#         if not  user.check_password(password):
#             raise AuthenticationFailed("An incorrect password was entered!")

#         payload = {
#             "id": user.id,
#             "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
#             "iat": datetime.datetime.utcnow()
#         }

#         refresh_token = RefreshToken.for_user(user)

#         response = Response()

#         response.set_cookie(key="jwt", value=refresh_token.access_token, httponly=True)
#         response.data = {
#             "jwt": str(refresh_token.access_token)
#         }
        
#         # return Response("You've been successfully logged in")
#         return response


# # class UserView(APIView):
# #     def get(self, request):
# #         token = request.COOKIES.get("jwt")

# #         if not token:
# #             raise AuthenticationFailed("User unauthenticated!")
# #         return Response({"jwt": token})


