from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import socketio
from models import User, Provider
from bson import ObjectId
import math

provider_bp = Blueprint('provider', __name__)


@provider_bp.get('/providers/nearby')
@jwt_required(optional=True)
def providers_nearby():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except Exception:
        print("No valid lat/lon provided, using default")
        lat, lon = 28.6139, 77.2090  # Default to Delhi

    # Get optional service filter
    service_type = request.args.get('service_type', '').lower()
    print(f"Searching for providers near {lat}, {lon} with service: {service_type}")
    
    # very simple distance filter using Pythagorean approximation
    users = User.objects(role='provider')
    print(f"Found {users.count()} provider users")
    results = []
    for u in users:
        print(f"Checking provider user: {u.name} (ID: {u.id})")
        # Use default location if provider doesn't have location set
        provider_lat = u.latitude if u.latitude is not None else 28.6139  # Delhi default
        provider_lon = u.longitude if u.longitude is not None else 77.2090  # Delhi default
        dist = math.sqrt((provider_lat - lat) ** 2 + (provider_lon - lon) ** 2) * 111  # rough km
        provider = u.provider_profile
        print(f"  Provider profile: {provider}")
        if not provider:
            print(f"  No provider profile found for {u.name}")
            continue
            
        skills = provider.skills if provider.skills else []
        print(f"  Skills: {skills}")
        
        # Filter by service type if provided
        if service_type:
            print(f"  Filtering by service type: {service_type}")
            # Check if provider has the requested service - improved matching
            service_match = False
            
            # Exact match
            if service_type in [skill.lower() for skill in skills]:
                service_match = True
            
            # Partial match (e.g., "electrician" matches "Electrical")
            if not service_match:
                for skill in skills:
                    if (service_type in skill.lower() or 
                        skill.lower() in service_type or
                        service_type.replace(' ', '') in skill.lower().replace(' ', '') or
                        skill.lower().replace(' ', '') in service_type.replace(' ', '')):
                        service_match = True
                        break
            
            # Category-based matching
            if not service_match and service_type:
                service_categories = {
                    'electrician': ['electrical', 'electric', 'wiring', 'power'],
                    'plumber': ['plumbing', 'water', 'pipe', 'drain'],
                    'carpenter': ['carpentry', 'wood', 'furniture', 'cabinet'],
                    'cleaner': ['cleaning', 'housekeeping', 'maid'],
                    'painter': ['painting', 'paint', 'wall', 'decor'],
                    'ac': ['air conditioning', 'cooling', 'refrigerator', 'hvac']
                }
                
                for category, keywords in service_categories.items():
                    if category in service_type:
                        for keyword in keywords:
                            if any(keyword in skill.lower() for skill in skills):
                                service_match = True
                                break
                        if service_match:
                            break
            
            if not service_match:
                print(f"  Service mismatch for {u.name}")
                continue
            else:
                print(f"  Service match found for {u.name}")
        
        # Calculate hourly rate based on skills and experience
        base_rate = 300  # Base rate in INR
        skill_multiplier = len(skills) * 50
        hourly_rate = base_rate + skill_multiplier
        
        # Get jobs count from bookings
        from models import Booking
        jobs_count = Booking.objects(provider=provider).count()
        
        results.append({
            'id': str(provider.id),
            'name': u.name,
            'skills': skills,
            'rating': u.rating or 5.0,
            'hourly_rate': hourly_rate,
            'price': hourly_rate,  # For backward compatibility
            'lat': provider_lat,
            'lon': provider_lon,
            'jobs_count': jobs_count,
            'distance_km': round(dist, 2),
            'avatar': u.avatar_path,
            'availability': provider.availability
        })
    
    # Sort by distance first, then by rating
    results.sort(key=lambda x: (x['distance_km'], -x['rating']))
    print(f"Returning {len(results)} providers")
    return jsonify(results[:50])


@provider_bp.get('/nearby')
@jwt_required(optional=True)
def nearby_page():
    booking_id = request.args.get('booking_id')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    return render_template('nearby.html', booking_id=booking_id, lat=lat, lon=lon)


@provider_bp.post('/providers/location')
@jwt_required()
def update_provider_location():
    ident = get_jwt_identity()
    user_id = str(ident) if isinstance(ident, str) else str(ident['id'])
    try:
        user = User.objects(id=ObjectId(user_id)).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json() or {}
        user.latitude = data.get('lat')
        user.longitude = data.get('lon')
        # Optional human-readable address
        if 'address' in data:
            user.address = data.get('address')
        user.save()
        # Broadcast provider location update to clients
        try:
            room = f"provider_{user.id}"
            socketio.emit('provider_location', {
                'user_id': str(user.id),
                'name': user.name,
                'lat': user.latitude,
                'lon': user.longitude,
                'address': user.address,
                'rating': user.rating
            })
        except Exception:
            pass
        return jsonify({'message': 'Location updated', 'address': user.address})
    except Exception as e:
        return jsonify({'message': 'Invalid user ID'}), 400


