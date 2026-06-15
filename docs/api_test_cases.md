# AutomationExercise API Test Cases

Source: https://automationexercise.com/api_list (verified against the live API 2026-06-16)

These are the 14 documented REST endpoints, implemented in `tests/test_api.py`
against `api/automation_exercise_api.py`.

## The one quirk that matters

Every endpoint answers with transport status **`200 OK`** and a
`Content-Type: text/html` body. The *real* status code is carried inside the JSON
body as `responseCode`. Tests therefore assert on `ApiResponse.response_code`,
not on the HTTP status line. The negative cases additionally assert
`http_status == 200` to keep that quirk pinned down.

| API | Method | Endpoint | Parameters | `responseCode` | Body message / key |
|---|---|---|---|---|---|
| 1 | GET | `/api/productsList` | — | 200 | `products` list |
| 2 | POST | `/api/productsList` | — | 405 | `This request method is not supported.` |
| 3 | GET | `/api/brandsList` | — | 200 | `brands` list |
| 4 | PUT | `/api/brandsList` | — | 405 | `This request method is not supported.` |
| 5 | POST | `/api/searchProduct` | `search_product` | 200 | `products` list |
| 6 | POST | `/api/searchProduct` | — (missing) | 400 | `Bad request, search_product parameter is missing in POST request.` |
| 7 | POST | `/api/verifyLogin` | `email`, `password` | 200 | `User exists!` |
| 8 | POST | `/api/verifyLogin` | `password` (no email) | 400 | `Bad request, email or password parameter is missing in POST request.` |
| 9 | DELETE | `/api/verifyLogin` | — | 405 | `This request method is not supported.` |
| 10 | POST | `/api/verifyLogin` | `email`, `password` (invalid) | 404 | `User not found!` |
| 11 | POST | `/api/createAccount` | full account form\* | 201 | `User created!` |
| 12 | DELETE | `/api/deleteAccount` | `email`, `password` | 200 | `Account deleted!` |
| 13 | PUT | `/api/updateAccount` | full account form\* | 200 | `User updated!` |
| 14 | GET | `/api/getUserDetailByEmail` | `email` | 200 | `user` object |

\* createAccount / updateAccount form fields: `name`, `email`, `password`,
`title`, `birth_date`, `birth_month`, `birth_year`, `firstname`, `lastname`,
`company`, `address1`, `address2`, `country`, `zipcode`, `state`, `city`,
`mobile_number`. Built by `utils.user_factory.new_api_user()`.

## Notes verified against the live API

- `createAccount` uses different field names than the signup UI form
  (`birth_date`/`firstname`/`lastname`/`address1` vs the UI's
  `birth_day`/`first_name`/`last_name`/`address`), which is why there is a
  dedicated `new_api_user()` factory.
- `getUserDetailByEmail` returns the stored profile (`first_name`, `last_name`,
  `address1`, `city`, …) but never the password or mobile number.
- `updateAccount` changes are immediately reflected by `getUserDetailByEmail`
  (test 13 cross-checks this).
- Deleting an account that does not exist returns `responseCode 404`
  (`Account not found!`), which is what makes fixture teardown idempotent.
- Account-lifecycle tests mint a unique email per run, so repeated or parallel
  runs never collide on an existing account, and every account they create is
  deleted on teardown.
