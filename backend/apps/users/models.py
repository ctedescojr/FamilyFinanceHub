from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model for FamilyFinanceHub.
    """

    class FamilyRole(models.TextChoices):
        FATHER = "FATHER", _("Father")
        MOTHER = "MOTHER", _("Mother")
        SON = "SON", _("Son")
        DAUGHTER = "DAUGHTER", _("Daughter")
        GRANDFATHER = "GRANDFATHER", _("Grandfather")
        GRANDMOTHER = "GRANDMOTHER", _("Grandmother")
        UNCLE = "UNCLE", _("Uncle")
        AUNT = "AUNT", _("Aunt")
        FRIEND = "FRIEND", _("Friend")
        PET = "PET", _("Pet")

    email = models.EmailField(_("email address"), unique=True)
    cellphone = models.CharField(_("cellphone"), max_length=20, blank=True)
    job = models.CharField(_("job"), max_length=100, blank=True)
    family_role = models.CharField(
        _("family role"),
        max_length=20,
        choices=FamilyRole.choices,
        default=FamilyRole.FRIEND,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.email
