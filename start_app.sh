echo "Running migrations..."

alembic upgrade head

echo "Running app..."

python src/main.py
