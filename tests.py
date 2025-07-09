import unittest
import uuid
from fastapi.testclient import TestClient
from api import app

class PaymentMethodTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.created_uuid = None

    def setUp(self):
        self.ac = TestClient(app)

    def tearDown(self):
        self.ac.close()

    def test_01_create_payment_method(self):
        payload = {
            "user_id": str(uuid.uuid4()),
            "owner": "John Doe",
            "number": "1234567812345678",
            "expiry": "12/25",
            "cvc": "123"
        }
        response = self.ac.post("/payment_method/", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["owner"], "John Doe")
        self.assertEqual(data["number"], "1234567812345678")
        self.assertEqual(data["expiry"], "12/25")
        self.assertEqual(data["cvc"], "123")
        self.assertIn("uuid", data)
        PaymentMethodTestCase.created_uuid = data["uuid"]

    def test_02_list_payment_methods(self):
        response = self.ac.get("/payment_method/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(any("uuid" in item for item in data))

    def test_03_get_payment_method_by_id(self):
        response = self.ac.get(f"/payment_method/{self.created_uuid}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["uuid"], self.created_uuid)

    def test_04_update_payment_method(self):
        update_payload = {
            "user_id": str(uuid.uuid4()),
            "owner": "Jane Doe",
            "number": "8765432187654321",
            "expiry": "11/30",
            "cvc": "321"
        }
        response = self.ac.put(f"/payment_method/{self.created_uuid}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["owner"], "Jane Doe")
        self.assertEqual(data["number"], "8765432187654321")

    def test_05_delete_payment_method(self):
        response = self.ac.delete(f"/payment_method/{self.created_uuid}")
        self.assertEqual(response.status_code, 204)

        # Confirm deletion
        response = self.ac.get(f"/payment_method/{self.created_uuid}")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()