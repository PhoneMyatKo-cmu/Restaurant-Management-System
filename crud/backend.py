import hashlib
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist

class EmployeeBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        # SQL query to get employee info based on email
        query = "SELECT employee_id, employee_name, acc_password, employee_type,restaurant_id FROM employee WHERE email = %s"
     
        
        with connection.cursor() as cursor:
            cursor.execute(query, [email])
            employee = cursor.fetchone()
            print(employee)

        if employee:
            employee_id, employee_name, acc_password, employee_type,restaurant_id = employee
            # Compare password hash with stored SHA-2 hash
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if acc_password == hashed_password:
                # Return employee object (without ORM)
                return {
                    'employee_id': employee_id,
                    'employee_name': employee_name,
                    'employee_type': employee_type,
                    'restaurant_id':restaurant_id,
                }
        return None

    def get_user(self, user_id):
        # This method is typically used to fetch user details
        return None
