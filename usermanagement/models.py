import uuid
import hashlib
from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    salt = models.CharField(max_length=64)
    hash = models.CharField(max_length=128)

    def set_password(self, password):
        self.salt = uuid.uuid4().hex
        self.hash = self._generate_hash(password)

    def check_password(self, password):
        return self.hash == self._generate_hash(password)

    def _generate_hash(self, password):
        return hashlib.sha512((self.salt + password).encode('utf-8')).hexdigest()

    def __str__(self):
        return self.email
