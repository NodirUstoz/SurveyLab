# SurveyLab - Survey & Research Platform

A production-grade survey and research platform supporting advanced question types, branching logic, anonymous responses, real-time analytics, data export, quotas, and multi-language support.

## Features

- **Question Types**: Multiple choice, rating scales, matrix grids, open-ended text, NPS (Net Promoter Score)
- **Branching Logic**: Conditional page/question display based on previous answers
- **Anonymous Responses**: Configurable anonymity settings per survey
- **Response Analytics**: Real-time charts, cross-tabulations, and statistical summaries
- **Data Export**: CSV, Excel, and PDF export for responses and analytics
- **Quotas**: Set response limits by demographic or answer criteria
- **Multi-Language**: Full i18n support for surveys in multiple languages
- **Distribution**: Email invitations, shareable links, embedded surveys, QR codes
- **Organizations**: Multi-tenant support with team collaboration

## Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Backend      | Django 5.x + Django REST Framework |
| Frontend     | Vue.js 3 + Vuex + Vue Router      |
| Database     | PostgreSQL 16                      |
| Cache/Broker | Redis 7                           |
| Task Queue   | Celery 5.x                        |
| Containers   | Docker + Docker Compose            |
| Web Server   | Nginx                             |

## Architecture

```
                    +-------------+
                    |   Nginx     |
                    | (port 80)   |
                    +------+------+
                           |
              +------------+------------+
              |                         |
       +------+------+          +------+------+
       |  Vue.js SPA |          | Django API  |
       |  (static)   |          | (port 8000) |
       +-------------+          +------+------+
                                       |
                          +------------+------------+
                          |            |            |
                   +------+--+  +-----+----+  +----+-----+
                   |PostgreSQL|  |  Redis   |  |  Celery  |
                   |(port 5432)| |(port 6379)|  | (worker) |
                   +----------+  +----------+  +----------+
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/surveylab.git
   cd surveylab
   ```

2. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

4. Run database migrations:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. Access the application:
   - Frontend: http://localhost
   - API: http://localhost/api/
   - Admin: http://localhost/admin/

### Development

For local development without Docker:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Celery Worker:**
```bash
cd backend
celery -A config worker -l info
```

## API Documentation

The API follows RESTful conventions. Key endpoints:

| Endpoint                         | Method | Description                |
|----------------------------------|--------|----------------------------|
| `/api/v1/auth/register/`        | POST   | Register new user          |
| `/api/v1/auth/login/`           | POST   | Obtain JWT tokens          |
| `/api/v1/surveys/`              | GET    | List user surveys          |
| `/api/v1/surveys/`              | POST   | Create new survey          |
| `/api/v1/surveys/{id}/`         | GET    | Get survey details         |
| `/api/v1/surveys/{id}/publish/` | POST   | Publish survey             |
| `/api/v1/responses/submit/`     | POST   | Submit survey response     |
| `/api/v1/analytics/{id}/`       | GET    | Get survey analytics       |
| `/api/v1/distributions/`        | POST   | Create distribution        |

## Environment Variables

See `.env.example` for all available configuration options.

## Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
docker-compose exec frontend npm run test
```

## License

MIT License. See LICENSE for details.
