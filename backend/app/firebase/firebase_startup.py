from app.core.config import settings
import firebase

firebase_config = dict(settings.FIREBASE_CONFIG)
firebase_app = firebase.initialize_app(firebase_config)
firebase_storage = firebase_app.storage()
