# SpyCatAgency
## Backend
### Prerequisites
- Python 3.12
- PostgreSQL database
- Environment variables configured

### Environment Variables
create your `.env` file in root directory (like in the `.env.example`)
```
LOGGING_LEVEL="INFO"

PG_USER="postgres"
PG_PASSWORD="postgres"
PG_HOST="localhost"
PG_DB="SpyCatAgency"
PG_PORT=5432
DATABASE_URL="postgresql+asyncpg://${PG_USER}:${PG_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_DB}"

VALIDATE_URL = "https://api.thecatapi.com/v1"
```

### Installation
```
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic revision --autogenerate
alembic upgrade head

# Start development server
python main.py
```

### API Documentation
- Swagger UI: http://127.0.0.1:8000/api/docs
- Postman collection: [here](./assets/openapi.json)


## Frontend
### Prerequisites
- Node.js 18+ or 20+
- npm or yarn package manager
- Backend API running on port 8000

### Environment Variables
`NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

### Installation
```
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```