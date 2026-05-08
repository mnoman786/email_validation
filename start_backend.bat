@echo off
chcp 65001 >NUL
echo ========================================
echo   EmailGuard Backend - Local Dev
echo ========================================

cd /d "%~dp0backend"

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv. Make sure Python 3.9+ is installed.
        pause
        exit /b 1
    )
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install/update dependencies
echo [2/5] Installing dependencies...
pip install -r requirements_local.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

:: Copy .env.local if .env doesn't exist
if not exist ".env" (
    echo Copying .env.local to .env...
    copy .env.local .env >NUL
)

:: Run migrations
echo [3/5] Running migrations...
set DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py migrate --run-syncdb 2>&1 | findstr /v "^$" | findstr /v "Applying"

:: Seed data
echo [4/5] Seeding initial data...
python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.billing.models import Subscription, CreditPack
User = get_user_model()
if not User.objects.filter(email='admin@emailguard.io').exists():
    u = User.objects.create_superuser('admin@emailguard.io', 'admin123')
    u.first_name = 'Admin'; u.is_verified = True; u.save()
    Subscription.objects.get_or_create(user=u, defaults={'plan':'pro','available_credits':99999})
    print('Admin user created: admin@emailguard.io / admin123')
packs=[('Starter Pack',1000,9.99,False),('Growth Pack',5000,29.99,True),('Pro Pack',25000,99.99,False),('Enterprise Pack',100000,299.99,False)]
[CreditPack.objects.get_or_create(name=n,defaults={'credits':c,'price_usd':p,'is_active':True,'is_popular':pop}) for n,c,p,pop in packs]
print('Setup complete!')
"

:: Import disposable domain blocklist (try GitHub, fallback to local)
echo [5/5] Updating disposable domain blocklist...
python manage.py update_disposable_domains --source github
if errorlevel 1 (
    python manage.py update_disposable_domains --source local
)

echo.
echo ========================================
echo   Backend is RUNNING
echo ----------------------------------------
echo   API:      http://localhost:8000
echo   Docs:     http://localhost:8000/api/docs/
echo   Admin:    http://localhost:8000/admin
echo   Login:    admin@emailguard.io / admin123
echo ========================================
echo   Press CTRL+C to stop
echo.

python manage.py runserver 0.0.0.0:8000

pause
