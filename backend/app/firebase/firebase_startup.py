from app.core.config import settings
import firebase


firebase_config = {
  "apiKey": settings.FIREBASE_API_KEY,
  "authDomain": "discord-83cd2.firebaseapp.com",
  "databaseURL": "https://discord-83cd2-default-rtdb.firebaseio.com",
  "projectId": "discord-83cd2",
  "storageBucket": "discord-83cd2.appspot.com",
  "messagingSenderId": "951586420649",
  "appId": "1:951586420649:web:c95ce57fdd3766492336b8",
  "measurementId": "G-GLYJ5PKYF7"
}
firebase_app = firebase.initialize_app(firebase_config)
firebase_storage = firebase_app.storage()