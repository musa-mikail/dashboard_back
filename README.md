# Nigerian Financial News Scraper Backend

A FastAPI-based backend service that scrapes and analyzes financial news from Nigerian sources, with a focus on sentiment analysis and topic tracking.

## Features

- Automated scraping of Nigerian financial news sources (currently Nairametrics)
- Real-time sentiment analysis of articles
- Topic extraction and trending topics tracking
- RESTful API endpoints for data access
- MySQL database for persistent storage
- Asynchronous scraping with rate limiting
- Scheduled scraping jobs

## Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- Git

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd naija_inference/backend
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory with the following content:
```env
DATABASE_URL=mysql+aiomysql://root:@localhost/naija_sentiment
```

5. Create the MySQL database:
```sql
CREATE DATABASE naija_sentiment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. Initialize the database:
```bash
python -m app.init_db
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

2. Access the API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

- `GET /`: API root
- `GET /articles/latest`: Get latest articles
- `GET /articles/trending`: Get trending articles
- `GET /topics/trending`: Get trending topics
- `GET /sources/status`: Get status of news sources
- `GET /scraping/logs`: Get scraping logs
- `POST /scraping/run`: Manually trigger scraping

## Scraping Schedule

The application automatically runs scraping jobs every 30 minutes. You can also trigger manual scraping using the `/scraping/run` endpoint.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── init_db.py           # Database initialization
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py          # Base scraper class
│   │   └── nairametrics.py  # Nairametrics scraper
│   └── services/
│       ├── __init__.py
│       └── scraping_service.py  # Scraping orchestration
├── requirements.txt
└── README.md
```

## Development

- The application uses FastAPI for the web framework
- SQLAlchemy for database ORM
- BeautifulSoup4 for web scraping
- NLTK and transformers for text analysis
- AsyncIO for concurrent operations

## Error Handling

- All scraping errors are logged in the database
- Failed scraping attempts are retried automatically
- Rate limiting is implemented to prevent server overload

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Git Deployment

### Initial Setup

1. Initialize Git repository (if not already done):
```bash
git init
```

2. Create a `.gitignore` file in the root directory:
```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.env
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

3. Add your files to Git:
```bash
git add .
```

4. Make your initial commit:
```bash
git commit -m "Initial commit: Nigerian Financial News Scraper Backend"
```

### Remote Repository Setup

1. Create a new repository on GitHub/GitLab/Bitbucket (don't initialize with README)

2. Add the remote repository:
```bash
git remote add origin <your-repository-url>
# Example: git remote add origin https://github.com/username/naija_inference.git
```

3. Push your code:
```bash
git push -u origin main  # or 'master' depending on your default branch name
```

### Regular Updates

1. Check status of your changes:
```bash
git status
```

2. Add new changes:
```bash
git add .
```

3. Commit changes with a descriptive message:
```bash
git commit -m "Description of your changes"
```

4. Push to remote repository:
```bash
git push
```

### Branch Management

1. Create a new feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Switch between branches:
```bash
git checkout branch-name
```

3. Merge changes from a branch:
```bash
git checkout main
git merge feature/your-feature-name
```

### Best Practices

- Always pull before pushing to avoid conflicts:
```bash
git pull origin main
```

- Keep commits atomic and focused on single features/fixes
- Write clear commit messages
- Regularly push your changes
- Use branches for new features
- Never commit sensitive data (passwords, API keys)
- Keep your `.env` file in `.gitignore` 