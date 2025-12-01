from flask_sse import sse
from flask import session
from functools import wraps
from datetime import datetime

def send_notification(user_id, title, message, notification_type):
    """Send notification to a specific user"""
    notification = {
        'title': title,
        'message': message,
        'type': notification_type,
        'timestamp': datetime.utcnow().isoformat()
    }
    sse.publish(notification, type='notification', channel=f'user_{user_id}')

def notify_transaction_status(transaction):
    """Send transaction status notifications to both sender and receiver"""
    if transaction.status == 'pending':
        # Notify sender that money is being debited
        send_notification(
            transaction.sender_id,
            'Transaction Initiated',
            f'${transaction.amount:.2f} is being debited from your account.',
            'info'
        )
        # Notify receiver that money is on the way
        send_notification(
            transaction.receiver_id,
            'Incoming Transaction',
            f'${transaction.amount:.2f} is being transferred to your account.',
            'info'
        )
    
    elif transaction.status == 'processing':
        # Notify sender that money has been debited
        send_notification(
            transaction.sender_id,
            'Money Debited',
            f'${transaction.amount:.2f} has been debited from your account and is being processed.',
            'warning'
        )
        # Notify receiver that money is being processed
        send_notification(
            transaction.receiver_id,
            'Transaction Processing',
            f'${transaction.amount:.2f} transfer is being processed.',
            'warning'
        )
    
    elif transaction.status == 'completed':
        # Notify sender of successful transaction
        send_notification(
            transaction.sender_id,
            'Transaction Completed',
            f'${transaction.amount:.2f} has been successfully sent.',
            'success'
        )
        # Notify receiver of received money
        send_notification(
            transaction.receiver_id,
            'Money Received',
            f'${transaction.amount:.2f} has been added to your account.',
            'success'
        )
    
    elif transaction.status == 'failed':
        # Notify sender of failed transaction
        send_notification(
            transaction.sender_id,
            'Transaction Failed',
            f'${transaction.amount:.2f} transaction failed. The amount will be refunded.',
            'error'
        )
        # Notify receiver of failed transaction
        send_notification(
            transaction.receiver_id,
            'Transaction Failed',
            f'${transaction.amount:.2f} incoming transfer has failed.',
            'error'
        ) 