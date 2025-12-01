from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    # Transactions where user is the sender
    sent_transactions = db.relationship('Transaction', 
                                     backref='sender',
                                     foreign_keys='Transaction.sender_id',
                                     lazy=True)
    
    # Transactions where user is the receiver
    received_transactions = db.relationship('Transaction',
                                         backref='receiver',
                                         foreign_keys='Transaction.receiver_id',
                                         lazy=True)
    
    # User's notifications
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign keys for sender and receiver
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Status fields
    status = db.Column(db.String(20), nullable=False, default='pending')  # overall status
    sender_status = db.Column(db.String(20), nullable=False, default='pending')  # status for sender
    receiver_status = db.Column(db.String(20), nullable=False, default='pending')  # status for receiver

    def get_status_color(self):
        status_colors = {
            'pending': 'yellow',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'sent': 'blue',
            'received': 'green'
        }
        return status_colors.get(self.status, 'gray')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # success, error, warning, info
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    is_announced = db.Column(db.Boolean, default=False)  # Track if notification has been announced

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'timestamp': self.timestamp.isoformat(),
            'is_read': self.is_read,
            'is_announced': self.is_announced
        } 