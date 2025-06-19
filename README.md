# Jijenga Referral System Backend

This repository contains the backend service for the Jijenga Referral System, built with Python FastAPI and PostgreSQL.

## Getting Started

Clone the repository to your local machine:

```bash
git clone https://gitlab.com/jijenga-admin-group/Jijenga_Projects_JRMS.git
cd Jijenga_Projects_JRMS/backend # Navigate to the backend directory, if it dosent exist create it , the code will be separated in backend and client folders
```

## Prerequisites

Ensure you have the following installed:

*   **Python 3.10+**: The project is developed using Python 3.10 or newer.
*   **Poetry**: Used for dependency management. Install it by following the official documentation: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)
*   **PostgreSQL Database**: A running PostgreSQL instance is required. You can use a local installation or a cloud provider like Supabase.
*   **Docker or Podman**: For building and running the application in a container.

## Installation

Navigate to the backend directory and install the dependencies using Poetry:

```bash
poetry install
```

This will create a virtual environment and install all project dependencies.

## Configuration

Copy the example environment file and update it with your database credentials and API keys:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in the required values:

```dotenv
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
JWT_SECRET_KEY=your-secret-key-here
MPESA_API_KEY=your-mpesa-api-key
RESEND_API_KEY=your-resend-api-key
REFERRAL_BASE_URL=http://localhost:8000 # Or your frontend URL
```

**Note:** Ensure your `DATABASE_URL` uses the `postgresql+asyncpg` driver.

## Database Setup

The database schema is managed using Alembic migrations.

**For Development (Supabase Workaround):**

Due to potential issues with Alembic applying migrations directly to some Supabase configurations via the Session pooler, the initial schema might need to be created manually.

1.  Connect to your Supabase database using a tool like `psql` or the Supabase UI SQL Editor.
2.  Execute the SQL commands provided in the initial migration file (`alembic/versions/YOUR_REVISION_ID_create_initial_schema.py`) or use the manual creation script provided separately (if available). Ensure the `referral` schema and all tables are created.

**For Other Environments (Local PostgreSQL, etc.):**

Apply the database migrations using Alembic:

```bash
poetry run alembic upgrade head
```

This will create the necessary tables and schema in your database.

## Running the Application

Start the FastAPI development server using Poetry:

```bash
poetry run uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`. The API documentation can be accessed at `http://127.0.0.1:8000/docs` (Swagger UI) or `http://127.0.0.1:8000/redoc` (ReDoc).

## Running Tests

Execute the test suite using Poetry:

```bash
poetry run pytest -vv
```

Ensure all tests pass before pushing changes.

## Containerization

You can build a Docker or Podman image for the application:

```bash
podman build -t jijenga-referral-system-backend .
# Or for Docker: docker build -t jijenga-referral-system-backend .
```

Run the container:

```bash
podman run -p 8000:8000 --env-file .env jijenga-referral-system-backend
# Or for Docker: docker run -p 8000:8000 --env-file .env jijenga-referral-system-backend
```

## Project Structure

```
.
├── alembic/             # Alembic migration scripts
├── app/                 # Application source code
│   ├── api/             # API endpoints
│   │   └── v1/
│   │       ├── admin/   # Admin specific endpoints
│   │       └── router.py # V1 API router
│   ├── core/            # Core utilities (database, security)
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic services
│   ├── __init__.py
│   ├── config.py        # Application settings
│   ├── dependencies.py  # FastAPI dependencies
│   ├── exceptions.py    # Custom exceptions
│   └── main.py          # FastAPI application entry point
├── tests/               # Project tests
├── .env.example         # Example environment variables
├── Containerfile        # Containerization definition
├── poetry.lock          # Poetry lock file
├── pyproject.toml       # Poetry project definition
├── pytest.ini           # Pytest configuration
└── README.md            # Project documentation
```

---

This README provides a starting point for new developers to set up and run the project.
