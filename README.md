# Sample TRC-USDT Payment Platform Skeleton

This project contains a minimal demonstration of a payment platform similar in concept to **nowpayments** but simplified for local testing. It includes a Flask backend and very basic HTML pages for users and an admin.

## Requirements

- Python 3.8+
- `flask` package

Install dependencies:

```bash
pip install flask
```

## Running

Run the Flask app from the repo root:

```bash
python backend/app.py
```

Then open `http://localhost:5000/` for the user page or `http://localhost:5000/admin` for the admin page.

These pages use the REST endpoints under `/api/v1/` provided by the backend.

## Notes

This is only a skeleton to demonstrate API structure and basic interactions. It does **not** interact with the real TRON blockchain, perform authentication securely, or persist data. Use it as a starting point for further development.
