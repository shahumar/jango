import request
import sys
from accounts.models import ListUser

class PersonaAuthenticationBackend(object):
    
    def authenticate(self, assertion):
        # send assertion to mozzila verifier service.

        data = {'assertion': assertion, 'audience': 'localhost'}
        print('sending to mozilla', data, file=sys.stderr)
        resp = request.post('https://verifier.login.persona.org/verify', data=data)
        print('got', resp.content, file=sys.stderr)

        # Did the verifier respond ?
        if resp.ok:
            verification_data = resp.json()
            #check if assertion is valid
            if verification_data['status'] == 'okay':
                email = verification_data['email']
                try:
                    return self.get_user(email)
                except ListUser.DoesNotExist:
                    return ListUser.objects.create(email=email)

    def get_user(self, email):
        return ListUser.objects.get(email=email)

