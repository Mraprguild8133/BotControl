"""
Database operations and data management
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from .config import DATA_DIR, DATABASE_FILE

logger = logging.getLogger(__name__)

def ensure_data_directory():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_json_file(filename: str, default_data: dict = None) -> dict:
    """Load JSON data from file"""
    ensure_data_directory()
    filepath = os.path.join(DATA_DIR, filename)
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return default_data if default_data is not None else {}
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {filename}: {e}")
        return default_data if default_data is not None else {}

def save_json_file(filename: str, data: dict) -> bool:
    """Save JSON data to file"""
    ensure_data_directory()
    filepath = os.path.join(DATA_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, TypeError) as e:
        logger.error(f"Error saving {filename}: {e}")
        return False

def get_welcome_message() -> dict:
    """Get current welcome message configuration"""
    from .config import DEFAULT_WELCOME_MESSAGE, DEFAULT_BOTTOM_TEXT
    
    default_config = {
        'message': DEFAULT_WELCOME_MESSAGE,
        'bottom_text': DEFAULT_BOTTOM_TEXT,
        'last_updated': datetime.now().isoformat()
    }
    
    return load_json_file('welcome_config.json', default_config)

def set_welcome_message(message: str, bottom_text: str = None) -> bool:
    """Set welcome message configuration"""
    current_config = get_welcome_message()
    
    config = {
        'message': message,
        'bottom_text': bottom_text if bottom_text is not None else current_config.get('bottom_text', ''),
        'last_updated': datetime.now().isoformat()
    }
    
    return save_json_file('welcome_config.json', config)

def get_bot_stats() -> dict:
    """Get bot statistics"""
    stats_file = 'bot_stats.json'
    default_stats = {
        'channels': 0,
        'keywords': 0,
        'users': 0,
        'messages': 0,
        'searches': 0,
        'downloads': 0,
        'uptime': '0 days',
        'memory': '0 MB',
        'last_updated': datetime.now().isoformat()
    }
    
    return load_json_file(stats_file, default_stats)

def update_bot_stats(stat_name: str, increment: int = 1) -> bool:
    """Update bot statistics"""
    stats = get_bot_stats()
    
    if stat_name in stats:
        if isinstance(stats[stat_name], (int, float)):
            stats[stat_name] += increment
        stats['last_updated'] = datetime.now().isoformat()
        return save_json_file('bot_stats.json', stats)
    
    return False

def add_user_activity(user_id: int, activity: str, details: dict = None) -> bool:
    """Log user activity"""
    activity_file = 'user_activity.json'
    activities = load_json_file(activity_file, {'activities': []})
    
    new_activity = {
        'user_id': user_id,
        'activity': activity,
        'timestamp': datetime.now().isoformat(),
        'details': details if details is not None else {}
    }
    
    activities['activities'].append(new_activity)
    
    # Keep only last 1000 activities
    if len(activities['activities']) > 1000:
        activities['activities'] = activities['activities'][-1000:]
    
    return save_json_file(activity_file, activities)

def get_user_stats(user_id: int) -> dict:
    """Get statistics for a specific user"""
    activity_file = 'user_activity.json'
    activities = load_json_file(activity_file, {'activities': []})
    
    user_activities = [a for a in activities['activities'] if a['user_id'] == user_id]
    
    stats = {
        'total_activities': len(user_activities),
        'searches': len([a for a in user_activities if a['activity'] == 'movie_search']),
        'downloads': len([a for a in user_activities if a['activity'] == 'download_request']),
        'commands': len([a for a in user_activities if a['activity'] == 'command_used']),
        'last_activity': user_activities[-1]['timestamp'] if user_activities else 'Never',
        'first_seen': user_activities[0]['timestamp'] if user_activities else 'Never'
    }
    
    return stats

def store_search_result(query: str, results: List[dict], user_id: int) -> bool:
    """Store movie search results for analytics"""
    search_file = 'search_history.json'
    searches = load_json_file(search_file, {'searches': []})
    
    search_entry = {
        'query': query,
        'user_id': user_id,
        'results_count': len(results),
        'timestamp': datetime.now().isoformat(),
        'results': results[:5]  # Store only first 5 results
    }
    
    searches['searches'].append(search_entry)
    
    # Keep only last 500 searches
    if len(searches['searches']) > 500:
        searches['searches'] = searches['searches'][-500:]
    
    return save_json_file(search_file, searches)

def get_popular_searches(limit: int = 10) -> List[dict]:
    """Get most popular search queries"""
    search_file = 'search_history.json'
    searches = load_json_file(search_file, {'searches': []})
    
    # Count search queries
    query_counts = {}
    for search in searches['searches']:
        query = search['query'].lower()
        query_counts[query] = query_counts.get(query, 0) + 1
    
    # Sort by count and return top results
    popular = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {'query': query, 'count': count}
        for query, count in popular[:limit]
    ]

def store_download_request(movie_name: str, user_id: int, success: bool) -> bool:
    """Store download request for analytics"""
    download_file = 'download_history.json'
    downloads = load_json_file(download_file, {'downloads': []})
    
    download_entry = {
        'movie_name': movie_name,
        'user_id': user_id,
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    downloads['downloads'].append(download_entry)
    
    # Keep only last 1000 downloads
    if len(downloads['downloads']) > 1000:
        downloads['downloads'] = downloads['downloads'][-1000:]
    
    return save_json_file(download_file, downloads)

def get_download_stats() -> dict:
    """Get download statistics"""
    download_file = 'download_history.json'
    downloads = load_json_file(download_file, {'downloads': []})
    
    total_downloads = len(downloads['downloads'])
    successful_downloads = len([d for d in downloads['downloads'] if d['success']])
    failed_downloads = total_downloads - successful_downloads
    
    # Most requested movies
    movie_counts = {}
    for download in downloads['downloads']:
        movie = download['movie_name'].lower()
        movie_counts[movie] = movie_counts.get(movie, 0) + 1
    
    popular_movies = sorted(movie_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'total_downloads': total_downloads,
        'successful_downloads': successful_downloads,
        'failed_downloads': failed_downloads,
        'success_rate': (successful_downloads / total_downloads * 100) if total_downloads > 0 else 0,
        'popular_movies': [
            {'movie': movie, 'requests': count}
            for movie, count in popular_movies
        ]
    }

def cleanup_old_data(days: int = 30) -> bool:
    """Clean up old data files"""
    try:
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        # Files to clean up
        files_to_clean = [
            'user_activity.json',
            'search_history.json',
            'download_history.json'
        ]
        
        for filename in files_to_clean:
            filepath = os.path.join(DATA_DIR, filename)
            if os.path.exists(filepath):
                data = load_json_file(filename, {})
                
                if 'activities' in data:
                    # Clean user activities
                    data['activities'] = [
                        a for a in data['activities']
                        if datetime.fromisoformat(a['timestamp']).timestamp() > cutoff_date
                    ]
                
                elif 'searches' in data:
                    # Clean search history
                    data['searches'] = [
                        s for s in data['searches']
                        if datetime.fromisoformat(s['timestamp']).timestamp() > cutoff_date
                    ]
                
                elif 'downloads' in data:
                    # Clean download history
                    data['downloads'] = [
                        d for d in data['downloads']
                        if datetime.fromisoformat(d['timestamp']).timestamp() > cutoff_date
                    ]
                
                save_json_file(filename, data)
        
        logger.info(f"Cleaned up data older than {days} days")
        return True
    
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return False

def backup_data(backup_name: str = None) -> bool:
    """Create backup of all data files"""
    try:
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = os.path.join(DATA_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Copy all JSON files to backup directory
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.json'):
                source = os.path.join(DATA_DIR, filename)
                destination = os.path.join(backup_dir, f"{backup_name}_{filename}")
                
                with open(source, 'r') as src, open(destination, 'w') as dst:
                    dst.write(src.read())
        
        logger.info(f"Data backed up as {backup_name}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

