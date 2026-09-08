import os
import unittest
from app import app
from database import init_db, get_db

class FinanceTrackerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()
        init_db()

    def test_full_user_flow_and_isolation(self):
        # 1. Register User 1 (Alice)
        res = self.client.post('/register', data={
            'full_name': 'Alice Smith',
            'username': 'alice',
            'email': 'alice@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'currency': '₹'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration successful', res.data)

        # 2. Login as Alice
        res = self.client.post('/login', data={
            'username_or_email': 'alice',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Alice Smith', res.data)

        # 3. Add Income for Alice (+50,000)
        res = self.client.post('/transactions/add', data={
            'type': 'income',
            'amount': '50000.00',
            'category': 'Salary',
            'description': 'Tech Corp Monthly Salary',
            'date': '2026-09-01'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'50000.00', res.data)

        # 4. Add Expense for Alice (-15,000)
        res = self.client.post('/transactions/add', data={
            'type': 'expense',
            'amount': '15000.00',
            'category': 'Rent & Housing',
            'description': 'Apartment Rent',
            'date': '2026-09-02'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'35000.00', res.data) # Balance should be 35,000

        # 5. Log Attendance for Alice
        res = self.client.post('/attendance/mark', data={
            'date': '2026-09-02',
            'status': 'Present',
            'check_in': '09:00',
            'check_out': '18:00',
            'notes': 'All tasks completed'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 6. Logout Alice
        self.client.get('/logout', follow_redirects=True)

        # 7. Register User 2 (Bob)
        res = self.client.post('/register', data={
            'full_name': 'Bob Jones',
            'username': 'bob',
            'email': 'bob@test.com',
            'password': 'password456',
            'confirm_password': 'password456',
            'currency': '$'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 8. Login as Bob
        res = self.client.post('/login', data={
            'username_or_email': 'bob',
            'password': 'password456'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Bob Jones', res.data)

        # 9. Verify Bob has a FRESH START: 0 balance, no transactions from Alice!
        self.assertIn(b'$0.00', res.data)
        self.assertNotIn(b'Tech Corp Monthly Salary', res.data)
        self.assertNotIn(b'Apartment Rent', res.data)
        self.assertIn(b'No transactions found', res.data)

        # 10. Add Bob's own transaction ($1,200 income)
        res = self.client.post('/transactions/add', data={
            'type': 'income',
            'amount': '1200.00',
            'category': 'Freelance',
            'description': 'Website Design for Client',
            'date': '2026-09-02'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'1200.00', res.data)

        print("\nAll automated tests passed successfully! Data isolation & calculations verified.")

if __name__ == '__main__':
    unittest.main()
