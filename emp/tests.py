from django.test import TestCase

from emp.models import Emp


class EmpDuplicateEmpIdTests(TestCase):
    def test_create_duplicate_emp_id_blocked(self):
        Emp.objects.create(
            name="Alice",
            emp_id="E123",
            phone="1234567890",
            address="Addr",
            working=True,
            department="CSE",
        )

        resp = self.client.post(
            "/emp/add-emp/",
            {
                "emp_name": "Bob",
                "emp_id": "E123",
                "emp_phone": "9999999999",
                "emp_address": "Addr2",
                "emp_working": "on",
                "emp_department": "ME",
            },
        )

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Employee ID already exists")
        self.assertEqual(Emp.objects.filter(emp_id="E123").count(), 1)

    def test_update_duplicate_emp_id_blocked(self):
        a = Emp.objects.create(
            name="Alice",
            emp_id="E123",
            phone="1234567890",
            address="Addr",
            working=True,
            department="CSE",
        )
        b = Emp.objects.create(
            name="Bob",
            emp_id="E456",
            phone="1111111111",
            address="Addr2",
            working=True,
            department="ME",
        )

        resp = self.client.post(
            f"/emp/do-update-emp/{b.id}",
            {
                "emp_name": "Bob",
                "emp_id": a.emp_id,
                "emp_phone": "1111111111",
                "emp_address": "Addr2",
                "emp_working": "on",
                "emp_department": "ME",
            },
        )

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Employee ID already exists")

        b.refresh_from_db()
        self.assertEqual(b.emp_id, "E456")
