# ReHearten - Bus Booking Management System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

**ReHearten** is a comprehensive bus booking management system built with Django and PostgreSQL. The system provides a complete solution for managing bus routes, trips, bookings, and payments with both web frontend and RESTful API.

### 🎯 Mission
To provide a reliable, scalable platform for bus ticket booking and management, streamlining operations for both administrators and customers.

## ✨ Features

### 🔐 Authentication & User Management
- **Multi-role User System**: Admin and regular user roles with different permissions
- **Google OAuth2 Integration**: Seamless login with Google accounts
- **Secure Session Management**: Custom session tracking with UserSession model
- **User Profile Management**: Complete user profile editing and management
- **Password Security**: Secure password hashing using Django's built-in hashers
- **Custom Authentication Backend**: Flexible authentication system supporting multiple backends

### 🚌 Bus & Route Management
- **Location Management**: Create and manage bus stations and locations
- **Route Configuration**: Define routes with start/end locations and distances
- **Bus Fleet Management**: Track buses with license plates, models, and seating capacity
- **Seat Management**: Automatic seat assignment and availability tracking
- **Trip Scheduling**: Schedule trips with departure/arrival times and pricing

### 🎫 Booking System
- **Real-time Seat Selection**: Choose specific seats with availability checking
- **Booking Workflow**: Pending → Confirmed/Canceled status management
- **Multi-seat Booking**: Book multiple seats in a single transaction
- **Booking Validation**: Prevent double-booking with unique constraints
- **Ticket Generation**: Automatic ticket creation with passenger details
- **Booking History**: Track all user bookings with detailed information

### 💳 Payment Processing
- **Multiple Payment Methods**: Credit Card, PayPal, Bank Transfer
- **Payment Tracking**: Track payment status (Pending → Completed/Failed)
- **Transaction Management**: Unique transaction codes for each payment
- **Payment Summaries**: Detailed payment information and receipts

### 🎨 Modern User Interface
- **Responsive Design**: Beautiful, modern UI that works on all devices
- **Role-based Dashboards**: Separate interfaces for admin and regular users
- **Real-time Updates**: Dynamic content updates without page refresh
- **Accessibility**: Designed with accessibility best practices

### 🔧 Technical Features
- **PostgreSQL Database**: Robust relational database with proper constraints
- **RESTful API**: Comprehensive API endpoints using Django REST Framework
- **Social Authentication**: Google OAuth2 integration via social-auth-app-django
- **Session Management**: Cache-based session handling with custom UserSession tracking
- **Admin Dashboard**: Comprehensive Django admin panel for system management
- **Logging System**: Comprehensive logging to both console and file (logs/django.log)
- **Vietnamese Localization**: Full support for Vietnamese language (vi-VN)

## 🛠️ Technology Stack

### Backend
- **Python 3.12+**: Core programming language
- **Django 4.2+**: Web framework for rapid development
- **Django REST Framework**: API development
- **PostgreSQL**: Primary relational database (psycopg2-binary)
- **Social Auth App Django**: OAuth2 authentication (Google)
- **MongoDB**: Secondary database support (mongoengine, pymongo)

### AI Integration
- **OpenAI**: AI-powered features
- **Anthropic Claude**: Advanced AI capabilities

### Frontend
- **Bootstrap 5.3**: Responsive CSS framework
- **Font Awesome 6**: Icon library
- **Inter Font**: Modern typography
- **Custom CSS/JS**: Tailored styling and interactions

