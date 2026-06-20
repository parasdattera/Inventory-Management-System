# Inventory Management System

A simple inventory management web application built with **Django**. It lets you
manage products, track stock coming in and going out, and keep an eye on items
that are running low.

This was built as an assessment submission.

## Features

- **Dashboard** with headline numbers (total products, total units, low-stock count),
  a low-stock alert list, and recent stock movements.
- **Product management** — full create / read / update / delete (CRUD).
- **Categories** to group products.
- **Stock in / stock out** — every change to a product's quantity is recorded as a
  transaction, so the current stock level is always explainable. You can't remove
  more stock than you actually have.
- **Low-stock alerts** — products at or below their reorder level are flagged.
- **Search & filter** products by name / SKU and by category.
- **Django admin** for power users.

## Tech stack

- Python 3.12
- Django 6.0
- SQLite (no database setup needed)
- Bootstrap 5 for styling (loaded from a CDN)

## Getting started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up the database
python manage.py migrate

# 4. (Optional) Load some sample data to play with
python manage.py seed_data

# 5. (Optional) Create your own admin user
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

Then open <http://127.0.0.1:8000/> in your browser.

### Admin login

A default admin account is created if you run `createsuperuser`. For quick local
testing you can also create one with these credentials:

- **Username:** `admin`
- **Password:** `admin123`

The admin panel is at <http://127.0.0.1:8000/admin/>.

## Running the tests

```bash
python manage.py test
```

## Project structure

```
inventory_system/        # Django project (settings, root URLs)
inventory/               # the main app
├── models.py            # Category, Product, StockTransaction
├── forms.py             # ModelForms for products and stock adjustments
├── views.py             # function-based views (dashboard, CRUD, stock adjust)
├── urls.py              # app URLs
├── admin.py             # admin registrations
├── tests.py             # unit tests for models and views
├── templates/inventory/ # Bootstrap templates
└── management/commands/
    └── seed_data.py     # sample data loader
```

## A few design notes

- **Stock changes go through transactions.** Once a product exists, its quantity is
  only changed via a stock-in / stock-out movement (`StockTransaction`). This keeps a
  history instead of just overwriting a number, and the product + transaction are
  saved together inside a database transaction so they never get out of sync.
- **Function-based views** were chosen over class-based views to keep the flow easy
  to read end to end.
- **SQLite** is used so the project runs with zero database configuration. For
  production you'd swap in PostgreSQL via the `DATABASES` setting.
