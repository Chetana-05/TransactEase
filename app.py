from flask import Flask, render_template, request, flash, redirect, url_for, Response, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
from extensions import db, login_manager
from models import User, Transaction, Notification
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
import time
from threading import Thread
import random

load_dotenv()

# Add user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_notification(user_id, title, message, notification_type):
    """Store notification in database"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type
    )
    db.session.add(notification)
    db.session.commit()

def process_transaction(transaction_id):
    """
    Process transaction with detailed status notifications
    """
    with app.app_context():
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return

        try:
            # Initial notification
            send_notification(
                transaction.sender_id,
                'Transaction Started',
                f'Processing transfer of ${transaction.amount:.2f} to {transaction.receiver.email}',
                'info'
            )
            send_notification(
                transaction.receiver_id,
                'Incoming Transfer',
                f'${transaction.amount:.2f} transfer initiated from {transaction.sender.email}',
                'info'
            )
            time.sleep(2)  # Initial processing delay

            # Update sender status to 'sent'
            transaction.sender_status = 'sent'
            db.session.commit()
            
            send_notification(
                transaction.sender_id,
                'Money Sent',
                f'${transaction.amount:.2f} has been sent to {transaction.receiver.email}',
                'warning'
            )
            time.sleep(3)

            # Simulate success/failure (80% success rate)
            if random.random() < 0.8:
                # Success Scenario
                transaction.status = 'completed'
                transaction.receiver_status = 'received'
                db.session.commit()

                # Success notifications
                success_message = f'${transaction.amount:.2f} was successfully transferred to {transaction.receiver.email}'
                receive_message = f'${transaction.amount:.2f} has been received from {transaction.sender.email}'
                
                send_notification(
                    transaction.sender_id,
                    'Transaction Successful',
                    success_message,
                    'success'
                )
                send_notification(
                    transaction.receiver_id,
                    'Money Received',
                    receive_message,
                    'success'
                )
            else:
                # Failure Scenario
                transaction.status = 'failed'
                transaction.receiver_status = 'failed'
                db.session.commit()

                # Failure notifications with specific reasons
                failure_reason = random.choice([
                    'Network connectivity issues',
                    'Insufficient funds',
                    'Security verification failed',
                    'System timeout'
                ])

                error_message = f'Transfer of ${transaction.amount:.2f} to {transaction.receiver.email} failed. Reason: {failure_reason}. Your money will be refunded.'
                receiver_message = f'Incoming transfer of ${transaction.amount:.2f} from {transaction.sender.email} failed. Reason: {failure_reason}.'
                
                send_notification(
                    transaction.sender_id,
                    'Transaction Failed',
                    error_message,
                    'error'
                )
                send_notification(
                    transaction.receiver_id,
                    'Transfer Failed',
                    receiver_message,
                    'error'
                )

                # Simulate refund process
                time.sleep(2)
                refund_message = f'${transaction.amount:.2f} has been refunded to your account.'
                send_notification(
                    transaction.sender_id,
                    'Refund Processed',
                    refund_message,
                    'info'
                )

        except Exception as e:
            # Handle unexpected errors
            print(f"Error processing transaction: {e}")
            transaction.status = 'failed'
            transaction.receiver_status = 'failed'
            db.session.commit()
            
            error_message = "An unexpected error occurred. Please try again later."
            sender_error = f'{error_message} Your funds will be refunded.'
            
            send_notification(
                transaction.sender_id,
                'System Error',
                sender_error,
                'error'
            )
            send_notification(
                transaction.receiver_id,
                'System Error',
                error_message,
                'error'
            )

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///transactions.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @app.before_request
    def before_request():
        session.permanent = True  # Set session to permanent
        if current_user.is_authenticated:
            app.permanent_session_lifetime = timedelta(minutes=60)

    @app.route('/get-notifications')
    @login_required
    def get_notifications():
        """Get unannounced notifications for the current user"""
        notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_announced=False
        ).order_by(Notification.timestamp.desc()).all()
        
        return jsonify([notification.to_dict() for notification in notifications])

    @app.route('/mark-notification-announced/<int:notification_id>', methods=['POST'])
    @login_required
    def mark_notification_announced(notification_id):
        """Mark a notification as announced"""
        notification = Notification.query.get_or_404(notification_id)
        if notification.user_id == current_user.id:
            notification.is_announced = True
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False}), 403

    @app.route('/mark-notification-read/<int:notification_id>', methods=['POST'])
    @login_required
    def mark_notification_read(notification_id):
        """Mark a notification as read"""
        notification = Notification.query.get_or_404(notification_id)
        if notification.user_id == current_user.id:
            notification.is_read = True
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False}), 403

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists')
                return redirect(url_for('signup'))
                
            if password != confirm_password:
                flash('Passwords do not match')
                return redirect(url_for('signup'))
                
            new_user = User(
                email=email,
                password=generate_password_hash(password, method='scrypt')  # Updated to use scrypt
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            return redirect(url_for('dashboard'))
            
        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember_me') else False
            
            user = User.query.filter_by(email=email).first()
            
            if not user or not check_password_hash(user.password, password):
                flash('Please check your login details and try again.')
                return redirect(url_for('login'))
                
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))
            
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get all users except current user for the receiver dropdown
        users = User.query.filter(User.id != current_user.id).all()
        
        # Get all transactions where user is either sender or receiver
        transactions = Transaction.query.filter(
            or_(
                Transaction.sender_id == current_user.id,
                Transaction.receiver_id == current_user.id
            )
        ).order_by(Transaction.timestamp.desc()).all()
        
        # Get user's notifications
        notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).order_by(Notification.timestamp.desc()).limit(10).all()
        
        return render_template('dashboard.html', 
                             transactions=transactions, 
                             users=users,
                             notifications=notifications)

    @app.route('/transaction/new', methods=['POST'])
    @login_required
    def create_transaction():
        amount = request.form.get('amount')
        receiver_id = request.form.get('receiver_id')
        
        if not receiver_id:
            flash('Please select a receiver')
            return redirect(url_for('dashboard'))
            
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be positive')
                return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid amount')
            return redirect(url_for('dashboard'))
            
        receiver = User.query.get(receiver_id)
        if not receiver:
            flash('Selected receiver not found')
            return redirect(url_for('dashboard'))
            
        transaction = Transaction(
            amount=amount,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            status='pending',
            sender_status='pending',
            receiver_status='pending'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Start processing in background
        Thread(target=process_transaction, args=(transaction.id,)).start()
        
        flash('Transaction initiated!')
        return redirect(url_for('dashboard'))

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True) 