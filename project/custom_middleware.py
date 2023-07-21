from django.utils.deprecation import MiddlewareMixin

class CsrfHeaderMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if "CSRF_COOKIE" in request.META:
            # csrfviewmiddleware sets response cookie as request.META['CSRF_COOKIE']
            #response["Set-Cookie"]
            
            a = request.headers['Cookie'].split(";")[0] + "; expires=Fri, 19 Jul 2024 03:43:33 GMT; Max-Age=31449600; Path=/; SameSite=None; Secure "
            b = request.headers['Cookie'].split(";")[1] + "; expires=Fri, 19 Jul 2024 03:43:33 GMT; Max-Age=31449600; Path=/; SameSite=None; Secure"
            response["Set-Cookie"] = a + b
            response["X-CSRFTOKEN"] = request.META['CSRF_COOKIE']
        return response
    
        # I am now using JWT Authentication with django-rest-framework-simplejwt. Everything works fine and its less code. awesome! 
        # I am now using JWT Authentication with django-rest-framework-simplejwt. Everything works fine and its less code. awesome! 
        # I am now using JWT Authentication with django-rest-framework-simplejwt. Everything works fine and its less code. awesome! 
        # I am now using JWT Authentication with django-rest-framework-simplejwt. Everything works fine and its less code. awesome! 
        # I am now using JWT Authentication with django-rest-framework-simplejwt. Everything works fine and its less code. awesome! 
        # I am now using JWT Authentication with django-rest-framework-simplejwt. Everything works fine and its less code. awesome! 
        # I am now using JWT Authentication with django-rest-framework-simplejwt. Everything works fine and its less code. awesome! 
