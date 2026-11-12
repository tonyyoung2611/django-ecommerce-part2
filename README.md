
# Django eCommerce Application

## Project Overview

This project is a Django-based eCommerce application developed as part of the ASU Software Engineering Bootcamp.

The application supports buyer and vendor accounts, online stores, product listings, shopping carts, checkout, orders, product reviews, and REST API functionality.

## Features

- Buyer and vendor registration and login
- Vendor store and product management
- Product listings and shopping cart
- Buyer checkout and order confirmation
- Product reviews and verified purchase indicators
- Password reset functionality
- REST API using Django REST Framework
- Vendor-only API permissions
- Reddit feed integration with error handling

## Technologies Used

- Python
- Django
- Django REST Framework
- MariaDB 11.8
- mysqlclient
- Requests
- HTML
- JSON

## Installation Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/tonyyoung2611/django-ecommerce-part2.git
cd ecommerce_project
```

Replace `YOUR_REPOSITORY_URL` with the actual GitHub repository URL. If the repository contains an additional project folder, navigate into the folder containing `manage.py`.

### 2. Create a Virtual Environment

```bash
python -m venv myenv
```

### 3. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\myenv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure MariaDB

Install MariaDB Server 11.8 and log in as the root user.

Create the database and application user:

```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'YOUR_SECURE_PASSWORD';

GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
```

Replace `YOUR_SECURE_PASSWORD` with your own secure password.

In Windows PowerShell, set the database password:

```powershell
$env:ECOMMERCE_DB_PASSWORD = Read-Host "Enter your MariaDB ecommerce_user password"
```

The password must match the one configured in MariaDB.

Keep this environment variable set in the terminal used to run Django.

Do not commit passwords or other sensitive credentials to GitHub.

### 6. Apply Database Migrations

```bash
python manage.py migrate
```

### 7. Create an Administrator Account

```bash
python manage.py createsuperuser
```

### 8. Start the Django Server

```bash
python manage.py runserver 8001
```

Open the application at:

http://127.0.0.1:8001/

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/vendors/1/stores/ | Retrieve vendor stores |
| GET | /api/stores/1/products/ | Retrieve store products |
| GET | /api/products/1/reviews/ | Retrieve reviews as an authorized vendor |
| POST | /api/stores/create/ | Create a store as a vendor |
| POST | /api/products/create/ | Create a product as a vendor |

The numeric IDs in these URLs are examples. Use IDs from your own database.

## Authentication and Authorization

Store and product creation require an authenticated vendor account.

Vendors can only add products to stores they own.

Product review retrieval is restricted to vendors who own the corresponding product.

## Reddit Integration

Visit:

http://127.0.0.1:8001/reddit/

The application attempts to retrieve posts from the Python subreddit.

During testing, Reddit returned HTTP 403 Forbidden. The application handles this error gracefully, although live posts could not be displayed.

## Testing

The following operations were successfully tested:

- Retrieve vendor stores — HTTP 200
- Retrieve store products — HTTP 200
- Retrieve product reviews — HTTP 200
- Create a store — HTTP 201
- Create a product — HTTP 201
- Block unauthenticated store creation — HTTP 403
- Block buyer store creation — HTTP 403

## Project Status

The eCommerce application and its REST API are functional in the local development environment.

The project uses MariaDB as its database, with migrations completed and existing eCommerce data successfully imported.

Further improvements include resolving the Reddit access restriction and expanding automated tests.

## Author

Tony Young

ASU Software Engineering Bootcamp
