"""Generate unique registration data for account-lifecycle tests.

Every call returns a fresh user with a unique email so parallel or repeated
runs never collide on 'Email Address already exist!'.
"""
from uuid import uuid4


def new_user() -> dict:
    uid = uuid4().hex[:10]
    return {
        "name": f"QA Bot {uid[:4]}",
        "email": f"qa.{uid}@example.com",
        "password": "S3cure!pass",
        "birth_day": "10",
        "birth_month": "May",
        "birth_year": "1995",
        "first_name": "QA",
        "last_name": "Bot",
        "company": "Example QA Ltd",
        "address": "221B Baker Street",
        "address2": "Floor 2",
        "country": "United States",
        "state": "California",
        "city": "San Francisco",
        "zipcode": "94016",
        "mobile_number": "5550100200",
    }