### Development Tools
- **uv**: Fast Python package installer (recommended)
- **Python-dotenv**: Environment variable management
- **Pillow**: Image processing
- **Cryptography**: Security features
- **Django CORS Headers**: Cross-origin resource sharing
- **Django Debug Toolbar**: Development debugging

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- PostgreSQL 15 or higher
- Google OAuth2 credentials (optional, for social login)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nguyenhieu277/rehearten.git
   cd Bus_Booking_System
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # or using pip
   pip install -r pyproject.toml
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required environment variables:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True

   # PostgreSQL Database
   DB_NAME=bus_booking_management
   DB_USER=postgres
   DB_PASSWORD=your-postgres-password
   DB_HOST=localhost
   DB_PORT=5432

   # Google OAuth2 (Optional)
   GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
   GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
   ```

4. **Database Setup**
   ```bash
   # Install and start PostgreSQL
   # Create database
   createdb bus_booking_management

   # Run migrations
   python manage.py migrate

   # Optional: Load initial data
   psql bus_booking_management < init_db_new.sql
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin/
   - API docs: See [API Endpoints](#-api-endpoints) section

## 📁 Project Structure

```
Bus_Booking_System/
├── accounts/                    # User authentication and management
│   ├── models.py               # User and UserSession models
│   ├── user_model.py           # Extended User model implementation
│   ├── session_model.py        # Custom session model
│   ├── views.py                # Authentication and user management views
│   ├── backends.py             # Custom authentication backend (AuthUserBackend)
│   ├── process_login_gg.py     # Google OAuth2 pipeline customization
│   ├── db_utils.py             # Database utility functions
│   ├── decorators.py           # Custom decorators for permissions
│   ├── forms.py                # Django forms
│   ├── urls.py                 # Account URLs (web pages and APIs)
│   └── utils.py                # Helper utilities
├── transport/                   # Transportation models and APIs
│   ├── models.py               # Locations, Route, Bus, Seat, Trip
│   ├── views.py                # REST API ViewSets
│   ├── views_frontend.py       # Frontend views (trip seats)
│   ├── serializers.py          # API serializers
│   ├── urls.py                 # API URLs
│   └── urls_frontend.py        # Frontend URLs
├── bookings/                    # Booking management
│   ├── models.py               # Booking and Ticket models
│   ├── views.py                # Booking and Ticket ViewSets
│   ├── serializers.py          # Booking serializers
│   └── urls.py                 # Booking API URLs
├── payments/                    # Payment processing
│   ├── models.py               # Payment and Wallet models
│   ├── views.py                # Payment ViewSets and update methods
│   ├── serializers.py          # Payment serializers
│   └── urls.py                 # Payment API URLs
├── utils/                       # Shared utilities
│   └── db_utils.py             # Database helper functions
├── REHEARTEN/                   # Django project settings
│   ├── settings.py             # Main configuration
│   ├── urls.py                 # Main URL routing
│   ├── wsgi.py                 # WSGI configuration
│   └── asgi.py                 # ASGI configuration
├── templates/                   # HTML templates
├── static/                      # Static files (CSS, JS, images)
├── logs/                        # Application logs (django.log)
├── migrations/                  # Custom migrations directory
├── manage.py                    # Django management script
├── main.py                      # Additional entry point
├── pyproject.toml              # uv project dependencies
├── uv.lock                     # uv lock file
├── init_db_new.sql             # Latest database initialization script
├── init_db_old.sql             # Legacy database initialization script
├── script.sql                  # Additional SQL scripts
├── CLAUDE.md                   # AI assistant guidance
├── POSTMAN_API_GUIDE.md        # API documentation for transport/bookings
├── POSTMAN_PAYMENTS_GUIDE.md   # API documentation for payments
├── LICENSE                     # MIT License
└── .env.example                # Environment variables template
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# PostgreSQL Database
DB_NAME=bus_booking_management
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432

# Google OAuth2 (Optional)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
```

### Google OAuth2 Setup (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth2 credentials (Web application)
5. Add authorized redirect URIs:
   - `http://localhost:8000/oauth/complete/google-oauth2/`
6. Copy Client ID and Client Secret to your `.env` file
7. The system uses a custom OAuth2 pipeline (process_login_gg) for session synchronization

## 👥 User Roles

### Admin Users
- Full system access
- User management capabilities
- Booking confirmation/cancellation
- System statistics and monitoring
- Route and trip management

### Regular Users
- Personal profile management
- Browse available trips
- Book and manage tickets
- View booking history
- Make payments

## 📊 API Endpoints

For detailed API documentation with request/response examples, see:
- **Transport & Bookings**: [POSTMAN_API_GUIDE.md](POSTMAN_API_GUIDE.md)
- **Payments**: [POSTMAN_PAYMENTS_GUIDE.md](POSTMAN_PAYMENTS_GUIDE.md)

### Web Pages (Frontend)
```
GET  /                           # Home page
GET  /register/                  # Registration page
GET  /login/                     # Login page
POST /logout/                    # Logout action
GET  /dashboard/                 # User dashboard
GET  /admin-dashboard/           # Admin dashboard
GET  /profile/                   # User profile page
GET  /users/                     # User management (admin only)
GET  /users/edit/<username>/     # Edit user page (admin only)
```

### Authentication APIs
```
POST /api/change-password/       # Change user password
POST /api/profile/               # Update user profile
GET  /api/get-profile/           # Get user profile data
```

### User Management APIs (Admin)
```
GET  /api/users/                 # List all users
POST /api/change-user-role/      # Change user role (admin/user)
POST /api/toggle-user-status/    # Toggle user active status
```

### OAuth2
```
GET  /oauth/login/google-oauth2/ # Initiate Google login
GET  /oauth/complete/google-oauth2/ # OAuth2 callback
```

### Transport APIs
```
GET    /api/locations/           # List locations
POST   /api/locations/           # Create location
GET    /api/locations/{id}/      # Get location details
PUT    /api/locations/{id}/      # Update location
DELETE /api/locations/{id}/      # Delete location

GET    /api/routes/              # List routes
POST   /api/routes/              # Create route
GET    /api/routes/{id}/         # Get route details
PUT    /api/routes/{id}/         # Update route
DELETE /api/routes/{id}/         # Delete route

GET    /api/buses/               # List buses
POST   /api/buses/               # Create bus
GET    /api/buses/{id}/          # Get bus details
PUT    /api/buses/{id}/          # Update bus
DELETE /api/buses/{id}/          # Delete bus

GET    /api/seats/               # List seats
POST   /api/seats/               # Create seat
GET    /api/seats/{id}/          # Get seat details
PUT    /api/seats/{id}/          # Update seat
DELETE /api/seats/{id}/          # Delete seat

GET    /api/trips/               # List trips
POST   /api/trips/               # Create trip
GET    /api/trips/{id}/          # Get trip details
PUT    /api/trips/{id}/          # Update trip
DELETE /api/trips/{id}/          # Delete trip
GET    /api/trip/{trip_id}/seats/ # Get trip seats with booking status
```

### Bookings APIs
```
GET    /api/bookings/            # List bookings (filtered by role)
POST   /api/bookings/            # Create booking with tickets
GET    /api/bookings/{id}/       # Get booking details
PUT    /api/bookings/{id}/       # Update booking (pending only)
DELETE /api/bookings/{id}/       # Delete booking
POST   /api/bookings/{id}/confirm/ # Confirm booking (admin)
POST   /api/bookings/{id}/cancel/ # Cancel booking
GET    /api/bookings/my-bookings/ # Get user's bookings
GET    /api/bookings/statistics/ # Get statistics (admin)
GET    /api/bookings/{id}/tickets/ # Get booking tickets
```

### Tickets APIs
```
GET    /api/tickets/             # List tickets (filtered by user)
GET    /api/tickets/{id}/        # Get ticket details
```

### Payments APIs
```
GET    /api/payments/            # List payments
POST   /api/payments/            # Create payment
GET    /api/payments/{id}/       # Get payment details
PUT    /api/payments/{id}/       # Update payment
DELETE /api/payments/{id}/       # Delete payment
POST   /payment/{payment_id}/update-method/ # Update payment method

GET    /api/wallets/             # List wallets
POST   /api/wallets/             # Create wallet
GET    /api/wallets/{id}/        # Get wallet details
PUT    /api/wallets/{id}/        # Update wallet
DELETE /api/wallets/{id}/        # Delete wallet
```

## 🗃️ Database Schema

### Database Initialization
The project includes SQL initialization scripts:
- `init_db_new.sql` - Latest schema with all features
- `init_db_old.sql` - Legacy schema for reference
- `script.sql` - Additional database scripts

### Key Models and Relationships

```
User (accounts.User)
├── role: 'admin' or 'user'
├── is_staff/is_superuser (auto-synced with role)
├── OneToMany → UserSession
├── OneToMany → Booking
└── OneToMany → Wallet

Locations
├── location_name, address, city
└── Referenced by Routes (start/end)

Route
├── start_location → Locations
├── end_location → Locations
├── distance_km, estimated_duration
└── OneToMany → Trip

Bus
├── license_plate, model, total_seats
└── OneToMany → Seat

Seat
├── ForeignKey → Bus
├── seat_number (unique per bus)
└── OneToMany → Ticket

Trip
├── ForeignKey → Route
├── ForeignKey → Bus
├── departure_time, arrival_time
├── price_per_seat, available_seats
└── OneToMany → Booking

Booking
├── ForeignKey → User
├── ForeignKey → Trip
├── status: 'Pending', 'Confirmed', 'Canceled'
├── number_of_seats, total_amount
├── OneToMany → Ticket
└── OneToOne → Payment

Ticket
├── ForeignKey → Booking
├── ForeignKey → Trip
├── ForeignKey → Seat
└── passenger details (first_name, last_name, etc.)

Payment
├── ForeignKey → Booking
├── ForeignKey → User
├── ForeignKey → Wallet (optional)
├── payment_method: 'Credit Card', 'PayPal', 'Bank Transfer', 'Wallet'
├── status: 'Pending', 'Completed', 'Failed'
└── transaction_code, amount

Wallet
├── ForeignKey → User
└── balance
```

### Important Constraints
- `Ticket`: Unique constraint on (trip, seat) - prevents double booking
- `Route`: Unique constraint on (start_location, end_location)
- `Seat`: Unique constraint on (bus, seat_number)
- `User`: Unique username and email
- `Booking.total_amount`: Auto-calculated as number_of_seats × trip.price_per_seat
- `Trip.available_seats`: Calculated based on bookings

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Django's built-in hashers
- **Custom Authentication Backend**: AuthUserBackend with raw SQL query protection
- **Custom Session Management**: UserSession model for tracking user sessions
- **Cache-based Sessions**: SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
- **CSRF Protection**: Cross-site request forgery protection enabled
- **OAuth2 Security**: Secure social authentication with Google via social-auth-app-django
- **Custom OAuth2 Pipeline**: process_login_gg for session synchronization
- **Custom Middleware**: SyncCustomSessionMiddleware for session management
- **Input Validation**: Comprehensive form and API validation
- **SQL Injection Protection**: Parameterized queries in db_utils.py
- **Role-based Access Control**: Permission system with admin/user roles
- **CORS Headers**: Configurable cross-origin resource sharing

## 🛠️ Management Commands

```bash
# Create superuser
python manage.py createsuperuser

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Show migrations
python manage.py showmigrations

# Collect static files
python manage.py collectstatic

# Create cache table (if needed)
python manage.py createcachetable

# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080
```

**Note**: User role management commands (list_users, change_user_role) mentioned in CLAUDE.md are not currently implemented as management commands. Use the web interface or API endpoints instead:
- Web: `/users/` (admin dashboard)
- API: `/api/change-user-role/` and `/api/toggle-user-status/`

## 🧪 Testing

Currently no test suite is configured. To add tests:

```bash
python manage.py test <app_name>
# Example: python manage.py test accounts
python manage.py test bookings
```

## 🚀 Deployment

### Production Checklist
1. **Security Settings**
   - Set `DEBUG=False` in settings.py
   - Configure `ALLOWED_HOSTS` properly (remove '*')
   - Set `SECRET_KEY` from secure environment variable
   - Enable HTTPS/SSL certificates

2. **Database Configuration**
   - Configure production PostgreSQL database
   - Set up database connection pooling
   - Configure database backups and replication
   - Run migrations: `python manage.py migrate`

3. **Static & Media Files**
   - Collect static files: `python manage.py collectstatic`
   - Set up static file serving (whitenoise, nginx, or CDN)
   - Configure STATIC_ROOT and MEDIA_ROOT properly

4. **Security Enhancements**
   - Configure CORS properly (update CORS_ORIGIN_ALLOW_ALL)
   - Set up CSRF_TRUSTED_ORIGINS
   - Enable secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
   - Configure SECURE_SSL_REDIRECT

5. **Monitoring & Logging**
   - Review logging configuration in settings.py
   - Set up log rotation for logs/django.log
   - Configure error monitoring (Sentry, etc.)
   - Set up application performance monitoring

6. **Authentication & Sessions**
   - Review authentication backend configuration
   - Configure session timeout appropriately
   - Set up cache backend for sessions (Redis recommended)
   - Verify Google OAuth2 credentials for production domain

7. **Environment Variables**
   - All secrets in .env file (never commit)
   - Configure SECRET_KEY, DB credentials
   - Set GOOGLE_OAUTH2_CLIENT_ID and SECRET for production

8. **WSGI/ASGI Server**
   - Use production server (gunicorn, uWSGI, or Daphne)
   - Configure worker processes
   - Set up reverse proxy (nginx or Apache)

### Example Production Command
```bash
# Using gunicorn
gunicorn REHEARTEN.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Using uWSGI
uwsgi --http :8000 --module REHEARTEN.wsgi --master --processes 4
```

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the project structure
4. Add tests if applicable
5. Update documentation (README.md, POSTMAN guides, CLAUDE.md)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Submit a pull request to `develop` branch

### Development Guidelines
- Follow Django best practices and PEP 8 style guide
- Use meaningful variable and function names
- Write docstrings for complex functions
- Keep models, views, and serializers organized
- Update API documentation when adding new endpoints
- Test your changes thoroughly before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PTIT (Posts and Telecommunications Institute of Technology)** - Academic institution
- **Django Community** - Excellent web framework
- **Django REST Framework** - Powerful API toolkit
- **PostgreSQL** - Robust database system

## 📞 Support & Documentation

- **Issues**: [GitHub Issues](https://github.com/nguyenhieu277/rehearten/issues)
- **Technical Documentation**: See [CLAUDE.md](CLAUDE.md) for detailed technical guidance
- **API Documentation**:
  - [POSTMAN_API_GUIDE.md](POSTMAN_API_GUIDE.md) - Transport & Bookings APIs
  - [POSTMAN_PAYMENTS_GUIDE.md](POSTMAN_PAYMENTS_GUIDE.md) - Payments APIs
- **Project Structure**: Refer to the [Project Structure](#-project-structure) section above

## ⚠️ Important Notes

### Development Mode
- `DEBUG=True` in settings.py (development only)
- `ALLOWED_HOSTS = ['*']` (development only)
- Some authentication checks may be relaxed for testing
- Comprehensive logging enabled to logs/django.log

### Database Architecture
- Primary database: PostgreSQL (relational data, Django models)
- MongoDB support available (mongoengine, pymongo configured)
- Session storage: Cache backend (SESSION_ENGINE = 'django.contrib.sessions.backends.cache')
- Custom session tracking: UserSession model

### Authentication Architecture
- Custom authentication backend: `accounts.backends.AuthUserBackend`
- Raw SQL queries via `accounts/db_utils.py`
- Google OAuth2 integration with custom pipeline: `process_login_gg`
- Custom middleware: `SyncCustomSessionMiddleware`

### Before Production
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS` properly
- Enable full authentication (review permission settings)
- Set up production-grade cache backend (Redis recommended)
- Configure proper CORS settings
- Review and test all security settings
- See [Deployment](#-deployment) section for complete checklist

---

**Made with ❤️ by the ReHearten Team**

*Simplifying bus travel management with modern technology*
