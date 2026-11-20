from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate

from accounts.models import Role

User = get_user_model()


class RegistrationTest(TestCase):
    def test_unapproved_user_cannot_login(self):
        User.objects.create_user(
            username="pending",
            password="testpass123",
            is_approved=False,
        )
        result = authenticate(username="pending", password="testpass123")
        self.assertIsNone(result)

    def test_approved_user_can_login(self):
        user = User.objects.create_user(
            username="approved",
            password="testpass123",
            is_approved=True,
        )
        result = authenticate(username="approved", password="testpass123")
        self.assertIsNotNone(result)
        self.assertEqual(result.pk, user.pk)

    def test_wrong_password_rejected(self):
        User.objects.create_user(
            username="gooduser",
            password="testpass123",
            is_approved=True,
        )
        result = authenticate(username="gooduser", password="wrongpass")
        self.assertIsNone(result)

    def test_role_assignment(self):
        role = Role.objects.create(
            code="TEST_ROLE",
            name="Test Role",
            permissions=["test.perm"],
        )
        user = User.objects.create_user(
            username="roleuser",
            password="testpass123",
            is_approved=True,
        )
        user.roles.add(role)
        self.assertTrue(user.has_role("TEST_ROLE"))
        self.assertIn("TEST_ROLE", user.role_codes)

    def test_has_permission_code(self):
        role = Role.objects.create(
            code="PERM_ROLE",
            name="Permission Role",
            permissions=["inventory.view_stock", "inventory.add_receipt"],
        )
        user = User.objects.create_user(
            username="permuser",
            password="testpass123",
            is_approved=True,
        )
        user.roles.add(role)
        self.assertTrue(user.has_permission_code("inventory.view_stock"))
        self.assertFalse(user.has_permission_code("admin.manage_users"))

    def test_admin_has_all_permissions(self):
        admin_role = Role.objects.create(
            code="ADMIN",
            name="Admin",
            permissions=["*"],
        )
        user = User.objects.create_user(
            username="adminuser",
            password="testpass123",
            is_approved=True,
        )
        user.roles.add(admin_role)
        self.assertTrue(user.has_permission_code("anything.at_all"))
