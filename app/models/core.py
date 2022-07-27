import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    This model represents a user that can log into ERP. A user can also be an
    employee, but an employee might not be a user.
    """

    email = models.EmailField(_("email address"), unique=True)

    organization = models.ForeignKey(
        "Organization", on_delete=models.CASCADE, null=True
    )

    default_role = models.ForeignKey("Role", on_delete=models.SET_NULL, null=True)
    is_onboarded = models.BooleanField(default=False)

    # this field should not be stored in DB. This field will be updated by
    # view to True if the user is admin for the module being accessed.
    is_module_admin = False

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class Invitation(models.Model):
    """
    This model is used to track the invitation of the user.
    """

    user = models.OneToOneField("User", on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_key(self):
        self.slug = f"{self.user.id}{random.randint(0, 2**31-1)}"


class Organization(models.Model):
    """
    This model is used to add organization scope. A data belonging to one
    organization should only be visible to that organization.
    """

    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def owner(self):
        return self.user_set.filter(
            default_role__permission=Role.Permission.OWNER
        ).first()


class OrganizationModule(models.Model):
    """
    Use this model to manage module access to an organization. There should be
    a row for every module-organization pair in this model. We control access
    using is_enabled boolean.
    """

    module = models.ForeignKey("Module", on_delete=models.PROTECT)
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserModuleRole(models.Model):
    """
    Use this model to manage role of user for a module. A user can have
    different roles in different modules.
    """

    module = models.ForeignKey("Module", on_delete=models.PROTECT)
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="module_roles"
    )
    role = models.ForeignKey("Role", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Module(models.Model):
    """
    Currently we support following modules:
    - Payroll
    - Employee
    - Inventory
    """

    slug = models.SlugField()
    name = models.CharField(max_length=64)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug


class Role(models.Model):
    """
    Currently we support following roles:
    - Owner: Super user for an organization. This is organization role. It
      cannot be assigned to module. There should always be atleast one owner.
    - Admin: Can manage data of other users.
    - Member: Can only manage own data.
    """

    class Permission(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    name = models.CharField(max_length=64, unique=True)
    permission = models.CharField(
        max_length=10, choices=Permission.choices, default=Permission.MEMBER
    )
    is_default = models.BooleanField(default=False)
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def less_than(self, permission_or_role):
        other_permission = (
            permission_or_role.permission
            if isinstance(permission_or_role, Role)
            else permission_or_role
        )

        if self.permission == self.Permission.OWNER and other_permission in (
            self.Permission.MEMBER,
            self.Permission.ADMIN,
        ):
            return True

        if (
            self.permission == self.Permission.ADMIN
            and other_permission == self.Permission.MEMBER
        ):
            return True

        return False

    def equal_to(self, permission_or_role):
        other_permission = (
            permission_or_role.permission
            if isinstance(permission_or_role, Role)
            else permission_or_role
        )
        return self.permission == other_permission

    def __str__(self):
        return self.name


class Currency(models.Model):
    """
    Currently we support following currencies:
    - USD
    - PKR
    """

    code = models.CharField(max_length=3)
    symbol = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
