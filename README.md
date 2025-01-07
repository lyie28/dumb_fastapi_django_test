
## Async FastAPI + Django
```uv pip sync requirements.txt```

###Set up DB
```bash
python manage.py makemigrations
python manage.py migrate
```

### Run fastapi server
```bash
uvicorn app.main:app --reload
```

### Test fetching data from django DB
```bash
curl http://localhost:8000/animals/
```