@provider_bp.post('/providers/add-service')
@jwt_required()
def add_provider_service():
    ident = get_jwt_identity()
    user_id = str(ident) if isinstance(ident, str) else str(ident['id'])
    
    try:
        user = User.objects(id=ObjectId(user_id)).first()
        if not user or user.role != 'provider':
            return jsonify({'message': 'Provider not found'}), 404
        
        provider = user.provider_profile
        if not provider:
            return jsonify({'message': 'Provider profile not found'}), 404
        
        data = request.get_json() or {}
        service_name = data.get('service_name')
        
        if not service_name:
            return jsonify({'message': 'Service name is required'}), 400
        
        # Add service to provider's skills if not already present
        if service_name not in provider.skills:
            provider.skills.append(service_name)
            provider.save()
            
            # Broadcast provider update
            try:
                socketio.emit('provider_services_updated', {
                    'provider_id': str(provider.id),
                    'services': provider.skills
                }, to='all_providers')
            except Exception:
                pass
            
            return jsonify({'message': 'Service added successfully', 'services': provider.skills})
        else:
            return jsonify({'message': 'Service already exists'}), 400
            
    except Exception as e:
        return jsonify({'message': 'Invalid request'}), 400


@provider_bp.post('/providers/remove-service')
@jwt_required()
def remove_provider_service():
    ident = get_jwt_identity()
    user_id = str(ident) if isinstance(ident, str) else str(ident['id'])
    
    try:
        user = User.objects(id=ObjectId(user_id)).first()
        if not user or user.role != 'provider':
            return jsonify({'message': 'Provider not found'}), 404
        
        provider = user.provider_profile
        if not provider:
            return jsonify({'message': 'Provider profile not found'}), 404
        
        data = request.get_json() or {}
        service_name = data.get('service_name')
        
        if not service_name:
            return jsonify({'message': 'Service name is required'}), 400
        
        # Remove service from provider's skills
        if service_name in provider.skills:
            provider.skills.remove(service_name)
            provider.save()
            
            # Broadcast provider update
            try:
                socketio.emit('provider_services_updated', {
                    'provider_id': str(provider.id),
                    'services': provider.skills
                }, to='all_providers')
            except Exception:
                pass
            
            return jsonify({'message': 'Service removed successfully', 'services': provider.skills})
        else:
            return jsonify({'message': 'Service not found'}), 400
            
    except Exception as e:
        return jsonify({'message': 'Invalid request'}), 400


