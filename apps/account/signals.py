from django.dispatch import Signal

user_created = Signal(providing_args=["is_lecturer", "created_user"])
