# FindUs - Handyman Services Platform
### [🔗 View Live Demo](https://fidamano.cfd/)

A comprehensive handyman services marketplace built with Django, connecting customers with skilled craftsmen across various trades and services.

##  Features

### Core Functionality
- **Multi-category Service Platform**: 30+ service categories including plumbing, electrical, carpentry, and more
- **User Profiles**: Separate profiles for customers and craftsmen with detailed information
- **Service Management**: Complete service listing, booking, and management system
- **Regional Coverage**: Support for multiple regions with location-based filtering
- **File Uploads**: Cloudinary integration for image and document storage
- **Email Notifications**: Comprehensive email system for user communications
- **Search & Filtering**: Advanced search capabilities for finding services

### Technical Features
- **Cloud Storage**: Cloudinary integration for media files
- **Caching**: Redis integration for performance optimization
- **Database**: PostgreSQL support with SQLite for development
- **Internationalization**: Multi-language support with Django's i18n
- **Admin Panel**: Comprehensive Django admin interface
- **Static File Management**: Optimized static file serving

## Tech Stack

- **Backend**: Django 4.2.28
- **Database**: PostgreSQL (production), SQLite (development)
- **Caching**: Redis 7.0.1
- **File Storage**: Cloudinary
- **Static Files**: Whitenoise
- **Web Server**: Gunicorn
- **Development Tools**: Django Debug Toolbar, Black, isort

## Project Structure

```
handyman_2/
├── handyman_project/          
│   ├── settings.py           
│   ├── urls.py              
│   └── wsgi.py              
├── findus/                   
│   ├── models.py            
│   ├── views/               
│   ├── forms.py             
│   ├── services.py          
│   ├── email_utils.py       
│   ├── templates/           
│   └── migrations/          
├── populate.py              
├── media/                   
├── static/                  
└── requirements.txt         
```

## Quick Start

### Prerequisites
- Python 3.8+
- Redis server
- PostgreSQL (for production)
- Cloudinary account (for file storage)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd handyman_2/handyman_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with:
   ```bash
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3  # For development
   REDIS_URL=redis://localhost:6379/0
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Populate test data (optional)**
   ```bash
   python populate.py
   ```

9. **Start the development server**
   ```bash
   python manage.py runserver
   ```

10. **Start Redis server** (in separate terminal)
    ```bash
    redis-server
    ```

## Database Models

### Core Models
- **User**: Extended Django user with profile information
- **UserProfile**: Common user profile fields
- **CraftsmanProfile**: Professional craftsman profile with skills and verification
- **CustomerProfile**: Customer-specific profile information
- **Service**: Service listings with categories, pricing, and availability

### Service Categories
The platform supports 30+ service categories including:
- Plumbing, Electrical, AC Technician
- Carpentry, Tiling, Painting
- Furniture Making, Fumigation
- DSTV Technician, Gas Appliance
- POP Worker, Cleaning Services
- And many more specialized trades

### Regional Coverage
Support for multiple regions with location-based filtering and search capabilities.

## Configuration

### Environment Variables
```bash
# Core Django settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3  # Development
# DATABASE_URL=postgresql://user:pass@localhost/dbname  # Production

# Redis
REDIS_URL=redis://localhost:6379/0

# Cloudinary (File Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Email Settings (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Key Features

### User Management
- **Customer Accounts**: Service seekers can browse, search, and book services
- **Craftsman Accounts**: Service providers can list services, manage bookings, and build reputation
- **Profile Verification**: Document upload and verification system for craftsmen

### Service Management
- **Service Listings**: Detailed service descriptions with images and pricing
- **Category Organization**: Services organized by trade categories
- **Location-based Search**: Find services by region and area
- **Booking System**: Complete service booking workflow

### Communication
- **Email Notifications**: Automated emails for bookings, updates, and alerts
- **Messaging System**: In-app communication between customers and craftsmen
- **Review System**: Rating and feedback mechanism

## Testing

```bash
# Run tests
python manage.py test

# Run specific app tests
python manage.py test findus
```

## Development Tools

### Code Quality
- **Black**: Code formatting
- **isort**: Import sorting
- **Django Debug Toolbar**: Development debugging

### Data Management
- **populate.py**: Test data population script
- **Admin Interface**: Comprehensive admin panel for data management

## Deployment

### Build Script
```bash
chmod +x build.sh
./build.sh
```

### Production Considerations
- Use PostgreSQL for production database
- Configure Redis for caching and sessions
- Set up Cloudinary for file storage
- Configure proper static file serving
- Set up SSL certificates
- Configure email services
- Set up monitoring and logging

## License

This project is proprietary and intended for commercial use.

## Contributing

Contact my team for contribution guidelines.

## Support

For technical support or questions, please contact the development team.

---

**Note**: This is a handyman services platform in active development. Features and configurations may evolve as the platform grows.
