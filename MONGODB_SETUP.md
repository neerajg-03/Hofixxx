# MongoDB Backend Setup Guide

This guide will help you set up and run the Hoofix application with MongoDB as the backend database.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ (for local development)

## Quick Start with Docker

1. **Clone and navigate to the project directory:**
   ```bash
   cd hoofix
   ```

2. **Start the application with MongoDB:**
   ```bash
   docker-compose up --build
   ```

3. **Run the migration script to seed initial data:**
   ```bash
   docker-compose exec backend python migrate_to_mongodb.py
   ```

4. **Access the application:**
   - Frontend: http://localhost:5000
   - MongoDB: localhost:27017

## Local Development Setup

### Option 1: With Local MongoDB

1. **Install MongoDB locally:**
   - Windows: Download from [MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - macOS: `brew install mongodb-community`
   - Ubuntu: `sudo apt-get install mongodb`

2. **Start MongoDB:**
   ```bash
   # Windows
   net start MongoDB
   
   # macOS/Linux
   mongod
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export MONGODB_URI=mongodb://localhost:27017/hofix
   export JWT_SECRET_KEY=your-secret-key
   export SECRET_KEY=your-secret-key
   ```

5. **Run the migration script:**
   ```bash
   python migrate_to_mongodb.py
   ```

6. **Start the application:**
   ```bash
   python app.py
   ```

### Option 2: With Docker MongoDB Only

1. **Start only MongoDB:**
   ```bash
   docker-compose up mongodb
   ```

2. **Set environment variables:**
   ```bash
   export MONGODB_URI=mongodb://localhost:27017/hofix
   export JWT_SECRET_KEY=your-secret-key
   export SECRET_KEY=your-secret-key
   ```

3. **Install Python dependencies and run:**
   ```bash
   pip install -r requirements.txt
   python migrate_to_mongodb.py
   python app.py
   ```

## Database Schema

### Collections

1. **users** - User accounts (customers, providers, admins)
2. **services** - Available services (electrician, plumber, etc.)
3. **providers** - Service provider profiles
4. **bookings** - Service bookings and appointments
5. **payments** - Payment records

### Key Features

- **User Management**: Support for different user roles (user, provider, admin)
- **Service Catalog**: Manage available services with pricing
- **Booking System**: Create and manage service bookings
- **Payment Processing**: Track payments and transactions
- **Location Services**: Store and query user/provider locations
- **Real-time Updates**: WebSocket support for live updates

## Sample Data

The migration script creates:

- **8 Services**: Electrician, Plumber, Carpenter, Cleaner, Painter, Gardener, Locksmith, HVAC Technician
- **4 Sample Users**:
  - Admin: admin@hofix.com / admin123
  - User: john@example.com / user123
  - Provider: jane@example.com / provider123 (Electrician, Plumber)
  - Provider: mike@example.com / provider123 (Carpenter, Painter)

## API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /login` - User login
- `GET /dashboard/user` - User dashboard
- `GET /dashboard/provider` - Provider dashboard

### Services
- `GET /services` - List all services
- `POST /services` - Create new service (admin only)

### Bookings
- `GET /bookings/user` - Get user bookings
- `GET /bookings/provider` - Get provider bookings
- `POST /bookings/create` - Create new booking
- `POST /bookings/accept` - Accept booking
- `POST /bookings/reject` - Reject booking

### Providers
- `GET /providers/nearby` - Find nearby providers
- `POST /providers/location` - Update provider location

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/hofix` |
| `JWT_SECRET_KEY` | JWT signing key | `dev-jwt-secret` |
| `SECRET_KEY` | Flask secret key | `dev-secret` |
| `PORT` | Application port | `5000` |

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error:**
   - Ensure MongoDB is running
   - Check connection string format
   - Verify network connectivity

2. **Migration Script Fails:**
   - Check MongoDB connection
   - Ensure database permissions
   - Clear existing data if needed

3. **Authentication Issues:**
   - Verify JWT secret key
   - Check token expiration
   - Ensure proper user roles

### Useful Commands

```bash
# Check MongoDB status
docker-compose ps

# View MongoDB logs
docker-compose logs mongodb

# Access MongoDB shell
docker-compose exec mongodb mongosh hofix

# Reset database
docker-compose down -v
docker-compose up --build
```

## Production Deployment

For production deployment:

1. **Use environment-specific configurations**
2. **Set strong secret keys**
3. **Enable MongoDB authentication**
4. **Use MongoDB Atlas or managed MongoDB service**
5. **Set up proper monitoring and backups**

## Support

For issues or questions:
1. Check the logs: `docker-compose logs backend`
2. Verify MongoDB connection
3. Ensure all environment variables are set correctly
4. Check the API documentation and endpoint responses










