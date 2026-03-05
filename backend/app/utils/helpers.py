from datetime import datetime, timedelta
import os
import uuid
from werkzeug.utils import secure_filename


class Helpers:
    @staticmethod
    def generate_unique_filename(original_filename):
        
        ext = os.path.splitext(original_filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return secure_filename(unique_name)
    
    @staticmethod
    def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
        
        if not dt:
            return None
        
        if isinstance(dt, str):
            return dt
        
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(dt_str):  
        if not dt_str:
            return None
        
        if isinstance(dt_str, datetime):
            return dt_str
        
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None
    
    @staticmethod
    def get_date_range(days=7):
        
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        
        date_list = []
        current = today
        while current <= end_date:
            date_list.append(current)
            current += timedelta(days=1)
        
        return date_list
    
    @staticmethod
    def calculate_age(date_of_birth):
        
        if not date_of_birth:
            return None
        
        today = datetime.now().date()
        
        if isinstance(date_of_birth, str):
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        
        age = today.year - date_of_birth.year
        
        if today.month < date_of_birth.month or \
           (today.month == date_of_birth.month and today.day < date_of_birth.day):
            age -= 1
        
        return age
    
    @staticmethod
    def time_slot_to_datetime(date_str, time_str):
        
        dt_str = f"{date_str} {time_str}"
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
    
    @staticmethod
    def is_weekend(date_obj):
        
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        
        return date_obj.weekday() >= 5
    
    @staticmethod
    def paginate_results(items, page=1, per_page=10):
        
        total = len(items)
        total_pages = (total + per_page - 1) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'items': items[start:end],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    
    @staticmethod
    def sanitize_search_query(query):
        
        if not query:
            return ""
        
        query = query.strip()
        query = query.replace('%', '\\%')
        query = query.replace('_', '\\_')
        
        return query
    
    @staticmethod
    def allowed_file(filename, allowed_extensions={'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}):
        
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def format_currency(amount_cents):
        
        dollars = amount_cents / 100
        return f"${dollars:,.2f}"
    
    @staticmethod
    def success_response(data=None, message=None, status=200):
        
        response = {"success": True}
        
        if message:
            response["message"] = message
        
        if data is not None:
            response["data"] = data
        
        return response, status
    
    @staticmethod
    def error_response(message, status=400):
        
        return {
            "success": False,
            "error": message
        }, status

