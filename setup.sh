#!/bin/bash
# Smart Aquarium Setup Script

echo "================================"
echo "Smart Aquarium Setup"
echo "================================"

# Check Python installation
echo -e "\n[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Install dependencies
echo -e "\n[2/5] Installing Python packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi
echo "✓ Packages installed successfully"

# Database migrations
echo -e "\n[3/5] Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Migration failed"
    exit 1
fi
echo "✓ Migrations completed"

# Collect static files
echo -e "\n[4/5] Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "ERROR: Static files collection failed"
    exit 1
fi
echo "✓ Static files collected"

# Create superuser
echo -e "\n[5/5] Creating admin user..."
echo "Please enter admin username:"
read username
echo "Please enter admin email:"
read email
echo "Please enter admin password:"
read -s password
echo "Please confirm password:"
read -s password_confirm

if [ "$password" != "$password_confirm" ]; then
    echo "ERROR: Passwords do not match"
    exit 1
fi

python manage.py shell << END
from django.contrib.auth.models import User
if not User.objects.filter(username='$username').exists():
    User.objects.create_superuser('$username', '$email', '$password')
    print("✓ Admin user created successfully")
else:
    print("✓ Admin user already exists")
END

echo -e "\n================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update MySQL credentials in smartAquarium/settings.py"
echo "2. Update API key in api/views.py"
echo "3. Run: python manage.py runserver"
echo "4. Visit: http://localhost:8000"
echo ""
