import os
import firebase_admin
from firebase_admin import credentials, initialize_app, storage

cred = credentials.Certificate(
    r"C:\Users\KevSa\Documents\GitHub\McDonalds-McNuggets\src\studio-3378748931-552bc-firebase-adminsdk-fbsvc-b7bf8b035b.json"
)

firebase_admin.initialize_app(cred, {
    'storageBucket': 'studio-3378748931-552bc.firebasestorage.app'
})

bucket = storage.bucket()
