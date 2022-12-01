from django.conf import settings

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate(settings.FIRESTORE_JSON_PATH)

app = firebase_admin.initialize_app(cred)

db = firestore.client()