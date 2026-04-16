from models.database import db, User
from sqlalchemy.exc import IntegrityError

class AuthService:
    
    @staticmethod
    def register(username, email, password):
        """Returns: (success: bool, message: str, user: User or None)"""
        if not username or not email or not password:
            return False, "Sva polja su obavezna", None
        
        if len(password) < 6:
            return False, "Lozinka mora imati najmanje 6 karaktera", None
        
        if len(username) < 3:
            return False, "Korisničko ime mora imati najmanje 3 karaktera", None
        
        try:
            user = User(
                username=username.lower(),
                email=email.lower(),
                role='user'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return True, "Nalog uspješno kreiran! Molimo prijavite se.", user
        
        except IntegrityError:
            db.session.rollback()
            existing_user = User.query.filter(
                (User.username == username.lower()) | (User.email == email.lower())
            ).first()
            
            if existing_user and existing_user.username == username.lower():
                return False, "Korisničko ime je već zauzeto", None
            else:
                return False, "Email je već registrovan", None
        
        except Exception as e:
            db.session.rollback()
            return False, f"Greška pri registraciji: {str(e)}", None
    
    @staticmethod
    def login(email, password):
        """Returns: (success: bool, message: str, user: User or None)"""
        if not email or not password:
            return False, "Email i lozinka su obavezni", None
        
        try:
            user = User.query.filter_by(email=email.lower()).first()
            
            if not user:
                return False, "Pogrešan email ili lozinka", None
            
            if not user.is_active:
                return False, "Nalog je deaktiviran", None
            
            if not user.check_password(password):
                return False, "Pogrešan email ili lozinka", None
            
            return True, "Uspješna prijava", user
        
        except Exception as e:
            return False, f"Greška pri prijavi: {str(e)}", None
