import unittest
import uuid
from fastapi.testclient import TestClient
from api import app

class PaymentMethodTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_id = str(uuid.uuid4())
        cls.created_uuid = None

    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_01_create_payment_method(self):
        payload = {
            "user": self.user_id,
            "owner_name": "John Doe",
            "card_number": "1234567812345678",
            "expiration_date": "12/2025",
            "security_code": "123"
        }
        response = self.client.post("/payment_method", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["owner_name"], "John Doe")
        self.assertEqual(data["card_number"], "1234567812345678")
        self.assertEqual(data["expiration_date"], "12/2025")
        self.assertEqual(data["security_code"], "123")
        self.assertIn("uuid", data)
        PaymentMethodTestCase.created_uuid = data["uuid"]

    def test_02_list_payment_methods(self):
        response = self.client.get(f"/payment_method?user={self.user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(any(item["uuid"] == self.created_uuid for item in data))

    def test_03_update_payment_method(self):
        update_payload = {
            "owner_name": "Jane Doe",
            "card_number": "8765432187654321",
            "expiration_date": "11/2030",
            "security_code": "321"
        }
        response = self.client.patch(f"/payment_method?user={self.user_id}&uuid={self.created_uuid}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["owner_name"], "Jane Doe")
        self.assertEqual(data["card_number"], "8765432187654321")
        self.assertEqual(data["expiration_date"], "11/2030")
        self.assertEqual(data["security_code"], "321")

    def test_04_delete_payment_method(self):
        response = self.client.delete(f"/payment_method?user={self.user_id}&uuid={self.created_uuid}")
        self.assertEqual(response.status_code, 204)
        # Confirm deletion
        response = self.client.get(f"/payment_method?user={self.user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(any(item["uuid"] == self.created_uuid for item in data))

if __name__ == "__main__":
    unittest.main()