# ReHearten - Bus Booking Management System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

**ReHearten** is a comprehensive bus booking management system built with Django and PostgreSQL. The system provides a complete solution for managing bus routes, trips, bookings, and payments with an intuitive user interface and robust RESTful API.

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
- **Social Authentication**: Google OAuth2 integration
- **Session Management**: Custom session handling with security features
- **Admin Dashboard**: Comprehensive admin panel for system management
- **Management Commands**: CLI tools for user role management

## 🛠️ Technology Stack

### Backend
- **Python 3.12+**: Core programming language
- **Django 4.2+**: Web framework for rapid development
- **Django REST Framework**: API development
- **PostgreSQL**: Relational database management system
- **Social Auth App Django**: OAuth2 authentication

### Frontend
- **Bootstrap 5.3**: Responsive CSS framework
- **Font Awesome 6**: Icon library
- **Inter Font**: Modern typography
- **Custom CSS/JS**: Tailored styling and interactions

### Development Tools
- **Python-dotenv**: Environment variable management
- **Pillow**: Image processing
- **Cryptography**: Security features
- **uv**: Fast Python package installer (recommended)

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- PostgreSQL 15 or higher
- Google OAuth2 credentials (optional, for social login)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nguyenhieu277/rehearten.git
   cd rehearten
   ```

2. **Install dependencies**
   ```bash
   # Using pip
   pip install -r requirements.txt

   # or using uv (recommended)
   uv sync
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Database Configuration**
   - Install and start PostgreSQL
   - Create database: `createdb bus_booking_management`
   - Update database credentials in `.env`

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open http://localhost:8000
   - Login with your admin credentials

## 📁 Project Structure

```
ReHearten/
├── accounts/                 # User authentication and management
│   ├── models.py            # User and UserSession models
│   ├── views.py             # Authentication views
│   ├── backends.py          # Custom authentication backend
│   ├── urls.py              # Account URLs
│   └── management/          # Django management commands
│       └── commands/
│           ├── change_user_role.py
│           └── list_users.py
├── transport/               # Transportation models
│   ├── models.py            # Locations, Route, Bus, Seat, Trip
│   └── serializers.py       # API serializers
├── bookings/                # Booking management
│   ├── models.py            # Booking and Ticket models
│   ├── views.py             # Booking ViewSets
│   ├── serializers.py       # Booking serializers
│   └── urls.py              # Booking API URLs
├── payments/                # Payment processing
│   └── models.py            # Payment model
├── REHEARTEN/               # Django project settings
│   ├── settings.py          # Main configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS, images)
├── logs/                    # Application logs
├── manage.py                # Django management script
├── pyproject.toml           # Project dependencies
└── CLAUDE.md                # AI assistant guidance
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
4. Create OAuth2 credentials
5. Add authorized redirect URIs: `http://localhost:8000/oauth/complete/google-oauth2/`

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

### Authentication
- `POST /register/` - User registration
- `POST /login/` - User login
- `POST /logout/` - User logout
- `GET /profile/` - User profile
- `POST /change-password/` - Change password

### User Management (Admin)
- `GET /api/users/` - List users
- `POST /api/change-user-role/` - Change user role
- `POST /api/toggle-user-status/` - Toggle user active status

### Bookings API
- `GET /api/bookings/` - List bookings (filtered by user role)
- `POST /api/bookings/` - Create booking with tickets
- `GET /api/bookings/{id}/` - Retrieve booking details
- `PUT /api/bookings/{id}/` - Update booking (only pending)
- `DELETE /api/bookings/{id}/` - Cancel booking
- `POST /api/bookings/{id}/confirm/` - Confirm booking (admin only)
- `POST /api/bookings/{id}/cancel/` - Cancel booking
- `GET /api/bookings/my-bookings/` - Get current user's bookings
- `GET /api/bookings/statistics/` - Get statistics (admin only)
- `GET /api/bookings/{id}/tickets/` - Get all tickets for a booking

### Tickets API
- `GET /api/tickets/` - List tickets (filtered by user)
- `GET /api/tickets/{id}/` - Retrieve ticket details

## 🗃️ Database Schema

### Key Models

**User** → **Booking** → **Payment**
**User** → **UserSession**

**Locations** → **Route** (start/end locations)
**Bus** → **Seat** (one-to-many)
**Route** + **Bus** → **Trip**

**Trip** → **Booking** → **Ticket**
**Seat** → **Ticket**

### Important Constraints
- `Ticket`: Unique constraint on (trip, seat) - prevents double booking
- `Route`: Unique constraint on (start_location, end_location)
- `Seat`: Unique constraint on (bus, seat_number)
- `User`: Unique username and email

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Django's built-in hashers
- **Custom Session Management**: UserSession model for tracking user sessions
- **CSRF Protection**: Cross-site request forgery protection
- **OAuth2 Security**: Secure social authentication with Google
- **Input Validation**: Comprehensive form and API validation
- **SQL Injection Protection**: Django ORM prevents injection attacks
- **Role-based Access Control**: Permission system with admin/user roles

## 🛠️ Management Commands

```bash
# Create superuser
python manage.py createsuperuser

# List all users
python manage.py list_users

# Change user role
python manage.py change_user_role <username> <role>
# Example: python manage.py change_user_role john admin

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

## 🧪 Testing

Currently no test suite is configured. To add tests:

```bash
python manage.py test <app_name>
# Example: python manage.py test accounts
python manage.py test bookings
```

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG=False` in settings
2. Configure production PostgreSQL database
3. Set up static file serving (whitenoise or CDN)
4. Configure HTTPS/SSL
5. Set up monitoring and logging
6. Use environment variables for secrets
7. Enable full authentication (disable test mode)
8. Set up database backups
9. Configure allowed hosts properly

### Static Files
```bash
python manage.py collectstatic
```

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PTIT (Posts and Telecommunications Institute of Technology)** - Academic institution
- **Django Community** - Excellent web framework
- **Django REST Framework** - Powerful API toolkit
- **PostgreSQL** - Robust database system

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/nguyenhieu277/rehearten/issues)
- **Documentation**: See [CLAUDE.md](CLAUDE.md) for detailed technical documentation

## ⚠️ Development Notes

- Authentication is partially disabled for testing purposes in development mode
- Anonymous users can access bookings/tickets APIs in development
- Enable full authentication before production deployment
- See `bookings/views.py` for permission settings

---

**Made with ❤️ by the ReHearten Team**

*Simplifying bus travel management*
