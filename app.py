import os
from datetime import timedelta
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from flask_socketio import join_room
from extensions import jwt, bcrypt, socketio, init_mongodb
from models import User, Service


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

    # Init extensions
    CORS(app)
    init_mongodb()  # Initialize MongoDB connection
    jwt.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, async_mode='threading', cors_allowed_origins="*")

    # Register blueprints
    from routes.auth import auth_bp
    from routes.booking import booking_bp
    from routes.provider import provider_bp
    from routes.service import service_bp
    from routes.completion import completion_bp

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(booking_bp, url_prefix='/')
    app.register_blueprint(provider_bp, url_prefix='/')
    app.register_blueprint(service_bp, url_prefix='/')
    app.register_blueprint(completion_bp, url_prefix='/')

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/services')
    def services_page():
        return render_template('services_catalog.html')

    @app.route('/booking-map')
    def booking_map_page():
        return render_template('booking_map.html')

    @app.route('/track-provider')
    def track_provider_page():
        return render_template('track_provider.html')

    @app.route('/dashboard')
    def dashboard_redirect():
        return redirect(url_for('auth.login_page'))

    # Socket events
    @socketio.on('connect')
    def on_connect():
        print('Client connected')
    
    @socketio.on('disconnect')
    def on_disconnect():
        print('Client disconnected')
    
    @socketio.on('join')
    def on_join(data):
        try:
            room = data.get('room')
            if room:
                join_room(room)
                print(f'Client joined room: {room}')
        except Exception as e:
            print(f'Error in join event: {e}')
    
    @socketio.on('join_provider_room')
    def on_join_provider_room(data):
        try:
            provider_id = data.get('provider_id')
            if provider_id:
                join_room(f"provider_{provider_id}")
                join_room('all_providers')
                print(f'Provider {provider_id} joined rooms')
        except Exception as e:
            print(f'Error in join_provider_room event: {e}')
    
    @socketio.on('join_booking_room')
    def on_join_booking_room(data):
        try:
            booking_id = data.get('booking_id')
            if booking_id:
                join_room(f"booking_{booking_id}")
                print(f'Client joined booking room: {booking_id}')
        except Exception as e:
            print(f'Error in join_booking_room event: {e}')

    # Seed minimal services if empty
    with app.app_context():
        try:
            if Service.objects.count() == 0:
                services = [
                    Service(name='Electrician', category='Electrical', base_price=20.0),
                    Service(name='Plumber', category='Plumbing', base_price=18.0),
                    Service(name='Carpenter', category='Woodwork', base_price=22.0),
                    Service(name='Cleaner', category='Cleaning', base_price=15.0),
                ]
                for service in services:
                    service.save()
        except Exception as e:
            print(f"Error seeding services: {e}")

    return app


app = create_app()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
