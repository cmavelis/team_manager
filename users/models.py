import logging

from django.core.mail import send_mail
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

_LOGGER = logging.getLogger(__name__)


class AppUserManager(BaseUserManager):
    """
    Custom user manager for application. Upon creation, the password
    is not given unless it's a superuser. This allows admins to create
    users easily without having direct access to their account.
    """
    use_in_migrations = True

    def _create_user(self, email, password, is_staff,
                     is_superuser, is_active, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        try:
            now = timezone.now()
            if not email:
                raise ValueError('The given email must be set')
            email = self.normalize_email(email)
            user = self.model(email=email, is_staff=is_staff,
                              is_active=is_active, is_superuser=is_superuser, #date_joined=now,
                              **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
        except IntegrityError:
            _LOGGER.error('Cannot create new user with email {}. '
                          'A user with that email already exists.'.format(email))

    def create_user(self, email, password=None, **extra_fields):
        """
        Public method for creating a user.
        """
        return self._create_user(email, password, False, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Public method for creating a superuser.
        """
        return self._create_user(email, password, True, True, True,
                                 **extra_fields)


class AppUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email for authentication rather than
    a username.
    """
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    full_name = models.CharField(_('full name'), max_length=100, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this '
                    'admin site.'))
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_('Designates whether this user should be treated as '
                    'active. Deselect this instead of deleting accounts.'))
    # date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = AppUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])


