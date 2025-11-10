# app/core/tmdb.py

import requests
import logging
from typing import Optional, Dict
import re
from pathlib import Path

class TMDBClient:
    """Client for The Movie Database (TMDB) API."""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _clean_movie_title(self, filename: str) -> str:
        """Extracts clean title from filename."""
        # Remove extension
        title = Path(filename).stem
        
        # Remove year in parentheses or brackets
        title = re.sub(r'[\[\(]\d{4}[\]\)]', '', title)
        
        # Remove common quality and format tags
        title = re.sub(r'\b(1080p|720p|480p|BluRay|BRRip|WEB-DL|HDRip|XviD|x264|x265|HEVC)\b', '', title, flags=re.IGNORECASE)
        
        # Replace dots, underscores and multiple spaces
        title = re.sub(r'[._-]', ' ', title)
        title = re.sub(r'\s+', ' ', title)
        
        return title.strip()
    
    def search_movie(self, filename: str) -> Optional[Dict]:
        """Searches for a movie by filename and returns information."""
        if not self.api_key:
            logging.warning("TMDB API key not configured.")
            return None
        
        # Clean the title
        clean_title = self._clean_movie_title(filename)
        
        try:
            # Search movie
            url = f"{self.BASE_URL}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': clean_title,
                'language': 'en-US',
                'page': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                # Take the first result
                movie = data['results'][0]
                
                # Get complete details
                return self.get_movie_details(movie['id'])
            
            logging.info(f"No information found for: {clean_title}")
            return None
            
        except requests.RequestException as e:
            logging.error(f"Error searching movie in TMDB: {e}")
            return None
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Gets complete movie details."""
        try:
            url = f"{self.BASE_URL}/movie/{movie_id}"
            params = {
                'api_key': self.api_key,
                'language': 'en-US',
                'append_to_response': 'credits'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            movie = response.json()
            
            # Format data
            return {
                'title': movie.get('title', 'Unknown Title'),
                'original_title': movie.get('original_title', ''),
                'overview': movie.get('overview', 'No description available.'),
                'release_date': movie.get('release_date', 'Unknown'),
                'runtime': movie.get('runtime', 0),
                'vote_average': movie.get('vote_average', 0),
                'poster_path': f"{self.IMAGE_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                'backdrop_path': f"{self.IMAGE_BASE_URL}{movie['backdrop_path']}" if movie.get('backdrop_path') else None,
                'genres': [g['name'] for g in movie.get('genres', [])],
                'director': self._get_director(movie.get('credits', {})),
                'cast': self._get_cast(movie.get('credits', {}))
            }
            
        except requests.RequestException as e:
            logging.error(f"Error getting details from TMDB: {e}")
            return None
    
    def _get_director(self, credits: Dict) -> str:
        """Extracts director from credits."""
        crew = credits.get('crew', [])
        for person in crew:
            if person.get('job') == 'Director':
                return person.get('name', 'Unknown')
        return 'Unknown'
    
    def _get_cast(self, credits: Dict) -> list:
        """Extracts main cast members."""
        cast = credits.get('cast', [])
        return [person.get('name') for person in cast[:5]]

# Instancia global (se inicializará con la API key del config)
_tmdb_client: Optional[TMDBClient] = None

def get_tmdb_client() -> Optional[TMDBClient]:
    """Obtiene o crea la instancia del cliente TMDB."""
    global _tmdb_client
    
    if _tmdb_client is None:
        from app.core.config import config
        api_key = config.get('TMDB', 'api_key', fallback='')
        
        if api_key:
            _tmdb_client = TMDBClient(api_key)
        else:
            logging.warning("API key de TMDB no configurada.")
    
    return _tmdb_client
