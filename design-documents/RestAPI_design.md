# ReST API Design and Specifications 

## 1. User Account Management
### POST /users/signup
Input: JSON object containing username, password, email, and businessName.
Output:
Success: 201 Created with JSON object containing userId, username, and businessName.
Failure: 400 Bad Request if input validation fails.
Failure: 409 Conflict if username or email already exists.
Functional Logic:
Validate input data.
Hash and salt the password.
Create a new user in the database.
Return the user information.
### POST /users/login
Input: JSON object containing username and password.
Output:
Success: 200 OK with JSON Web Token for authentication.
Failure: 400 Bad Request if input validation fails.
Failure: 401 Unauthorized if username or password is incorrect.
Functional Logic:
Validate input data.
Retrieve user from database and check password.
Generate and return JSON Web Token.
## 2. Payment Processing
### POST /payments/charge
Input: JSON object containing cardNumber, expiryDate, cvv, amount, and userId.
Output:
Success: 201 Created with JSON object containing transaction details.
Failure: 400 Bad Request if input validation fails.
Failure: 402 Payment Required if card validation fails or insufficient funds.
Functional Logic:
Validate input data.
Validate card using the Lund Algorithm.
Process payment (instant for debit, 2 days processing for credit).
Save transaction details in database.
Return transaction details.
### GET /payments/balance
Input: Query parameters userId and optional startDate, endDate.
Output:
Success: 200 OK with JSON object containing total balance.
Failure: 400 Bad Request if input validation fails.
Failure: 404 Not Found if user not found.
Functional Logic:
Validate input data.
Retrieve and sum all processed transactions for the user (and within date range if provided).
Return total balance.
### GET /payments/transactions
Input: Query parameters userId.
Output:
Success: 200 OK with JSON array of transaction details.
Failure: 400 Bad Request if input validation fails.
Failure: 404 Not Found if user not found.
Functional Logic:
Validate input data.
Retrieve all transactions for the user.
Return transactions details.
## 3. Error Messages and HTTP Status Codes
200 OK: Request was successful.
201 Created: Resource was successfully created.
400 Bad Request: Input validation failed.
401 Unauthorized: Authentication failed.
402 Payment Required: Payment failed.
404 Not Found: Requested resource or user not found.
409 Conflict: Resource already exists (e.g., username or email).
500 Internal Server Error: Unexpected server error.