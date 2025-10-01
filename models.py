from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields
from mongoengine import connect, disconnect_all
import os


class User(Document):
    name = fields.StringField(max_length=120, required=True)
    email = fields.EmailField(required=True, unique=True)
    phone = fields.StringField(max_length=30)
    role = fields.StringField(max_length=20, required=True, choices=['user', 'provider', 'admin'])
    password_hash = fields.StringField(max_length=255, required=True)
    # Optional geolocation and human-readable address
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    address = fields.StringField(max_length=255)
    avatar_path = fields.StringField(max_length=255)
    credits = fields.FloatField(default=0.0)
    rating = fields.FloatField(default=5.0)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    # Reference to provider profile
    provider_profile = fields.ReferenceField('Provider')
    
    meta = {
        'collection': 'users',
        'indexes': ['email', 'role']
    }


class Service(Document):
    name = fields.StringField(max_length=100, required=True)
    category = fields.StringField(max_length=100, required=True)
    base_price = fields.FloatField(required=True)
    image_path = fields.StringField(max_length=255)
    location_lat = fields.FloatField()
    location_lon = fields.FloatField()
    
    meta = {
        'collection': 'services',
        'indexes': ['category', 'name']
    }


class Provider(Document):
    user = fields.ReferenceField('User', required=True, unique=True)
    skills = fields.ListField(fields.StringField())  # List of skills instead of comma-separated
    availability = fields.BooleanField(default=True)
    
    meta = {
        'collection': 'providers',
        'indexes': ['user', 'availability']
    }


class Booking(Document):
    user = fields.ReferenceField('User', required=True)
    provider = fields.ReferenceField('Provider')
    service = fields.ReferenceField('Service', required=True)
    status = fields.StringField(max_length=50, default='Pending', 
                               choices=['Pending', 'Accepted', 'Rejected', 'In Progress', 'Completed', 'Cancelled'])
    scheduled_time = fields.DateTimeField()
    price = fields.FloatField(default=0.0)
    location_lat = fields.FloatField()
    location_lon = fields.FloatField()
    notes = fields.StringField()
    rating = fields.FloatField()  # Optional user rating for the completed booking
    review = fields.StringField()  # Optional user review text
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    # Service completion details
    completion_notes = fields.StringField()  # Provider's completion notes
    completion_images = fields.ListField(fields.StringField())  # URLs of completion images
    completed_at = fields.DateTimeField()  # When service was completed
    
    # Reference to payment
    payment = fields.ReferenceField('Payment')
    
    meta = {
        'collection': 'bookings',
        'indexes': ['user', 'provider', 'service', 'status', 'created_at']
    }


class Payment(Document):
    booking = fields.ReferenceField('Booking', required=True, unique=True)
    amount = fields.FloatField(required=True)
    method = fields.StringField(max_length=30, required=True, 
                               choices=['Cash', 'Card', 'UPI', 'Bank Transfer', 'Razorpay'])
    status = fields.StringField(max_length=30, default='Pending',
                               choices=['Success', 'Failed', 'Pending', 'Refunded'])
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    # Razorpay specific fields
    razorpay_payment_id = fields.StringField()
    razorpay_order_id = fields.StringField()
    razorpay_signature = fields.StringField()
    
    meta = {
        'collection': 'payments',
        'indexes': ['booking', 'status']
    }


class ServiceCompletion(Document):
    """Model for tracking service completion uploads"""
    booking = fields.ReferenceField('Booking', required=True, unique=True)
    provider = fields.ReferenceField('Provider', required=True)
    completion_notes = fields.StringField()
    images = fields.ListField(fields.StringField())  # URLs of uploaded images
    completed_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'service_completions',
        'indexes': ['booking', 'provider', 'completed_at']
    }


def connect_to_mongodb():
    """Initialize MongoDB connection"""
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/hofix')
    connect(host=mongodb_uri)


def disconnect_from_mongodb():
    """Disconnect from MongoDB"""
    disconnect_all()