@provider_bp.get('/debug/providers')
def debug_providers():
    """Debug endpoint to check provider data and services"""
    try:
        users = User.objects(role='provider')
        providers_data = []
        
        for user in users:
            provider = user.provider_profile
            if provider:
                providers_data.append({
                    'user_id': str(user.id),
                    'user_name': user.name,
                    'provider_id': str(provider.id),
                    'skills': provider.skills,
                    'availability': provider.availability,
                    'location': {
                        'lat': user.latitude,
                        'lon': user.longitude,
                        'address': user.address
                    }
                })
            else:
                providers_data.append({
                    'user_id': str(user.id),
                    'user_name': user.name,
                    'provider_id': None,
                    'skills': [],
                    'availability': False,
                    'location': {
                        'lat': user.latitude,
                        'lon': user.longitude,
                        'address': user.address
                    },
                    'error': 'No provider profile found'
                })
        
        return jsonify({
            'total_providers': len(providers_data),
            'total_users': users.count(),
            'providers': providers_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@provider_bp.get('/debug/bookings')
def debug_bookings():
    """Debug endpoint to check recent bookings"""
    try:
        from models import Booking
        recent_bookings = Booking.objects.order_by('-created_at').limit(10)
        
        bookings_data = []
        for booking in recent_bookings:
            bookings_data.append({
                'id': str(booking.id),
                'user_name': booking.user.name if booking.user else 'Unknown',
                'provider_name': booking.provider.user.name if booking.provider and booking.provider.user else 'Unassigned',
                'service_name': booking.service.name if booking.service else 'Unknown',
                'service_category': booking.service.category if booking.service else 'Unknown',
                'status': booking.status,
                'price': booking.price,
                'created_at': booking.created_at.isoformat() if booking.created_at else None,
                'location': {
                    'lat': booking.location_lat,
                    'lon': booking.location_lon
                }
            })
        
        return jsonify({
            'total_bookings': len(bookings_data),
            'recent_bookings': bookings_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@provider_bp.post('/debug/create-test-providers')
def create_test_providers():
    """Create test providers for debugging"""
    try:
        from models import User, Provider
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        
        # Create test providers
        test_providers = [
            {
                'name': 'Sahil Electric',
                'email': 'sahil@test.com',
                'phone': '9876543210',
                'skills': ['Electrician', 'Electrical'],
                'lat': 28.6139,
                'lon': 77.2090,
                'address': 'Delhi, India'
            },
            {
                'name': 'Rajesh Plumber',
                'email': 'rajesh@test.com', 
                'phone': '9876543211',
                'skills': ['Plumber', 'Plumbing'],
                'lat': 28.6140,
                'lon': 77.2091,
                'address': 'Delhi, India'
            },
            {
                'name': 'Amit Carpenter',
                'email': 'amit@test.com',
                'phone': '9876543212', 
                'skills': ['Carpenter', 'Woodwork'],
                'lat': 28.6141,
                'lon': 77.2092,
                'address': 'Delhi, India'
            }
        ]
        
        created_count = 0
        for provider_data in test_providers:
            # Check if user already exists
            existing_user = User.objects(email=provider_data['email']).first()
            if existing_user:
                print(f"User {provider_data['name']} already exists")
                continue
                
            # Create user
            user = User(
                name=provider_data['name'],
                email=provider_data['email'],
                phone=provider_data['phone'],
                role='provider',
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
                latitude=provider_data['lat'],
                longitude=provider_data['lon'],
                address=provider_data['address']
            )
            user.save()
            
            # Create provider profile
            provider = Provider(
                user=user,
                skills=provider_data['skills'],
                availability=True
            )
            provider.save()
            
            # Update user with provider reference
            user.provider_profile = provider
            user.save()
            
            created_count += 1
            print(f"Created provider: {provider_data['name']}")
        
        return jsonify({
            'message': f'Created {created_count} test providers',
            'total_providers': User.objects(role='provider').count()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@provider_bp.post('/providers/update-tracking-location')
@jwt_required()
def update_provider_tracking_location():
    """Update provider's current location for tracking"""
    ident = get_jwt_identity()
    user_id = str(ident) if isinstance(ident, str) else str(ident.get('id') or ident)
    
    try:
        user = User.objects(id=ObjectId(user_id)).first()
        if not user or user.role != 'provider':
            return jsonify({'message': 'Provider not found'}), 404
        
        data = request.get_json() or {}
        latitude = data.get('lat')
        longitude = data.get('lon')
        
        if latitude is None or longitude is None:
            return jsonify({'message': 'Latitude and longitude are required'}), 400
        
        # Update user location
        user.latitude = float(latitude)
        user.longitude = float(longitude)
        user.save()
        
        # Broadcast location update to clients tracking this provider
        try:
            from datetime import datetime
            socketio.emit('provider_location_update', {
                'provider_id': str(user.id),
                'name': user.name,
                'lat': latitude,
                'lon': longitude,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception:
            pass
        
        return jsonify({
            'message': 'Location updated successfully',
            'lat': latitude,
            'lon': longitude
        })
        
    except Exception as e:
        return jsonify({'message': 'Invalid request'}), 400


@provider_bp.get('/providers/<provider_id>/track')
@jwt_required()
def track_provider(provider_id):
    """Get current location and ETA for a specific provider"""
    try:
        provider_user = User.objects(id=ObjectId(provider_id)).first()
        if not provider_user or provider_user.role != 'provider':
            return jsonify({'message': 'Provider not found'}), 404
        
        # Get current user location (for ETA calculation)
        ident = get_jwt_identity()
        user_id = str(ident) if isinstance(ident, str) else str(ident.get('id') or ident)
        current_user = User.objects(id=ObjectId(user_id)).first()
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Calculate ETA (simple distance-based calculation)
        if (provider_user.latitude and provider_user.longitude and 
            current_user.latitude and current_user.longitude):
            
            # Calculate distance in km
            lat_diff = provider_user.latitude - current_user.latitude
            lon_diff = provider_user.longitude - current_user.longitude
            distance_km = math.sqrt(lat_diff**2 + lon_diff**2) * 111
            
            # Estimate ETA (assuming average speed of 25 km/h in city traffic)
            eta_minutes = max(5, int((distance_km / 25) * 60))
            
            return jsonify({
                'provider_id': str(provider_user.id),
                'provider_name': provider_user.name,
                'location': {
                    'lat': provider_user.latitude,
                    'lon': provider_user.longitude,
                    'address': provider_user.address
                },
                'distance_km': round(distance_km, 2),
                'eta_minutes': eta_minutes,
                'status': 'On the way',
                'last_updated': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({'message': 'Location data not available'}), 400
            
    except Exception as e:
        return jsonify({'message': 'Invalid provider ID'}), 400

