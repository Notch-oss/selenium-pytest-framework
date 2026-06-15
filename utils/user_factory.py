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


def new_api_user() -> dict:
    """Registration payload keyed by the exact field names the createAccount /
    updateAccount APIs expect.

    The API uses different keys than the signup UI form (`birth_date` not
    `birth_day`, `firstname`/`lastname` not `first_name`/`last_name`, `address1`
    not `address`, plus a required `title`), so this is kept separate from
    `new_user()` rather than mapped at the call site. Every call returns a unique
    email so repeated or parallel runs never collide on an existing account.
    """
    uid = uuid4().hex[:10]
    return {
        "name": f"QA Bot {uid[:4]}",
        "email": f"qa.api.{uid}@example.com",
        "password": "S3cure!pass",
        "title": "Mr",
        "birth_date": "10",
        "birth_month": "May",
        "birth_year": "1995",
        "firstname": "QA",
        "lastname": "Bot",
        "company": "Example QA Ltd",
        "address1": "221B Baker Street",
        "address2": "Floor 2",
        "country": "United States",
        "zipcode": "94016",
        "state": "California",
        "city": "San Francisco",
        "mobile_number": "5550100200",
    }
