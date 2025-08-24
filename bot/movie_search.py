"""
Movie search functionality
"""

import asyncio
import logging
from typing import List, Dict, Optional

from .config import MOVIE_SEARCH_CHANNEL, MOVIE_DOWNLOAD_CHANNEL

logger = logging.getLogger(__name__)

# Mock movie database - In production, this would connect to actual movie APIs
MOCK_MOVIE_DATABASE = [
    {
        'title': 'Avengers: Endgame',
        'year': '2019',
        'quality': 'HD',
        'genre': 'Action',
        'download_link': 'https://example.com/avengers-endgame'
    },
    {
        'title': 'Spider-Man: No Way Home',
        'year': '2021',
        'quality': 'HD',
        'genre': 'Action',
        'download_link': 'https://example.com/spiderman-nwh'
    },
    {
        'title': 'The Batman',
        'year': '2022',
        'quality': 'HD',
        'genre': 'Action',
        'download_link': 'https://example.com/the-batman'
    },
    {
        'title': 'Top Gun: Maverick',
        'year': '2022',
        'quality': 'HD',
        'genre': 'Action',
        'download_link': 'https://example.com/top-gun-maverick'
    },
    {
        'title': 'Dune',
        'year': '2021',
        'quality': 'HD',
        'genre': 'Sci-Fi',
        'download_link': 'https://example.com/dune-2021'
    }
]

async def search_movie(movie_name: str) -> List[Dict]:
    """
    Search for movies by name
    In production, this would connect to movie databases or APIs
    """
    try:
        await asyncio.sleep(1)  # Simulate API delay
        
        # Simple search in mock database
        movie_name_lower = movie_name.lower()
        results = []
        
        for movie in MOCK_MOVIE_DATABASE:
            if movie_name_lower in movie['title'].lower():
                results.append(movie)
        
        # If no exact matches, try partial matches
        if not results:
            for movie in MOCK_MOVIE_DATABASE:
                title_words = movie['title'].lower().split()
                search_words = movie_name_lower.split()
                
                if any(search_word in ' '.join(title_words) for search_word in search_words):
                    results.append(movie)
        
        logger.info(f"Movie search for '{movie_name}' returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error in movie search: {e}")
        return []

async def get_download_link(movie_name: str) -> Optional[str]:
    """
    Get download link for a specific movie
    In production, this would check availability and generate secure links
    """
    try:
        await asyncio.sleep(1)  # Simulate processing delay
        
        # Search for the movie first
        results = await search_movie(movie_name)
        
        if results:
            # Return the first match's download link
            movie = results[0]
            logger.info(f"Download link found for '{movie_name}': {movie['title']}")
            return movie.get('download_link')
        
        logger.info(f"No download link found for '{movie_name}'")
        return None
        
    except Exception as e:
        logger.error(f"Error getting download link: {e}")
        return None

async def get_movie_details(movie_name: str) -> Optional[Dict]:
    """Get detailed information about a movie"""
    try:
        results = await search_movie(movie_name)
        
        if results:
            movie = results[0]
            
            # In production, this would fetch additional details from movie APIs
            details = {
                'title': movie['title'],
                'year': movie['year'],
                'quality': movie['quality'],
                'genre': movie['genre'],
                'rating': 'Not available',
                'duration': 'Not available',
                'director': 'Not available',
                'cast': 'Not available',
                'plot': 'Not available',
                'download_available': bool(movie.get('download_link')),
                'request_channel': MOVIE_SEARCH_CHANNEL,
                'download_channel': MOVIE_DOWNLOAD_CHANNEL
            }
            
            return details
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting movie details: {e}")
        return None

async def search_by_genre(genre: str) -> List[Dict]:
    """Search movies by genre"""
    try:
        await asyncio.sleep(1)
        
        genre_lower = genre.lower()
        results = []
        
        for movie in MOCK_MOVIE_DATABASE:
            if genre_lower in movie.get('genre', '').lower():
                results.append(movie)
        
        logger.info(f"Genre search for '{genre}' returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error in genre search: {e}")
        return []

async def search_by_year(year: str) -> List[Dict]:
    """Search movies by year"""
    try:
        await asyncio.sleep(1)
        
        results = []
        
        for movie in MOCK_MOVIE_DATABASE:
            if year in movie.get('year', ''):
                results.append(movie)
        
        logger.info(f"Year search for '{year}' returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error in year search: {e}")
        return []

def get_popular_movies() -> List[Dict]:
    """Get list of popular movies"""
    try:
        # In production, this would fetch from trending/popular APIs
        popular = MOCK_MOVIE_DATABASE[:3]  # Return first 3 as "popular"
        
        logger.info(f"Retrieved {len(popular)} popular movies")
        return popular
        
    except Exception as e:
        logger.error(f"Error getting popular movies: {e}")
        return []

def get_movie_categories() -> Dict[str, List[str]]:
    """Get available movie categories"""
    try:
        categories = {
            'genres': list(set(movie.get('genre', 'Unknown') for movie in MOCK_MOVIE_DATABASE)),
            'years': list(set(movie.get('year', 'Unknown') for movie in MOCK_MOVIE_DATABASE)),
            'qualities': list(set(movie.get('quality', 'Unknown') for movie in MOCK_MOVIE_DATABASE))
        }
        
        # Sort categories
        for category in categories:
            categories[category] = sorted(categories[category])
        
        return categories
        
    except Exception as e:
        logger.error(f"Error getting movie categories: {e}")
        return {'genres': [], 'years': [], 'qualities': []}
