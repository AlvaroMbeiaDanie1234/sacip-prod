import time
import random
import requests
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
try:
    import snscrape.modules.twitter as sntwitter
    import snscrape.modules.instagram as sninstagram
    import snscrape.modules.facebook as snfacebook
    import snscrape.modules.reddit as snreddit
    SNSCRAPE_AVAILABLE = True
except ImportError:
    SNSCRAPE_AVAILABLE = False
    sntwitter = None
    sninstagram = None
    snfacebook = None
    snreddit = None

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import undetected_chromedriver as uc

from django.conf import settings
from .models import PerfilRedeSocial, Postagem


class ProxyRotator:
    """Class to handle proxy rotation for ethical scraping"""
    
    def __init__(self):
        self.proxies = self._load_proxies()
        self.current_proxy_index = 0
        self.failed_proxies = set()  # Track failed proxies
    
    def _load_proxies(self) -> List[str]:
        """Load proxy list from settings or external source"""
        # This could be loaded from settings or an external proxy service
        # For now, we'll return an empty list and let individual requests decide
        return getattr(settings, 'SCRAPING_PROXIES', [])
    
    def _is_proxy_working(self, proxy: str) -> bool:
        """Test if a proxy is working"""
        try:
            test_url = 'http://httpbin.org/ip'  # A simple test endpoint
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get(test_url, proxies=proxies, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_next_working_proxy(self) -> Optional[Dict[str, str]]:
        """Get next working proxy in rotation"""
        if not self.proxies:
            return None
        
        # Try to find a working proxy
        for _ in range(len(self.proxies)):
            proxy = self.proxies[self.current_proxy_index % len(self.proxies)]
            self.current_proxy_index += 1
            
            # Skip if we've already determined this proxy doesn't work
            if proxy in self.failed_proxies:
                continue
            
            # Test if proxy is working
            if self._is_proxy_working(proxy):
                # Format for requests library
                return {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
            else:
                # Mark as failed to avoid trying again
                self.failed_proxies.add(proxy)
        
        # If no working proxies found, return None
        return None
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy in rotation (with working status check)"""
        return self.get_next_working_proxy()


class EthicalScraper:
    """Main class for ethical social media scraping"""
    
    def __init__(self):
        self.proxy_rotator = ProxyRotator()
        self.ua = UserAgent()
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Initialize Selenium webdriver with proxy support
        self.webdriver = None
        
    def _setup_selenium_driver(self, proxy: Optional[Dict[str, str]] = None):
        """Setup Selenium WebDriver with proxy support"""
        chrome_options = Options()
        
        # Add various options to avoid detection
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add proxy if provided
        if proxy:
            proxy_server = proxy.get('http', '').replace('http://', '')
            if proxy_server:
                chrome_options.add_argument(f'--proxy-server=http://{proxy_server}')
        
        # Set a realistic user agent
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        
        # Create undetected Chrome driver
        try:
            self.webdriver = uc.Chrome(options=chrome_options)
            # Execute script to remove webdriver property
            self.webdriver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"Error setting up Chrome driver: {str(e)}")
            # Fallback to regular Chrome if undetected_chromedriver fails
            self.webdriver = webdriver.Chrome(options=chrome_options)
            self.webdriver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _teardown_selenium_driver(self):
        """Close and cleanup Selenium WebDriver"""
        if self.webdriver:
            self.webdriver.quit()
            self.webdriver = None
    
    def scrape_with_selenium(self, url: str, wait_selector: Optional[str] = None, use_proxy: bool = True) -> Optional[str]:
        """Scrape content using Selenium with proxy support"""
        # Add random delay to be respectful
        time.sleep(random.uniform(2, 5))
        
        # Get proxy if needed
        proxy = self.proxy_rotator.get_next_proxy() if use_proxy else None
        
        try:
            # Setup driver with proxy
            self._setup_selenium_driver(proxy)
            
            # Navigate to URL
            self.webdriver.get(url)
            
            # Wait for specific element if selector provided
            if wait_selector:
                wait = WebDriverWait(self.webdriver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
            else:
                # Wait a bit for page to load
                time.sleep(3)
            
            # Get page source
            page_source = self.webdriver.page_source
            
            return page_source
        except Exception as e:
            print(f"Error scraping with Selenium {url}: {str(e)}")
            return None
        finally:
            # Cleanup
            self._teardown_selenium_driver()
    
    def _make_request(self, url: str, use_proxy: bool = True) -> Optional[requests.Response]:
        """Make a request with optional proxy rotation and rate limiting"""
        # Add respectful delay to implement rate limiting
        self._respectful_delay(url)
        
        # Get proxy if needed
        proxies = self.proxy_rotator.get_next_proxy() if use_proxy else None
        
        try:
            response = self.session.get(
                url,
                proxies=proxies,
                timeout=30,
                headers={'User-Agent': self.ua.random}  # Refresh user agent
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Error making request to {url}: {str(e)}")
            return None
    
    def _respectful_delay(self, url: str):
        """Implement rate limiting based on domain to be respectful to servers"""
        domain = urlparse(url).netloc
        
        # Get last access time for this domain
        last_access = getattr(self, '_last_access_times', {})
        current_time = time.time()
        
        # Set default if not initialized
        if not hasattr(self, '_last_access_times'):
            self._last_access_times = {}
        
        # Check if we accessed this domain recently
        if domain in self._last_access_times:
            time_since_last = current_time - self._last_access_times[domain]
            
            # Minimum delay of 1-3 seconds between requests to same domain
            min_delay = random.uniform(1, 3)
            if time_since_last < min_delay:
                time.sleep(min_delay - time_since_last)
        
        # Update last access time
        self._last_access_times[domain] = time.time()
    
    def scrape_with_selenium(self, url: str, wait_selector: Optional[str] = None, use_proxy: bool = True) -> Optional[str]:
        """Scrape content using Selenium with proxy support and rate limiting"""
        # Add respectful delay to be respectful
        self._respectful_delay(url)
        
        # Get proxy if needed
        proxy = self.proxy_rotator.get_next_proxy() if use_proxy else None
        
        try:
            # Setup driver with proxy
            self._setup_selenium_driver(proxy)
            
            # Navigate to URL
            self.webdriver.get(url)
            
            # Wait for specific element if selector provided
            if wait_selector:
                wait = WebDriverWait(self.webdriver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
            else:
                # Wait a bit for page to load
                time.sleep(3)
            
            # Get page source
            page_source = self.webdriver.page_source
            
            return page_source
        except Exception as e:
            print(f"Error scraping with Selenium {url}: {str(e)}")
            return None
        finally:
            # Cleanup
            self._teardown_selenium_driver()
    
    def scrape_twitter_profile(self, username: str) -> Optional[Dict]:
        """Scrape public Twitter/X profile information using snscrape"""
        if not SNSCRAPE_AVAILABLE:
            print("snscrape not available, cannot scrape Twitter profile")
            return None
        
        try:
            # Use snscrape to get user information
            user = None
            for i, user in enumerate(sntwitter.TwitterUserScraper(username).get_items()):
                if i == 0:  # First item contains user info
                    break
            
            if user:
                return {
                    'nome_usuario': user.username,
                    'nome_completo': user.rawContent[:200] if user.rawContent else '',
                    'biografia': user.user.description if hasattr(user, 'user') and user.user else '',
                    'url_perfil': f'https://twitter.com/{username}',
                    'plataforma': 'twitter'
                }
        except Exception as e:
            print(f"Error scraping Twitter profile {username}: {str(e)}")
        
        return None
    
    def scrape_twitter_posts(self, username: str, limit: int = 10) -> List[Dict]:
        """Scrape public Twitter/X posts using snscrape"""
        if not SNSCRAPE_AVAILABLE:
            print("snscrape not available, cannot scrape Twitter posts")
            return []
        
        posts = []
        try:
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'from:{username}').get_items()):
                if i >= limit:
                    break
                
                posts.append({
                    'post_id': str(tweet.id),
                    'conteudo': tweet.rawContent,
                    'data_postagem': tweet.date,
                    'curtidas': tweet.likeCount or 0,
                    'comentarios': tweet.replyCount or 0,
                    'compartilhamentos': tweet.retweetCount or 0,
                    'url_postagem': tweet.url,
                    'marcadores': ' '.join([tag for tag in tweet.hashtags]) if tweet.hashtags else '',
                })
        except Exception as e:
            print(f"Error scraping Twitter posts for {username}: {str(e)}")
        
        return posts
    
    def scrape_instagram_profile(self, username: str) -> Optional[Dict]:
        """Scrape public Instagram profile information"""
        # Note: Instagram scraping is more restricted, using snscrape
        if not SNSCRAPE_AVAILABLE:
            print("snscrape not available, cannot scrape Instagram profile")
            return None
        
        try:
            profile = sninstagram.InstagramUserScraper(username).get_items()
            for item in profile:
                # Get profile info from first item
                return {
                    'nome_usuario': item.username if hasattr(item, 'username') else username,
                    'nome_completo': getattr(item, 'fullName', '')[:200],
                    'biografia': getattr(item, 'biography', ''),
                    'url_perfil': f'https://instagram.com/{username}',
                    'plataforma': 'instagram'
                }
        except Exception as e:
            print(f"Error scraping Instagram profile {username}: {str(e)}")
        
        return None
    
    def scrape_instagram_posts(self, username: str, limit: int = 10) -> List[Dict]:
        """Scrape public Instagram posts"""
        posts = []
        try:
            # Using the correct snscrape approach for Instagram user posts
            for i, post in enumerate(sninstagram.InstagramUserScraper(username).get_items()):
                if i >= limit:
                    break
                
                posts.append({
                    'post_id': str(post.id) if hasattr(post, 'id') else str(i),
                    'conteudo': getattr(post, 'caption', ''),
                    'data_postagem': getattr(post, 'date', datetime.now()),
                    'curtidas': getattr(post, 'likes', 0),
                    'comentarios': getattr(post, 'comments', 0),
                    'compartilhamentos': getattr(post, 'video_view_count', 0) if hasattr(post, 'video_view_count') else 0,
                    'url_postagem': getattr(post, 'url', ''),
                    'marcadores': '',
                })
        except Exception as e:
            print(f"Error scraping Instagram posts for {username}: {str(e)}")
        
        return posts
    
    def scrape_facebook_public_posts(self, page_name: str, limit: int = 10) -> List[Dict]:
        """Scrape public Facebook posts (requires careful implementation)"""
        if not SNSCRAPE_AVAILABLE:
            print("snscrape not available, cannot scrape Facebook posts")
            return []
            
        posts = []
        # Facebook is very restrictive, using snscrape as an alternative
        # This is a placeholder for more complex implementation
        try:
            for i, post in enumerate(snfacebook.FacebookPageScraper(page_name).get_items()):
                if i >= limit:
                    break
                    
                posts.append({
                    'post_id': str(post.id) if hasattr(post, 'id') else str(i),
                    'conteudo': getattr(post, 'text', ''),
                    'data_postagem': getattr(post, 'datetime', datetime.now()),
                    'curtidas': getattr(post, 'likes', 0),
                    'comentarios': getattr(post, 'comments', 0),
                    'compartilhamentos': getattr(post, 'shares', 0),
                    'url_postagem': getattr(post, 'url', ''),
                    'marcadores': '',
                })
        except Exception as e:
            print(f"Error scraping Facebook posts for {page_name}: {str(e)}")
            
        return posts
    
    def scrape_reddit_profile(self, username: str) -> Optional[Dict]:
        """Scrape Reddit user profile"""
        try:
            # Get user info from Reddit API
            response = self._make_request(f'https://www.reddit.com/user/{username}/about.json')
            if response:
                data = response.json()
                user_data = data['data']
                return {
                    'nome_usuario': user_data.get('name', username),
                    'nome_completo': f"u/{user_data.get('name', username)}",
                    'biografia': user_data.get('subreddit', {}).get('public_description', ''),
                    'url_perfil': f'https://reddit.com/user/{username}',
                    'plataforma': 'reddit'
                }
        except Exception as e:
            print(f"Error scraping Reddit profile {username}: {str(e)}")
        
        return None
    
    def scrape_reddit_posts(self, username: str, limit: int = 10) -> List[Dict]:
        """Scrape Reddit posts by user"""
        posts = []
        try:
            response = self._make_request(f'https://www.reddit.com/user/{username}/submitted.json')
            if response:
                data = response.json()
                for i, item in enumerate(data['data']['children'][:limit]):
                    post_data = item['data']
                    posts.append({
                        'post_id': post_data.get('id', str(i)),
                        'conteudo': post_data.get('title', '') + ' ' + post_data.get('selftext', ''),
                        'data_postagem': datetime.fromtimestamp(post_data.get('created_utc', time.time())),
                        'curtidas': post_data.get('score', 0),
                        'comentarios': post_data.get('num_comments', 0),
                        'compartilhamentos': 0,  # Reddit doesn't have shares in the traditional sense
                        'url_postagem': f"https://reddit.com{post_data.get('permalink', '')}",
                        'marcadores': '',
                    })
        except Exception as e:
            print(f"Error scraping Reddit posts for {username}: {str(e)}")
        
        return posts
    
    def scrape_generic_social_content(self, url: str) -> List[Dict]:
        """Scrape generic social media content from a URL"""
        posts = []
        
        # Try regular requests first
        response = self._make_request(url)
        soup = None
        
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
        else:
            # If regular requests fail, try with Selenium
            page_source = self.scrape_with_selenium(url)
            if page_source:
                soup = BeautifulSoup(page_source, 'html.parser')
        
        if soup:
            # This is a basic implementation - in practice, you'd need platform-specific selectors
            # Look for common social media post patterns
            post_elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['post', 'tweet', 'status', 'entry', 'feed', 'timeline']))
            
            for i, element in enumerate(post_elements):
                posts.append({
                    'post_id': f'generic_{i}',
                    'conteudo': element.get_text()[:500],  # Limit content
                    'data_postagem': datetime.now(),
                    'curtidas': 0,  # Not available in generic scraping
                    'comentarios': 0,
                    'compartilhamentos': 0,
                    'url_postagem': url,
                    'marcadores': '',
                })
        
        return posts


class SocialMediaScraperService:
    """Service class to manage social media scraping operations"""
    
    def __init__(self):
        self.scraper = EthicalScraper()
    
    def sync_profile_data(self, perfil_id: int) -> bool:
        """Sync profile data from social media platform"""
        try:
            perfil = PerfilRedeSocial.objects.get(id=perfil_id)
            
            if perfil.plataforma == 'twitter':
                profile_data = self.scraper.scrape_twitter_profile(perfil.nome_usuario)
            elif perfil.plataforma == 'instagram':
                profile_data = self.scraper.scrape_instagram_profile(perfil.nome_usuario)
            elif perfil.plataforma == 'facebook':
                # For Facebook, we could use the generic scraping approach
                profile_data = None  # Facebook profile scraping is complex, so we'll skip it for now
            elif perfil.plataforma == 'reddit':
                profile_data = self.scraper.scrape_reddit_profile(perfil.nome_usuario)
            else:
                # For other platforms, we might need different approaches
                profile_data = None
            
            if profile_data:
                perfil.nome_completo = profile_data.get('nome_completo', perfil.nome_completo)
                perfil.biografia = profile_data.get('biografia', perfil.biografia)
                perfil.url_perfil = profile_data.get('url_perfil', perfil.url_perfil)
                perfil.save()
                
                return True
            
            return False
        except PerfilRedeSocial.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error syncing profile {perfil_id}: {str(e)}")
            return False
    
    def sync_profile_posts(self, perfil_id: int, limit: int = 10) -> int:
        """Sync posts from a social media profile"""
        try:
            perfil = PerfilRedeSocial.objects.get(id=perfil_id)
            new_posts_count = 0
            
            if perfil.plataforma == 'twitter':
                posts_data = self.scraper.scrape_twitter_posts(perfil.nome_usuario, limit)
            elif perfil.plataforma == 'instagram':
                posts_data = self.scraper.scrape_instagram_posts(perfil.nome_usuario, limit)
            elif perfil.plataforma == 'facebook':
                # For Facebook, use generic scraping as snscrape may not work well
                posts_data = self.scraper.scrape_generic_social_content(perfil.url_perfil)
            elif perfil.plataforma == 'reddit':
                posts_data = self.scraper.scrape_reddit_posts(perfil.nome_usuario, limit)
            else:
                # For other platforms or generic URLs
                posts_data = self.scraper.scrape_generic_social_content(perfil.url_perfil)
            
            for post_data in posts_data:
                # Check if post already exists
                post, created = Postagem.objects.get_or_create(
                    post_id=post_data['post_id'],
                    perfil=perfil,
                    defaults={
                        'conteudo': post_data['conteudo'],
                        'data_postagem': post_data['data_postagem'],
                        'curtidas': post_data['curtidas'],
                        'comentarios': post_data['comentarios'],
                        'compartilhamentos': post_data['compartilhamentos'],
                        'url_postagem': post_data['url_postagem'],
                        'marcadores': post_data['marcadores'],
                    }
                )
                
                if created:
                    new_posts_count += 1
            
            return new_posts_count
        except PerfilRedeSocial.DoesNotExist:
            return 0
        except Exception as e:
            print(f"Error syncing posts for profile {perfil_id}: {str(e)}")
            return 0
    
    def scrape_profile_and_posts(self, perfil_id: int, limit: int = 10) -> Dict[str, int]:
        """Complete sync of profile and posts"""
        profile_synced = self.sync_profile_data(perfil_id)
        posts_count = self.sync_profile_posts(perfil_id, limit)
        
        return {
            'profile_synced': profile_synced,
            'new_posts_count': posts_count
        }
    
    def scrape_by_platform(self, plataforma: str, limit: int = 10) -> List[Dict]:
        """Scrape multiple profiles from a specific platform"""
        perfis = PerfilRedeSocial.objects.filter(plataforma=plataforma, ativo=True)
        results = []
        
        for perfil in perfis:
            result = self.scrape_profile_and_posts(perfil.id, limit)
            results.append({
                'perfil_id': perfil.id,
                'perfil_nome': perfil.nome_usuario,
                'result': result
            })
        
        return results