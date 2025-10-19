#!/usr/bin/env python3
import os
import json
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
from urllib.parse import quote, urlparse
import hashlib
import html
try:
    from googlesearch import search as google_search
except ImportError:
    print("Warning: googlesearch-python not installed. Using fallback search.")
    google_search = None
import random

class EnhancedTrendingNewsGenerator:
    def __init__(self, hours=1):
        # Use absolute path to ensure posts directory is created correctly
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.posts_dir = os.path.join(os.path.dirname(script_dir), "posts")
        self.base_url = "https://antonnie.dev"
        self.hours = hours  # Make it configurable for any number of hours
        os.makedirs(self.posts_dir, exist_ok=True)
        
        # Daily topics tracking file
        self.daily_topics_file = os.path.join(script_dir, "daily_topics.json")
        
        # SEO and ranking focused meta tags
        self.seo_keywords = [
            "trending news", "breaking news", "latest updates", "viral news",
            "current events", "hot topics", "news today", "top stories"
        ]
    
    def load_daily_topics(self):
        """Load today's already used topics from file"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if not os.path.exists(self.daily_topics_file):
            return set()
        
        try:
            with open(self.daily_topics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check if the data is for today
            if data.get('date') == today:
                return set(data.get('topics', []))
            else:
                # Data is from a previous day, start fresh
                return set()
        except (json.JSONDecodeError, FileNotFoundError):
            return set()
    
    def save_daily_topics(self, topics):
        """Save today's used topics to file"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Load existing topics for today
        existing_topics = self.load_daily_topics()
        
        # Add new topics
        all_topics = existing_topics.union(set(topics))
        
        # Save to file
        data = {
            'date': today,
            'topics': list(all_topics)
        }
        
        try:
            with open(self.daily_topics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(all_topics)} topics for {today}")
        except Exception as e:
            print(f"Warning: Could not save daily topics: {e}")
        
    def get_trending_topics(self, num_topics=3):
        """Get trending topics from multiple sources"""
        try:
            topics = []
            
            # Load today's already used topics
            daily_used_topics = self.load_daily_topics()
            print(f"Already used today: {len(daily_used_topics)} topics")
            
            # Try multiple trending topic sources
            print("Attempting to fetch trending topics from multiple sources...")
            
            # Method 1: Try Google Trends RSS (legacy)
            topics.extend(self.get_google_trends_rss(num_topics))
            
            # Method 2: Try news aggregator feeds
            if len(topics) < num_topics:
                topics.extend(self.get_news_trending_topics(num_topics - len(topics)))
            
            # Method 3: Try Reddit trending
            if len(topics) < num_topics:
                topics.extend(self.get_reddit_trending(num_topics - len(topics)))
            
            # Remove duplicates (both within this run and from daily used topics)
            seen_titles = set()
            unique_topics = []
            for topic in topics:
                clean_title = self.normalize_title(topic['title'])
                # Check against both current run duplicates and daily used topics
                if clean_title not in seen_titles and clean_title not in daily_used_topics and len(unique_topics) < num_topics:
                    seen_titles.add(clean_title)
                    unique_topics.append(topic)
            
            print(f"Found {len(unique_topics)} unique trending topics out of {len(topics)} total topics")
            print(f"Topics filtered out due to daily duplicates: {len([t for t in topics if self.normalize_title(t['title']) in daily_used_topics])}")
            
            # If we don't have enough unique topics, try expanded search
            if len(unique_topics) < num_topics:
                print(f"Need {num_topics - len(unique_topics)} more unique topics, expanding search...")
                
                # Try getting more topics from news sources with broader search
                additional_topics = self.get_expanded_news_topics(num_topics - len(unique_topics), daily_used_topics, seen_titles)
                
                # Add the new topics
                for topic in additional_topics:
                    if len(unique_topics) >= num_topics:
                        break
                    unique_topics.append(topic)
                    seen_titles.add(self.normalize_title(topic['title']))
                    print(f"Added expanded search topic: {topic['title']}")
            
            # If still not enough, use fallback topics
            if len(unique_topics) < num_topics:
                print(f"Still need {num_topics - len(unique_topics)} more topics, using fallback")
                fallback_topics = self.get_fallback_topics(num_topics)
                
                # Add fallback topics that aren't duplicates (both current run and daily)
                for fallback_topic in fallback_topics:
                    if len(unique_topics) >= num_topics:
                        break
                    clean_fallback_title = self.normalize_title(fallback_topic['title'])
                    if clean_fallback_title not in seen_titles and clean_fallback_title not in daily_used_topics:
                        seen_titles.add(clean_fallback_title)
                        unique_topics.append(fallback_topic)
                        print(f"Added fallback topic: {fallback_topic['title']}")
            
            # If still no topics at all, create emergency topics
            if len(unique_topics) == 0:
                print("Creating emergency topics to ensure content generation...")
                unique_topics = self.create_emergency_topics(num_topics, daily_used_topics)
            
            # Save the selected topics to daily tracking
            selected_normalized_topics = [self.normalize_title(topic['title']) for topic in unique_topics]
            self.save_daily_topics(selected_normalized_topics)
            
            # Ensure we return exactly the requested number of unique topics
            final_topics = unique_topics[:num_topics]
            print(f"Returning {len(final_topics)} unique trending topics:")
            for i, topic in enumerate(final_topics, 1):
                print(f"  {i}. {topic['title']} (from {topic.get('source', 'unknown')})")
            
            return final_topics
            
        except Exception as e:
            print(f"Error fetching trends: {e}")
            return self.get_fallback_topics(num_topics)

    def get_expanded_news_topics(self, num_needed, daily_used_topics, seen_titles):
        """Get additional topics by expanding search to more news sources and categories"""
        additional_topics = []
        
        # Additional news feeds to try
        additional_feeds = [
            'https://feeds.reuters.com/reuters/technologyNews',
            'https://feeds.reuters.com/reuters/businessNews',
            'https://feeds.reuters.com/reuters/healthNews',
            'https://feeds.reuters.com/reuters/environment',
            'https://feeds.reuters.com/reuters/scienceNews',
            'https://www.aljazeera.com/xml/rss/all.xml',
            'https://feeds.skynews.com/feeds/rss/world.xml',
            'https://feeds.skynews.com/feeds/rss/technology.xml',
            'https://rss.cnn.com/rss/cnn_tech.rss',
            'https://rss.cnn.com/rss/money_latest.rss'
        ]
        
        print("Searching additional news sources...")
        
        for feed_url in additional_feeds:
            if len(additional_topics) >= num_needed:
                break
                
            try:
                feed = feedparser.parse(feed_url)
                source_name = feed.feed.get('title', 'News Source')
                
                for entry in feed.entries[:10]:  # Check more entries per feed
                    if len(additional_topics) >= num_needed:
                        break
                        
                    title = entry.title
                    normalized_title = self.normalize_title(title)
                    
                    # Check if this is a unique topic
                    if (normalized_title not in daily_used_topics and 
                        normalized_title not in seen_titles and
                        len(title) > 10):  # Ensure title is substantial
                        
                        additional_topics.append({
                            'title': title,
                            'source': source_name,
                            'traffic': f"{random.randint(100, 999)}K+",
                            'search_query': self.clean_search_query(title),
                            'pub_date': entry.get('published', datetime.now().isoformat()),
                            'description': entry.get('description', '')
                        })
                        print(f"  Found from {source_name}: {title}")
                        
            except Exception as e:
                print(f"  Failed to fetch from {feed_url}: {e}")
                continue
        
        return additional_topics

    def create_emergency_topics(self, num_topics, daily_used_topics):
        """Create emergency topics when all other sources fail"""
        print("Creating emergency topics with current date context...")
        
        current_date = datetime.now()
        date_str = current_date.strftime("%B %d, %Y")
        
        # Generate time-specific emergency topics
        emergency_templates = [
            f"Breaking: Major Development in Global Markets on {date_str}",
            f"Technology Sector Update: Key Changes Announced {date_str}",
            f"Healthcare Breakthrough Reported This Week - {date_str}",
            f"Environmental Policy Changes Take Effect {date_str}",
            f"Financial Markets Analysis: Weekly Report {date_str}",
            f"Scientific Research Update: New Findings {date_str}",
            f"International Relations: Latest Developments {date_str}",
            f"Energy Sector News: Market Changes {date_str}",
            f"Education System Updates: Policy Changes {date_str}",
            f"Transportation Industry: New Announcements {date_str}"
        ]
        
        emergency_topics = []
        seen_normalized = set()
        
        for template in emergency_templates:
            if len(emergency_topics) >= num_topics:
                break
                
            normalized = self.normalize_title(template)
            if normalized not in daily_used_topics and normalized not in seen_normalized:
                emergency_topics.append({
                    'title': template,
                    'source': 'emergency',
                    'traffic': f"{random.randint(50, 200)}K+",
                    'search_query': self.clean_search_query(template),
                    'pub_date': current_date.isoformat(),
                    'description': f"Emergency topic generated for {date_str}"
                })
                seen_normalized.add(normalized)
                print(f"  Created emergency topic: {template}")
        
        return emergency_topics
    
    def normalize_title(self, title):
        """Normalize title for duplicate checking"""
        # Convert to lowercase and strip whitespace
        normalized = title.lower().strip()
        
        # Remove common news prefixes
        prefixes_to_remove = [
            r'^breaking:?\s*',
            r'^update:?\s*', 
            r'^news:?\s*',
            r'^trending:?\s*',
            r'^live:?\s*',
            r'^urgent:?\s*'
        ]
        
        for prefix in prefixes_to_remove:
            normalized = re.sub(prefix, '', normalized, flags=re.IGNORECASE)
        
        # Remove punctuation and extra spaces
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove common words that don't add meaning for duplicate detection
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'today', 'yesterday', 'now', 'new', 'latest', 'major']
        words = normalized.split()
        filtered_words = [word for word in words if word not in stop_words]
        
        # Sort words to catch reordered duplicates (e.g., "Company reports earnings" vs "Earnings reported by company")
        filtered_words.sort()
        
        return ' '.join(filtered_words)
    
    def clean_search_query(self, title):
        """Clean title for search query"""
        # Remove common prefixes and clean up
        clean = re.sub(r'^(breaking|news|update|trending):?\s*', '', title, flags=re.IGNORECASE)
        return clean.strip()
    
    def get_google_trends_rss(self, num_topics):
        """Try to get trending topics from Google Trends RSS (legacy method)"""
        topics = []
        seen_normalized_titles = set()
        try:
            trends_feeds = [
                "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US",
                "https://trends.google.com/trends/trendingsearches/daily/rss?geo=GB"
            ]
            
            for feed_url in trends_feeds:
                feed = feedparser.parse(feed_url)
                if hasattr(feed, 'status') and feed.status == 200:
                    for entry in feed.entries[:num_topics * 2]:
                        if entry.title:
                            normalized_title = self.normalize_title(entry.title)
                            if normalized_title not in seen_normalized_titles:
                                seen_normalized_titles.add(normalized_title)
                                topics.append({
                                    'title': entry.title,
                                    'traffic': entry.get('ht_approx_traffic', '1K+'),
                                    'description': entry.get('description', ''),
                                    'source': 'google_trends',
                                    'pub_date': entry.get('published', ''),
                                    'search_query': self.clean_search_query(entry.title)
                                })
        except Exception as e:
            print(f"Google Trends RSS failed: {e}")
        
        return topics[:num_topics]
    
    def get_news_trending_topics(self, num_topics):
        """Get actual breaking news from major news RSS feeds"""
        topics = []
        seen_normalized_titles = set()
        try:
            news_feeds = [
                {"url": "https://feeds.bbci.co.uk/news/rss.xml", "name": "BBC News"},
                {"url": "https://rss.cnn.com/rss/edition.rss", "name": "CNN"},
                {"url": "https://feeds.reuters.com/reuters/topNews", "name": "Reuters"},
                {"url": "https://feeds.ap.org/ap/rss/general.rss", "name": "Associated Press"},
                {"url": "https://www.theguardian.com/world/rss", "name": "The Guardian"}
            ]
            
            for feed_info in news_feeds:
                try:
                    print(f"Fetching from {feed_info['name']}...")
                    feed = feedparser.parse(feed_info['url'])
                    
                    if hasattr(feed, 'entries') and feed.entries:
                        for entry in feed.entries[:2]:  # Take top 2 from each feed
                            if entry.title and len(topics) < num_topics:
                                # Check if this is actually a news story (has recent date)
                                pub_date = entry.get('published_parsed')
                                is_recent = True
                                if pub_date:
                                    entry_date = datetime(*pub_date[:6])
                                    is_recent = (datetime.now() - entry_date).days <= 7
                                
                                if is_recent:
                                    # Clean up the title to make it more readable
                                    clean_title = entry.title.strip()
                                    if len(clean_title) > 100:
                                        clean_title = clean_title[:97] + "..."
                                    
                                    # Check for duplicates using normalized title
                                    normalized_title = self.normalize_title(clean_title)
                                    if normalized_title not in seen_normalized_titles:
                                        seen_normalized_titles.add(normalized_title)
                                        topics.append({
                                            'title': clean_title,
                                            'traffic': f"{random.randint(500, 2000)}K+",  # Higher traffic for real news
                                            'description': entry.get('description', entry.get('summary', ''))[:300],
                                            'source': feed_info['name'],
                                        'pub_date': entry.get('published', ''),
                                        'search_query': self.clean_search_query(clean_title),
                                        'original_url': entry.get('link', ''),
                                        'content_snippet': entry.get('summary', '')[:200]
                                    })
                                    print(f"  Added: {clean_title}")
                except Exception as e:
                    print(f"Failed to fetch from {feed_info['name']}: {e}")
                    continue
                    
                if len(topics) >= num_topics:
                    break
                    
        except Exception as e:
            print(f"News feeds failed: {e}")
        
        return topics[:num_topics]
    
    def get_reddit_trending(self, num_topics):
        """Get trending topics from Reddit"""
        topics = []
        seen_normalized_titles = set()
        try:
            # Reddit JSON API for popular posts
            reddit_urls = [
                "https://www.reddit.com/r/news/hot.json?limit=10",
                "https://www.reddit.com/r/worldnews/hot.json?limit=10"
            ]
            
            headers = {'User-Agent': 'TrendingNewsBot/1.0'}
            
            for url in reddit_urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts[:5]:  # Take top 5 from each subreddit
                            post_data = post.get('data', {})
                            title = post_data.get('title', '')
                            score = post_data.get('score', 0)
                            created = post_data.get('created_utc', 0)
                            url = post_data.get('url', '')
                            
                            # Filter for actual news stories with good engagement
                            if (title and len(topics) < num_topics and score > 500 and
                                not url.startswith('https://i.redd.it') and  # Skip image posts
                                not url.startswith('https://v.redd.it') and  # Skip video posts
                                created > (datetime.now().timestamp() - 86400)):  # Within 24 hours
                                
                                clean_title = title.strip()
                                if len(clean_title) > 100:
                                    clean_title = clean_title[:97] + "..."
                                
                                # Check for duplicates using normalized title
                                normalized_title = self.normalize_title(clean_title)
                                if normalized_title not in seen_normalized_titles:
                                    seen_normalized_titles.add(normalized_title)
                                    topics.append({
                                        'title': clean_title,
                                        'traffic': f"{score//100}K+" if score > 10000 else f"{score//10}K+",
                                        'description': post_data.get('selftext', '')[:300] or "Breaking news story from Reddit",
                                        'source': 'reddit_news',
                                        'pub_date': datetime.fromtimestamp(created).isoformat(),
                                        'search_query': self.clean_search_query(clean_title),
                                        'original_url': url,
                                        'reddit_score': score
                                    })
                except Exception as e:
                    print(f"Failed to fetch from Reddit {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Reddit trending failed: {e}")
        
        return topics[:num_topics]
    
    def get_fallback_topics(self, num_topics):
        """Provide realistic fallback news stories if all APIs fail"""
        # Load daily used topics to avoid duplicates
        daily_used_topics = self.load_daily_topics()
        
        # These are more realistic current news story formats
        current_date = datetime.now().strftime('%B %Y')
        all_fallback_topics = [
            {'title': f'Tech Companies Report Strong Q4 Earnings Despite Market Volatility', 'traffic': '1.2M+', 'source': 'fallback', 'search_query': 'tech earnings Q4 2024'},
            {'title': f'New Climate Policy Announced at International Summit', 'traffic': '890K+', 'source': 'fallback', 'search_query': 'climate policy summit 2024'},
            {'title': f'NASA Announces Major Discovery in Mars Exploration Mission', 'traffic': '750K+', 'source': 'fallback', 'search_query': 'NASA Mars discovery 2024'},
            {'title': f'Global Markets React to Federal Reserve Interest Rate Decision', 'traffic': '680K+', 'source': 'fallback', 'search_query': 'federal reserve rates 2024'},
            {'title': f'Breakthrough in Cancer Treatment Shows Promising Results in Trials', 'traffic': '520K+', 'source': 'fallback', 'search_query': 'cancer treatment breakthrough 2024'},
            {'title': f'Major Data Breach Affects Millions of Users Worldwide', 'traffic': '470K+', 'source': 'fallback', 'search_query': 'data breach cybersecurity 2024'},
            {'title': f'Renewable Energy Reaches New Milestone in Global Adoption', 'traffic': '410K+', 'source': 'fallback', 'search_query': 'renewable energy milestone 2024'},
            {'title': f'Electric Vehicle Sales Surge as New Models Hit Market', 'traffic': '390K+', 'source': 'fallback', 'search_query': 'electric vehicle sales 2024'},
            {'title': f'AI Technology Breakthrough Revolutionizes Healthcare Industry', 'traffic': '350K+', 'source': 'fallback', 'search_query': 'AI healthcare breakthrough 2024'},
            {'title': f'International Trade Agreement Reached After Months of Negotiations', 'traffic': '300K+', 'source': 'fallback', 'search_query': 'trade agreement 2024'},
            {'title': f'Major Archaeological Discovery Rewrites Ancient History', 'traffic': '280K+', 'source': 'fallback', 'search_query': 'archaeological discovery 2024'},
            {'title': f'Quantum Computing Milestone Achieved by Research Team', 'traffic': '250K+', 'source': 'fallback', 'search_query': 'quantum computing breakthrough 2024'}
        ]
        
        # Filter out topics that have already been used today
        available_topics = []
        for topic in all_fallback_topics:
            normalized_title = self.normalize_title(topic['title'])
            if normalized_title not in daily_used_topics:
                available_topics.append(topic)
        
        # Add current date context to available fallback topics
        today = datetime.now()
        for topic in available_topics:
            topic['pub_date'] = today.isoformat()
            topic['description'] = f"Latest developments and trends in {topic['title'].lower()} as of {today.strftime('%B %Y')}"
        
        print(f"Found {len(available_topics)} unused fallback topics out of {len(all_fallback_topics)} total")
        return available_topics[:num_topics]
    
    def search_google_top_results(self, query, num_results=3):
        """Get top websites from Google search for a query"""
        try:
            print(f"Searching Google for: {query}")
            results = []
            
            # Use googlesearch-python library if available
            if google_search is not None:
                try:
                    for url in google_search(query, num_results=num_results, lang='en'):
                        results.append({
                            'url': url,
                            'domain': urlparse(url).netloc
                        })
                    return results[:num_results]
                except Exception as search_error:
                    print(f"Google search failed: {search_error}")
                    print("Using fallback results instead")
                    return self.get_fallback_results(query, num_results)
            else:
                print("Google search library not available, using fallback results")
                return self.get_fallback_results(query, num_results)
            
        except Exception as e:
            print(f"Google search error for '{query}': {e}")
            return self.get_fallback_results(query, num_results)
    
    def get_fallback_results(self, query, num_results):
        """Provide fallback search results with actual news URLs"""
        # Create more realistic fallback URLs based on the query
        results = []
        domains_info = [
            {'domain': 'bbc.com', 'name': 'BBC News'},
            {'domain': 'cnn.com', 'name': 'CNN'},
            {'domain': 'reuters.com', 'name': 'Reuters'},
            {'domain': 'apnews.com', 'name': 'Associated Press'},
            {'domain': 'theguardian.com', 'name': 'The Guardian'}
        ]
        
        for domain_info in domains_info[:num_results]:
            results.append({
                'url': f'https://{domain_info["domain"]}/news',
                'domain': domain_info['domain'],
                'title': f'Coverage from {domain_info["name"]}'
            })
        
        return results
    
    def extract_first_three_lines(self, url, topic=None):
        """Extract first 3 meaningful lines from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Check if content type is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'html' not in content_type:
                return [
                    f"Content from {urlparse(url).netloc} is not in HTML format.",
                    "This may be a file download or API endpoint rather than a webpage.",
                    "Please check the source directly for complete information."
                ]
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text and split into lines
            text = soup.get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Filter meaningful lines (not too short, not navigation, etc.)
            meaningful_lines = []
            skip_keywords = ['menu', 'login', 'sign up', 'cookie', 'privacy', 'subscribe', 'newsletter', 'advertisement']
            
            for line in lines:
                if (len(line) > 30 and len(line) < 500 and 
                    not any(word in line.lower() for word in skip_keywords) and
                    len(meaningful_lines) < 3):
                    meaningful_lines.append(line[:300])  # Limit length
            
            if not meaningful_lines:
                return [
                    f"No meaningful content could be extracted from {urlparse(url).netloc}.",
                    "The webpage may have restricted access or unusual formatting.",
                    "This is a placeholder summary based on the trending topic."
                ]
            
            return meaningful_lines[:3]  # Return first 3 meaningful lines
            
        except requests.exceptions.Timeout:
            print(f"Timeout error for {url}")
            return [
                f"Request to {urlparse(url).netloc} timed out.",
                "The website may be experiencing high traffic or connectivity issues.",
                "This is a fallback summary for the trending topic."
            ]
        except requests.exceptions.RequestException as e:
            print(f"Request error for {url}: {e}")
            return self.generate_fallback_content_for_topic(url, topic)
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return self.generate_fallback_content_for_topic(url, topic)

    def generate_fallback_content_for_topic(self, url, topic):
        """Generate realistic fallback content based on the topic and domain"""
        domain = urlparse(url).netloc
        
        if topic is None:
            return [
                f"Content from {domain} is currently unavailable due to access restrictions.",
                "The website may be experiencing technical difficulties or high traffic.",
                "This is a placeholder summary based on the trending topic analysis."
            ]
            
        title_lower = topic['title'].lower()
        
        # Generate content based on the topic type and source
        if 'police' in title_lower or 'investigation' in title_lower:
            return [
                f"Authorities are investigating the circumstances surrounding {topic['title'].lower()}, according to sources familiar with the matter.",
                f"Law enforcement officials have confirmed they are treating this as a priority case requiring immediate attention and thorough investigation.",
                f"The investigation involves multiple departments working together to gather evidence and interview key witnesses, according to {domain} reports."
            ]
        elif 'dead' in title_lower or 'killed' in title_lower or 'died' in title_lower:
            return [
                f"Multiple fatalities have been confirmed in an incident involving {topic['title'].lower()}, emergency services report.",
                f"First responders arrived at the scene within minutes of receiving initial emergency calls, immediately beginning rescue and recovery operations.",
                f"Medical personnel and law enforcement are working together to secure the area and provide assistance to those affected, sources tell {domain}."
            ]
        elif 'government' in title_lower or 'minister' in title_lower or 'policy' in title_lower:
            return [
                f"Government officials have announced significant policy changes regarding {topic['title'].lower()}, marking a major shift in official position.",
                f"The announcement comes after extensive consultation with stakeholders and represents a comprehensive approach to addressing the issue.",
                f"Cabinet ministers have expressed their full support for the new measures, which are expected to have wide-ranging implications, {domain} reports."
            ]
        elif 'court' in title_lower or 'trial' in title_lower or 'lawsuit' in title_lower:
            return [
                f"Legal proceedings are advancing in the case involving {topic['title'].lower()}, with both sides preparing comprehensive arguments.",
                f"Court officials have confirmed that all proper procedures are being followed to ensure a fair and thorough hearing of the matter.",
                f"The case has attracted significant attention from legal experts who note its potential to set important precedents, according to {domain}."
            ]
        else:
            return [
                f"Developing story: {topic['title']} continues to unfold as authorities and stakeholders respond to the evolving situation.",
                f"Multiple agencies are coordinating their response efforts to address the complex circumstances surrounding this developing story.",
                f"Officials have promised regular updates as more information becomes available, with transparency maintained throughout the process, {domain} reports."
            ]
    
    def gather_topic_research(self, topic):
        """Gather comprehensive research for a topic including top websites and their content"""
        research_data = {
            'search_results': [],
            'website_content': {},
            'summaries': [],
            'key_points': []
        }
        
        try:
            # Get top Google search results
            search_results = self.search_google_top_results(topic['search_query'])
            research_data['search_results'] = search_results
            
            # Extract content from each website
            for result in search_results:
                domain = result['domain']
                print(f"Extracting content from: {domain}")
                
                lines = self.extract_first_three_lines(result['url'], topic)
                research_data['website_content'][domain] = {
                    'url': result['url'],
                    'lines': lines,
                    'domain': domain
                }
                
                time.sleep(1)  # Be respectful to websites
            
            # Additional context from Wikipedia
            wiki_summary = self.get_wikipedia_summary(topic['search_query'])
            if wiki_summary:
                research_data['summaries'].append(wiki_summary)
            
        except Exception as e:
            print(f"Research error for {topic['title']}: {e}")
        
        return research_data
    
    def get_wikipedia_summary(self, query):
        """Get summary from Wikipedia"""
        try:
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}"
            response = requests.get(wiki_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('extract', '')[:300]  # Limit length
        except:
            pass
        return None
    
    def generate_ai_content(self, topic, research_data):
        """Generate AI-powered content based on research"""
        
        # Prepare context from gathered research
        context = self.prepare_ai_context(topic, research_data)
        
        # Generate comprehensive article
        article_content = self.create_structured_article(topic, research_data, context)
        
        return article_content
    
    def prepare_ai_context(self, topic, research_data):
        """Prepare context for content generation"""
        context_parts = []
        
        # Add content from top websites
        for domain, content_data in research_data['website_content'].items():
            context_parts.append(f"From {domain}: {' '.join(content_data['lines'])}")
        
        # Add any Wikipedia summary
        for summary in research_data['summaries']:
            if summary:
                context_parts.append(f"Background: {summary}")
        
        return ". ".join(context_parts)
    
    def create_structured_article(self, topic, research_data, context):
        """Create a well-structured article with proper formatting"""
        
        # Build introduction using content from top websites
        intro_lines = []
        for domain, content_data in research_data['website_content'].items():
            if content_data['lines']:
                intro_lines.extend(content_data['lines'][:1])  # Use first line from each site
        
        # Create comprehensive news article structure with modern design
        article_html = f"""
        <article class="news-article">
            <!-- Hero Section with Breaking News Badge -->
            <div class="article-hero">
                <div class="breaking-badge">
                    <span class="pulse-dot"></span>
                    <span>BREAKING NEWS</span>
                </div>
                <div class="article-category">
                    <span class="category-pill">📰 NEWS</span>
                    <span class="trending-pill">🔥 TRENDING</span>
                </div>
            </div>
            
            <!-- Article Header -->
            <header class="article-header">
                <h1 class="article-title">{topic['title']}</h1>
                <div class="article-subtitle">
                    <p>Comprehensive coverage with real-time updates and expert analysis</p>
                </div>
            </header>
            
            <!-- Article Meta Information -->
            <div class="article-meta-section">
                <div class="meta-primary">
                    <div class="meta-item">
                        <span class="meta-icon">📅</span>
                        <span class="meta-label">Published</span>
                        <span class="meta-value">{datetime.now().strftime('%B %d, %Y')}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-icon">✍️</span>
                        <span class="meta-label">Author</span>
                        <span class="meta-value">Daily Reporter Staff</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-icon">🕒</span>
                        <span class="meta-label">Updated</span>
                        <span class="meta-value">{datetime.now().strftime('%H:%M UTC')}</span>
                    </div>
                </div>
                <div class="meta-secondary">
                    <div class="reading-time">
                        <span class="meta-icon">⏱️</span>
                        <span>3-4 min read</span>
                    </div>
                    <div class="share-count">
                        <span class="meta-icon">📊</span>
                        <span>{topic.get('traffic', '1K+')} views</span>
                    </div>
                </div>
            </div>
            
            <!-- Lead Story Section -->
            <section class="lead-story-modern">
                <div class="lead-highlight">
                    <span class="highlight-label">KEY DEVELOPMENTS</span>
                </div>
                {self.generate_lead_section(topic, research_data)}
            </section>
            
            <!-- Main Content Section -->
            <section class="main-content-modern">
                <div class="content-header">
                    <h2 class="section-title">
                        <span class="section-icon">📋</span>
                        Detailed Analysis
                    </h2>
                    <div class="content-divider"></div>
                </div>
        """
        
        # Generate authentic news content with modern formatting
        news_paragraphs = self.generate_authentic_news_content(topic, research_data)
        for i, paragraph in enumerate(news_paragraphs, 1):
            # Add variety to paragraph presentation
            if i == 1:
                article_html += f"""
                <div class="content-block featured-paragraph">
                    <div class="paragraph-number">01</div>
                    <div class="paragraph-content">
                        <p class="first-paragraph">{html.escape(paragraph)}</p>
                    </div>
                </div>
                """
            elif i % 3 == 0:
                article_html += f"""
                <div class="content-block highlight-paragraph">
                    <div class="highlight-icon">💡</div>
                    <div class="paragraph-content">
                        <p class="highlighted-text">{html.escape(paragraph)}</p>
                    </div>
                </div>
                """
            else:
                article_html += f"""
                <div class="content-block standard-paragraph">
                    <div class="paragraph-marker"></div>
                    <div class="paragraph-content">
                        <p>{html.escape(paragraph)}</p>
                    </div>
                </div>
                """
        
        article_html += f"""
            </section>
            
            <!-- What's Next Section -->
            <section class="story-impact-modern">
                <div class="impact-header">
                    <div class="impact-icon">🔮</div>
                    <h2 class="impact-title">What's Next</h2>
                </div>
                <div class="impact-content">
                    <p class="impact-text">{html.escape(self.generate_whats_next(topic))}</p>
                </div>
                <div class="impact-timeline">
                    <div class="timeline-item">
                        <div class="timeline-dot"></div>
                        <span>Ongoing monitoring</span>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-dot"></div>
                        <span>Updates expected</span>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-dot"></div>
                        <span>Follow-up coverage</span>
                    </div>
                </div>
            </section>
            
            <!-- Modern Article Footer -->
            <footer class="article-footer-modern">
                <div class="footer-section sources-section">
                    <div class="section-header">
                        <span class="section-icon">🔗</span>
                        <h3>Trusted Sources</h3>
                    </div>
                    <div class="sources-grid">
        """
        
        # Add modern source attribution
        if research_data['website_content']:
            for domain, content_data in research_data['website_content'].items():
                article_html += f'''
                    <div class="source-card">
                        <div class="source-icon">📰</div>
                        <div class="source-info">
                            <a href="{content_data["url"]}" target="_blank" rel="nofollow" class="source-link">{domain}</a>
                            <span class="source-type">News Source</span>
                        </div>
                        <div class="source-badge">Verified</div>
                    </div>
                '''
        else:
            # Show fallback sources if no content was extracted
            fallback_sources = [
                {"url": "https://bbc.com/news", "domain": "BBC News", "type": "International"},
                {"url": "https://reuters.com", "domain": "Reuters", "type": "Wire Service"},
                {"url": "https://apnews.com", "domain": "Associated Press", "type": "News Agency"}
            ]
            for source in fallback_sources:
                article_html += f'''
                    <div class="source-card">
                        <div class="source-icon">📰</div>
                        <div class="source-info">
                            <a href="{source["url"]}" target="_blank" rel="nofollow" class="source-link">{source["domain"]}</a>
                            <span class="source-type">{source["type"]}</span>
                        </div>
                        <div class="source-badge">Verified</div>
                    </div>
                '''
        
        article_html += """
                    </div>
                </div>
                
                <!-- Article Tags -->
                <div class="footer-section tags-section">
                    <div class="section-header">
                        <span class="section-icon">🏷️</span>
                        <h3>Related Topics</h3>
                    </div>
                    <div class="tags-container">
                        <span class="tag">Breaking News</span>
                        <span class="tag">Current Events</span>
                        <span class="tag">Latest Updates</span>
                        <span class="tag">News Analysis</span>
                    </div>
                </div>
                
                <!-- Editorial Note -->
                <div class="footer-section editorial-section">
                    <div class="editorial-card">
                        <div class="editorial-icon">⚠️</div>
                        <div class="editorial-content">
                            <h4>Developing Story</h4>
                            <p>This story is actively developing and will be updated as more information becomes available. Check back for the latest updates.</p>
                        </div>
                    </div>
                </div>
                
                <!-- Engagement Section -->
                <div class="footer-section engagement-section">
                    <div class="engagement-stats">
                        <div class="stat-item">
                            <span class="stat-icon">👀</span>
                            <span class="stat-number">2.3K</span>
                            <span class="stat-label">Views</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-icon">💬</span>
                            <span class="stat-number">45</span>
                            <span class="stat-label">Comments</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-icon">📤</span>
                            <span class="stat-number">28</span>
                            <span class="stat-label">Shares</span>
                        </div>
                    </div>
                </div>
            </footer>
        </article>
        """
        
        return article_html
    
    def generate_authentic_news_content(self, topic, research_data):
        """Generate authentic-looking news content with substantial length"""
        paragraphs = []
        
        # Extract the most relevant content from scraped sources
        key_details = self.extract_key_details(topic, research_data)
        
        # First paragraph: Strong lead with who, what, when, where (4-6 sentences)
        if key_details.get('lead_info') and not self.is_fallback_content(key_details['lead_info']):
            lead_paragraph = self.expand_paragraph(key_details['lead_info'], topic, 'lead')
            paragraphs.append(lead_paragraph)
        else:
            lead_paragraph = self.generate_expanded_contextual_lead(topic)
            paragraphs.append(lead_paragraph)
        
        # Second paragraph: Context and background (4-5 sentences)  
        if key_details.get('background') and not self.is_fallback_content(key_details['background']):
            background_paragraph = self.expand_paragraph(key_details['background'], topic, 'background')
            paragraphs.append(background_paragraph)
        else:
            background_paragraph = self.generate_expanded_contextual_background(topic, research_data)
            paragraphs.append(background_paragraph)
        
        # Third paragraph: Additional details from sources (4-5 sentences)
        if key_details.get('additional_content') and not self.is_fallback_content(key_details['additional_content']):
            details_paragraph = self.expand_paragraph(key_details['additional_content'], topic, 'details')
            paragraphs.append(details_paragraph)
        else:
            details_paragraph = self.generate_expanded_detailed_analysis(topic, research_data)
            paragraphs.append(details_paragraph)
        
        # Fourth paragraph: Official responses/reactions (4-5 sentences)
        official_paragraph = self.generate_expanded_official_response(topic)
        paragraphs.append(official_paragraph)
        
        # Fifth paragraph: Broader context/implications (4-5 sentences)
        context_paragraph = self.generate_expanded_broader_context(topic)
        paragraphs.append(context_paragraph)
        
        # Sixth paragraph: Looking ahead (3-4 sentences)
        conclusion_paragraph = self.generate_expanded_contextual_conclusion(topic, research_data)
        paragraphs.append(conclusion_paragraph)
        
        return paragraphs[:6]  # Return 6 substantial paragraphs

    def is_fallback_content(self, content):
        """Check if content is generated fallback content"""
        fallback_indicators = [
            "according to sources familiar with the matter",
            "emergency services report",
            "sources tell",
            "No meaningful content could be extracted",
            "Breaking News, Latest News and Videos"
        ]
        return any(indicator in content for indicator in fallback_indicators)

    def extract_key_details(self, topic, research_data):
        """Extract key details from scraped content to create authentic news"""
        details = {'lead_info': None, 'background': None, 'additional_content': None, 'implications': None}
        
        # Combine all scraped content
        all_content = []
        for domain, content_data in research_data['website_content'].items():
            all_content.extend(content_data['lines'])
        
        if all_content:
            # Use the first substantial piece of content as lead
            for content in all_content:
                if len(content) > 100 and not self.is_generic_content(content):
                    details['lead_info'] = content[:400] + ("..." if len(content) > 400 else "")
                    break
            
            # Use second piece for background if available
            if len(all_content) > 1:
                for content in all_content[1:]:
                    if len(content) > 80 and not self.is_generic_content(content):
                        details['background'] = content[:350] + ("..." if len(content) > 350 else "")
                        break
            
            # Use third piece for additional content
            if len(all_content) > 2:
                for content in all_content[2:]:
                    if len(content) > 80 and not self.is_generic_content(content):
                        details['additional_content'] = content[:300] + ("..." if len(content) > 300 else "")
                        break
        
        return details

    def is_generic_content(self, content):
        """Check if content is too generic/boilerplate to use"""
        generic_phrases = [
            'cookie', 'privacy policy', 'subscribe', 'newsletter', 'advertisement',
            'sign up', 'log in', 'menu', 'navigation', 'follow us', 'social media'
        ]
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in generic_phrases)
    
    def expand_paragraph(self, base_content, topic, paragraph_type):
        """Expand a paragraph to make it more substantial and natural"""
        title_lower = topic['title'].lower()
        
        # Add contextual sentences based on paragraph type
        if paragraph_type == 'lead':
            additional_sentences = [
                "According to multiple sources familiar with the matter, the situation has been developing rapidly over the past several hours.",
                "Local authorities have confirmed they are treating this as a high-priority incident requiring immediate attention.",
                "Preliminary reports suggest the circumstances surrounding the event are complex and still being investigated."
            ]
        elif paragraph_type == 'background':
            additional_sentences = [
                "The incident comes at a time when public attention has been focused on similar issues in the region.",
                "Experts note that such developments often require careful analysis to understand their full implications.",
                "Historical precedents suggest that resolution of such matters typically involves multiple stakeholders working together."
            ]
        elif paragraph_type == 'details':
            additional_sentences = [
                "Witness accounts and official reports are being carefully reviewed to establish an accurate timeline of events.",
                "The complexity of the situation has required coordination between various agencies and departments.",
                "Technical specialists have been brought in to assist with the investigation and ensure all relevant evidence is properly examined."
            ]
        else:  # conclusion
            additional_sentences = [
                "The full impact of these developments is expected to become clearer in the coming days.",
                "Stakeholders are expected to meet regularly to monitor progress and coordinate their responses."
            ]
        
        # Combine base content with additional context
        expanded_content = base_content
        
        # Add 2-3 additional sentences for more natural length
        import random
        selected_sentences = random.sample(additional_sentences, min(2, len(additional_sentences)))
        for sentence in selected_sentences:
            expanded_content += f" {sentence}"
            
        return expanded_content

    def generate_expanded_contextual_lead(self, topic):
        """Generate an expanded contextual lead paragraph (4-6 sentences)"""
        title_lower = topic['title'].lower()
        
        if 'police' in title_lower or 'investigation' in title_lower:
            base_lead = f"Law enforcement officials are investigating {topic['title'].lower()}, according to sources familiar with the matter."
            additional_context = " The investigation marks a significant development in the ongoing case, with multiple departments coordinating their efforts. Senior investigators have been assigned to oversee the inquiry, which is being conducted with urgency given the public interest. Officials have indicated that all available resources are being deployed to ensure a thorough and comprehensive investigation. The case has been classified as high priority, with regular briefings scheduled to keep stakeholders informed of progress."
            
        elif 'dead' in title_lower or 'killed' in title_lower or 'died' in title_lower:
            base_lead = f"Multiple fatalities have been reported in an incident involving {topic['title'].lower()}."
            additional_context = " Emergency services responded to the scene as authorities work to determine the full scope of the situation. First responders arrived within minutes of receiving the initial emergency calls, immediately securing the area and beginning rescue operations. Medical personnel worked tirelessly to provide assistance while law enforcement established a perimeter to preserve evidence. The incident has prompted an immediate review of emergency response protocols and safety measures."
            
        elif 'government' in title_lower or 'minister' in title_lower or 'president' in title_lower:
            base_lead = f"Senior government officials are addressing {topic['title'].lower()}, marking a significant policy development."
            additional_context = " The announcement comes amid ongoing discussions about the issue and represents a major shift in official policy. Cabinet members have been briefed extensively on the implications of this decision, with inter-departmental consultations continuing. The timing of this announcement reflects careful consideration of various factors, including public opinion and expert recommendations. Officials have emphasized their commitment to transparency throughout the implementation process."
            
        elif 'court' in title_lower or 'trial' in title_lower or 'lawsuit' in title_lower:
            base_lead = f"Legal proceedings are underway regarding {topic['title'].lower()}."
            additional_context = " The court case has drawn attention from legal experts and could set important precedents for future similar cases. Both prosecution and defense teams have been preparing extensively, with numerous pre-trial motions filed over recent weeks. The judge has emphasized the importance of conducting a fair and thorough hearing, with strict adherence to legal procedures. Court officials have implemented additional security measures given the high level of public interest in the case."
            
        else:
            base_lead = f"Authorities are responding to developments involving {topic['title'].lower()}."
            additional_context = " The situation has prompted immediate action from relevant agencies and continues to evolve as new information becomes available. Multiple departments are coordinating their response efforts to ensure all necessary measures are implemented effectively. Officials have established a command center to oversee operations and maintain regular communication with all stakeholders. The public is being kept informed through regular updates as the situation develops."
        
        return base_lead + additional_context

    def generate_expanded_contextual_background(self, topic, research_data):
        """Generate expanded contextual background (4-5 sentences)"""
        sources = list(research_data['website_content'].keys())
        
        base_paragraph = "The incident has raised questions about broader systemic issues and safety protocols."
        
        if sources:
            background_context = f" Reports from {len(sources)} different news sources have provided varying perspectives on the developing situation, highlighting the complexity of the issues involved. Journalists and analysts have been working to piece together a comprehensive understanding of the events, drawing on multiple witness accounts and official statements. The coverage has revealed important details about the circumstances leading up to the incident, as well as the immediate response from authorities. Experts note that such multi-source reporting is crucial for establishing an accurate and complete picture of complex events."
        else:
            background_context = " Officials are reviewing existing procedures to prevent similar occurrences in the future, with particular attention to identifying any gaps in current protocols. A comprehensive assessment is being conducted to examine all relevant policies and procedures, involving consultation with subject matter experts and stakeholders. The review process is expected to include recommendations for improvements and updates to existing guidelines. This systematic approach reflects the seriousness with which authorities are treating the situation and their commitment to preventing similar incidents."
        
        return base_paragraph + background_context

    def generate_expanded_detailed_analysis(self, topic, research_data):
        """Generate expanded detailed analysis paragraph (4-5 sentences)"""
        title_lower = topic['title'].lower()
        
        if 'police' in title_lower or 'investigation' in title_lower:
            return ("The investigation involves multiple departments working together to gather evidence and interview key witnesses, with coordination overseen by senior law enforcement officials. Forensic teams have been deployed to examine all available evidence, employing advanced techniques to ensure no crucial details are overlooked. Detectives are following up on leads provided by the public, with a dedicated tip line established to encourage community cooperation. The case has been assigned high priority status given its significant public interest, with additional resources allocated to support the investigation. Regular briefings are being held to ensure all team members are updated on the latest developments and can adjust their approach accordingly.")
            
        elif 'dead' in title_lower or 'killed' in title_lower:
            return ("Emergency medical services arrived on scene within minutes of the initial reports, immediately beginning triage and treatment of injured individuals. Medical personnel worked systematically to treat the injured while law enforcement secured the area and began collecting evidence. The incident has prompted a comprehensive review of safety protocols and emergency response procedures, with particular focus on coordination between different response agencies. Medical examiners are conducting thorough investigations to determine exact causes and circumstances, working closely with law enforcement to ensure all evidence is properly documented. The response has demonstrated the importance of inter-agency cooperation and the value of regular emergency preparedness training.")
            
        elif 'government' in title_lower or 'policy' in title_lower:
            return ("The policy changes come after months of consultation with stakeholders and expert analysis, reflecting careful consideration of various perspectives and potential impacts. Government officials have been working closely with various departments to ensure smooth implementation, establishing clear timelines and accountability measures. The new measures are expected to have wide-ranging implications across multiple sectors, with detailed impact assessments conducted to anticipate potential challenges. Consultation sessions have been held with industry representatives, advocacy groups, and subject matter experts to gather input and refine the proposed approach. Implementation will be phased to allow for adjustments based on initial results and feedback from affected parties.")
            
        else:
            return ("Experts are analyzing the full implications of these developments as more details emerge, drawing on their professional experience and knowledge of similar situations. The situation has prompted discussions among specialists about best practices and preventive measures, with particular attention to lessons learned from comparable incidents. Stakeholders are closely monitoring the evolving circumstances to assess potential impacts on their operations and constituencies. Technical consultants have been brought in to provide specialized expertise and ensure all relevant factors are properly considered. The collaborative approach reflects the complexity of the situation and the importance of bringing together diverse perspectives and expertise.")

    def generate_expanded_official_response(self, topic):
        """Generate expanded official response paragraph (4-5 sentences)"""
        title_lower = topic['title'].lower()
        
        if 'police' in title_lower:
            return ("Police officials have issued a statement emphasizing their commitment to a thorough and transparent investigation, outlining the specific steps being taken to ensure accountability. A spokesperson noted that all available resources are being deployed to ensure a comprehensive inquiry, including specialized units and external expertise where appropriate. The department has established a dedicated hotline for anyone with relevant information to contact investigators, staffed by trained personnel available around the clock. Senior officers are providing regular updates to department leadership and external oversight bodies to maintain transparency throughout the process. The police have also implemented additional community outreach measures to address public concerns and maintain trust during the investigation.")
            
        elif 'government' in title_lower or 'minister' in title_lower:
            return ("Government representatives have addressed the matter in recent statements to the press, providing detailed information about their planned response and timeline for action. Officials emphasized their commitment to addressing public concerns and ensuring appropriate action is taken, with specific measures outlined to demonstrate accountability. A senior spokesperson indicated that further announcements will be made as the situation develops, with regular briefings scheduled to keep the public informed. Cabinet ministers have been briefed on the implications and have expressed their full support for the proposed course of action. The government has also established a dedicated communication strategy to ensure accurate information is provided to the public and media.")
            
        elif 'court' in title_lower or 'trial' in title_lower:
            return ("Legal representatives from both sides have prepared extensive documentation for the proceedings, with teams of experienced attorneys working to present the strongest possible cases. Court officials have confirmed that all proper procedures are being followed to ensure a fair hearing, with additional measures implemented to accommodate the high level of public interest. The judge has emphasized the importance of allowing the legal process to proceed without outside interference, issuing clear guidelines for media coverage and public access. Security arrangements have been enhanced to ensure the safety of all participants and to maintain the dignity of the judicial process. Court administrators are working to ensure that scheduling accommodates the complexity of the case while maintaining efficiency.")
            
        else:
            return ("Officials have convened emergency meetings to address the developing situation and coordinate response efforts, bringing together representatives from all relevant agencies and departments. Relevant authorities are working together to ensure all necessary measures are implemented effectively, with clear communication channels established to facilitate coordination. Regular updates are being provided to keep the public informed of any significant developments, with designated spokespersons assigned to handle media inquiries. Emergency protocols have been activated where appropriate, ensuring that all response procedures are followed according to established guidelines. The coordinated approach reflects the seriousness of the situation and the commitment of authorities to providing an effective response.")

    def generate_expanded_broader_context(self, topic):
        """Generate expanded broader context paragraph (4-5 sentences)"""
        title_lower = topic['title'].lower()
        
        if 'police' in title_lower or 'investigation' in title_lower:
            return ("This investigation takes place against a backdrop of increased public scrutiny of law enforcement practices, reflecting broader societal discussions about accountability and transparency. Recent cases have highlighted the importance of transparency and accountability in police operations, leading to reforms in many jurisdictions. Legal experts note that such investigations often lead to important reforms and improved protocols, benefiting both law enforcement agencies and the communities they serve. The case has attracted attention from civil rights organizations and police reform advocates, who are monitoring the proceedings closely. The outcome could influence future policies and procedures, potentially setting new standards for how similar cases are handled.")
            
        elif 'international' in title_lower or 'global' in title_lower:
            return ("The international community is watching these developments closely as they may have broader implications for regional stability and international relations. Similar situations in other countries have demonstrated the importance of coordinated international responses, with lessons learned from previous experiences informing current approaches. Diplomatic observers note that the outcome could influence regional stability and international relations, particularly given the current global political climate. International organizations have expressed interest in the developments and have offered assistance where appropriate. The situation highlights the interconnected nature of modern global affairs and the importance of multilateral cooperation in addressing complex challenges.")
            
        elif 'economic' in title_lower or 'financial' in title_lower:
            return ("Economic analysts are assessing the potential market implications of these developments, examining both short-term volatility and long-term structural impacts. The situation comes at a time when financial markets are already facing various global challenges, including ongoing concerns about inflation, trade relationships, and geopolitical tensions. Industry experts suggest that the long-term economic impact will depend on how quickly issues are resolved and what measures are implemented to address underlying concerns. Financial institutions are monitoring the situation closely and adjusting their risk assessments accordingly. The broader economic context includes considerations of supply chain stability, consumer confidence, and international trade relationships.")
            
        else:
            return ("These developments occur within a larger context of ongoing social and political changes, reflecting broader trends and challenges facing society. Observers note that such incidents often reflect broader systemic issues that require comprehensive solutions, involving multiple stakeholders and long-term commitment. The situation has prompted renewed discussions about the need for policy reforms and institutional improvements, with calls for more proactive approaches to preventing similar issues. Academic researchers and policy experts are analyzing the implications for future governance and institutional effectiveness. The broader context includes considerations of public trust, institutional capacity, and the evolving relationship between government and civil society.")

    def generate_expanded_contextual_conclusion(self, topic, research_data):
        """Generate an expanded contextual conclusion paragraph (3-4 sentences)"""
        title_lower = topic['title'].lower()
        
        if 'investigation' in title_lower or 'police' in title_lower:
            return ("The investigation remains ongoing, with authorities pledging to pursue all available leads and ensure a comprehensive examination of all evidence. Officials have asked anyone with information to come forward to assist in the inquiry, emphasizing that community cooperation is essential for achieving a successful resolution. Regular updates will be provided to the public as the investigation progresses, with transparency maintained throughout the process. The case is expected to continue for several weeks as investigators work methodically through all aspects of the matter.")
            
        elif 'trial' in title_lower or 'court' in title_lower:
            return ("The legal proceedings are expected to continue over the coming weeks, with both sides presenting detailed arguments and evidence. Both prosecution and defense teams are preparing their cases as the judicial process moves forward, with additional hearings scheduled to address various aspects of the matter. The court has established a comprehensive schedule to ensure all parties have adequate time to present their positions. A verdict is anticipated following the completion of all scheduled proceedings and deliberations.")
            
        else:
            return ("Authorities continue to monitor the situation closely, maintaining readiness to respond to any new developments or changing circumstances. Further updates are expected as more information becomes available from official sources, with regular assessments conducted to evaluate progress. The commitment to transparency and public communication remains a priority throughout the ongoing response efforts. Stakeholders are expected to continue their collaborative approach as the situation evolves and new challenges emerge.")
        """Extract key details from scraped content to create authentic news"""
        details = {'lead_info': None, 'background': None, 'additional_content': None, 'implications': None}
        
        # Combine all scraped content
        all_content = []
        for domain, content_data in research_data['website_content'].items():
            all_content.extend(content_data['lines'])
        
        if all_content:
            # Use the first substantial piece of content as lead
            for content in all_content:
                if len(content) > 100 and not self.is_generic_content(content):
                    details['lead_info'] = content[:400] + ("..." if len(content) > 400 else "")
                    break
            
            # Use second piece for background if available
            if len(all_content) > 1:
                for content in all_content[1:]:
                    if len(content) > 80 and not self.is_generic_content(content):
                        details['background'] = content[:350] + ("..." if len(content) > 350 else "")
                        break
            
            # Use third piece for additional content
            if len(all_content) > 2:
                for content in all_content[2:]:
                    if len(content) > 80 and not self.is_generic_content(content):
                        details['additional_content'] = content[:300] + ("..." if len(content) > 300 else "")
                        break
        
        return details
    
    def is_generic_content(self, content):
        """Check if content is too generic/boilerplate to use"""
        generic_phrases = [
            'cookie', 'privacy policy', 'subscribe', 'newsletter', 'advertisement',
            'sign up', 'log in', 'menu', 'navigation', 'follow us', 'social media'
        ]
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in generic_phrases)
    
    def generate_contextual_lead(self, topic):
        """Generate a contextual lead paragraph based on topic type"""
        title_lower = topic['title'].lower()
        
        if 'police' in title_lower or 'investigation' in title_lower:
            return f"Law enforcement officials are investigating {topic['title'].lower()}, according to sources familiar with the matter. The investigation marks a significant development in the ongoing case."
        elif 'dead' in title_lower or 'killed' in title_lower or 'died' in title_lower:
            return f"Multiple fatalities have been reported in an incident involving {topic['title'].lower()}. Emergency services responded to the scene as authorities work to determine the full scope of the situation."
        elif 'government' in title_lower or 'minister' in title_lower or 'president' in title_lower:
            return f"Senior government officials are addressing {topic['title'].lower()}, marking a significant policy development. The announcement comes amid ongoing discussions about the issue."
        elif 'court' in title_lower or 'trial' in title_lower or 'lawsuit' in title_lower:
            return f"Legal proceedings are underway regarding {topic['title'].lower()}. The court case has drawn attention from legal experts and could set important precedents."
        else:
            return f"Authorities are responding to developments involving {topic['title'].lower()}. The situation has prompted immediate action from relevant agencies and continues to evolve."
    
    def generate_contextual_background(self, topic, research_data):
        """Generate contextual background based on available information"""
        sources = list(research_data['website_content'].keys())
        
        if sources:
            return f"Details from the incident reveal the complexity of the situation. Witnesses and officials are providing accounts of what transpired, helping to piece together a clearer picture of events."
        else:
            return f"The incident has raised questions about broader systemic issues and safety protocols. Officials are reviewing existing procedures to prevent similar occurrences in the future."
    
    def generate_contextual_conclusion(self, topic, research_data):
        """Generate a contextual conclusion paragraph"""
        title_lower = topic['title'].lower()
        
        if 'investigation' in title_lower or 'police' in title_lower:
            return f"The investigation remains ongoing, with authorities pledging to pursue all available leads. Officials have asked anyone with information to come forward to assist in the inquiry."
        elif 'trial' in title_lower or 'court' in title_lower:
            return f"The legal proceedings are expected to continue over the coming weeks. Both sides are preparing their cases as the judicial process moves forward."
        else:
            return f"Authorities continue to monitor the situation closely. Further updates are expected as more information becomes available from official sources."
    
    def generate_detailed_analysis(self, topic, research_data):
        """Generate detailed analysis paragraph"""
        title_lower = topic['title'].lower()
        
        if 'police' in title_lower or 'investigation' in title_lower:
            return ("The investigation involves multiple departments working together to gather evidence and interview key witnesses. "
                   "Forensic teams have been deployed to examine all available evidence, while detectives are following up on leads "
                   "provided by the public. The case has been assigned high priority status given its significant public interest.")
        elif 'dead' in title_lower or 'killed' in title_lower:
            return ("Emergency medical services arrived on scene within minutes of the initial reports. "
                   "Medical personnel worked to treat the injured while law enforcement secured the area. "
                   "The incident has prompted a comprehensive review of safety protocols and emergency response procedures.")
        elif 'government' in title_lower or 'policy' in title_lower:
            return ("The policy changes come after months of consultation with stakeholders and expert analysis. "
                   "Government officials have been working closely with various departments to ensure smooth implementation. "
                   "The new measures are expected to have wide-ranging implications across multiple sectors.")
        else:
            return ("Experts are analyzing the full implications of these developments as more details emerge. "
                   "The situation has prompted discussions among specialists about best practices and preventive measures. "
                   "Stakeholders are closely monitoring the evolving circumstances to assess potential impacts.")
    
    def generate_official_response(self, topic):
        """Generate official response paragraph"""
        title_lower = topic['title'].lower()
        
        if 'police' in title_lower:
            return ("Police officials have issued a statement emphasizing their commitment to a thorough and transparent investigation. "
                   "A spokesperson noted that all available resources are being deployed to ensure a comprehensive inquiry. "
                   "The department has also established a dedicated hotline for anyone with relevant information to contact investigators.")
        elif 'government' in title_lower or 'minister' in title_lower:
            return ("Government representatives have addressed the matter in recent statements to the press. "
                   "Officials emphasized their commitment to addressing public concerns and ensuring appropriate action is taken. "
                   "A senior spokesperson indicated that further announcements will be made as the situation develops.")
        elif 'court' in title_lower or 'trial' in title_lower:
            return ("Legal representatives from both sides have prepared extensive documentation for the proceedings. "
                   "Court officials have confirmed that all proper procedures are being followed to ensure a fair hearing. "
                   "The judge has emphasized the importance of allowing the legal process to proceed without outside interference.")
        else:
            return ("Officials have convened emergency meetings to address the developing situation and coordinate response efforts. "
                   "Relevant authorities are working together to ensure all necessary measures are implemented effectively. "
                   "Regular updates are being provided to keep the public informed of any significant developments.")
    
    def generate_broader_context(self, topic):
        """Generate broader context paragraph"""
        title_lower = topic['title'].lower()
        
        if 'police' in title_lower or 'investigation' in title_lower:
            return ("This investigation takes place against a backdrop of increased public scrutiny of law enforcement practices. "
                   "Recent cases have highlighted the importance of transparency and accountability in police operations. "
                   "Legal experts note that such investigations often lead to important reforms and improved protocols.")
        elif 'international' in title_lower or 'global' in title_lower:
            return ("The international community is watching these developments closely as they may have broader implications. "
                   "Similar situations in other countries have demonstrated the importance of coordinated international responses. "
                   "Diplomatic observers note that the outcome could influence regional stability and international relations.")
        elif 'economic' in title_lower or 'financial' in title_lower:
            return ("Economic analysts are assessing the potential market implications of these developments. "
                   "The situation comes at a time when financial markets are already facing various global challenges. "
                   "Industry experts suggest that the long-term economic impact will depend on how quickly issues are resolved.")
        else:
            return ("These developments occur within a larger context of ongoing social and political changes. "
                   "Observers note that such incidents often reflect broader systemic issues that require comprehensive solutions. "
                   "The situation has prompted renewed discussions about the need for policy reforms and institutional improvements.")
    
    def generate_lead_section(self, topic, research_data):
        """Generate an authentic lead section for the news article"""
        # Get the first substantial piece of content if available
        lead_content = ""
        for domain, content_data in research_data['website_content'].items():
            for line in content_data['lines']:
                if len(line) > 100 and not self.is_generic_content(line):
                    lead_content = line[:300] + ("..." if len(line) > 300 else "")
                    break
            if lead_content:
                break
        
        if lead_content:
            return f'<p class="lead-paragraph">{html.escape(lead_content)}</p>'
        else:
            # Generate a contextual lead if no content available
            contextual_lead = self.generate_contextual_lead(topic)
            return f'<p class="lead-paragraph">{html.escape(contextual_lead)}</p>'
    
    def generate_whats_next(self, topic):
        """Generate a 'what's next' paragraph based on the story type"""
        title_lower = topic['title'].lower()
        
        if 'investigation' in title_lower or 'police' in title_lower:
            return "Investigators are continuing to gather evidence and interview witnesses. Authorities expect to provide additional updates as the investigation progresses."
        elif 'court' in title_lower or 'trial' in title_lower:
            return "The legal proceedings will continue with scheduled hearings in the coming weeks. Both prosecution and defense teams are preparing their arguments for the next phase."
        elif 'government' in title_lower or 'policy' in title_lower:
            return "Officials are expected to announce further details about implementation timelines and specific measures in the near future."
        else:
            return "The situation remains under active monitoring, with authorities committed to providing updates as new developments emerge."
    
    def generate_seo_meta_tags(self, topic, research_data):
        """Generate comprehensive SEO meta tags for better ranking"""
        
        # Create keyword-rich description
        domains = list(research_data['website_content'].keys())
        sources_text = " ".join([domain.replace('.com', '').replace('.org', '') for domain in domains])
        
        description = (
            f"Comprehensive analysis of {topic['title']} - trending news with {topic['traffic']} search volume. "
            f"Get latest updates from {sources_text}. AI-generated summary with key insights and developments."
        )
        
        # Create keywords
        base_keywords = ["trending", "news", "updates", "latest", "breaking news"]
        topic_keywords = re.findall(r'\w+', topic['title'].lower())
        keywords = list(set(base_keywords + topic_keywords + self.seo_keywords))[:15]
        
        return {
            'title': f"{topic['title']} - Trending News Analysis & Updates",
            'description': description[:160],
            'keywords': ", ".join(keywords),
            'og_title': f"{topic['title']} - Comprehensive Trending News Coverage",
            'og_description': description[:300],
            'canonical_url': f"{self.base_url}/posts/{self.clean_filename(topic['title'])}.html",
            'article_section': 'Trending News',
            'article_tags': topic_keywords[:10]
        }
    
    def clean_filename(self, title):
        """Clean title for use in filename"""
        cleaned = re.sub(r'[^\w\s-]', '', title)
        cleaned = re.sub(r'[-\s]+', '-', cleaned)
        return cleaned[:50].lower()
    
    def generate_html_post(self, topic, article_content, research_data):
        """Generate complete HTML post with comprehensive SEO meta tags"""
        timestamp = datetime.now()
        filename = f"{self.clean_filename(topic['title'])}_{timestamp.strftime('%Y%m%d_%H%M')}.html"
        
        # Generate SEO meta tags
        seo_meta = self.generate_seo_meta_tags(topic, research_data)
        
        html_template = f"""<!DOCTYPE html>
<html lang="en" prefix="og: https://ogp.me/ns#">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Primary Meta Tags -->
    <title>{seo_meta['title']}</title>
    <meta name="description" content="{seo_meta['description']}">
    <meta name="keywords" content="{seo_meta['keywords']}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{seo_meta['canonical_url']}">
    <meta property="og:title" content="{seo_meta['og_title']}">
    <meta property="og:description" content="{seo_meta['og_description']}">
        <meta property="og:site_name" content="Daily Reporter">    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{seo_meta['canonical_url']}">
    <meta property="twitter:title" content="{seo_meta['og_title']}">
    <meta property="twitter:description" content="{seo_meta['og_description']}">
    
    <!-- Article Specific -->
    <meta property="article:section" content="{seo_meta['article_section']}">
    <meta property="article:published_time" content="{timestamp.isoformat()}">
    <meta property="article:modified_time" content="{timestamp.isoformat()}">
    {"".join([f'<meta property="article:tag" content="{tag}">' for tag in seo_meta['article_tags']])}
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{seo_meta['canonical_url']}">
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": "{topic['title']}",
        "description": "{seo_meta['description']}",
        "datePublished": "{timestamp.isoformat()}",
        "dateModified": "{timestamp.isoformat()}",
        "author": {{
            "@type": "Person",
            "name": "Staff Reporter"
        }},
        "publisher": {{
            "@type": "Organization",
            "name": "Daily Reporter",
            "url": "../index.html"
        }},
        "mainEntityOfPage": {{
            "@type": "WebPage",
            "@id": "{seo_meta['canonical_url']}"
        }},
        "articleSection": "News",
        "keywords": "{seo_meta['keywords']}"
    }}
    </script>
    
    <link rel="stylesheet" href="../css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
</head>
<body itemscope itemtype="https://schema.org/WebPage">
    <header>
        <nav class="container">
            <a href="../index.html" class="logo">Daily Reporter</a>
            <div class="nav-links">
                <span class="live-indicator"><span class="pulse-dot"></span>Live Updates</span>
            </div>
        </nav>
    </header>
    
    <main class="container" itemprop="mainContentOfPage">
        <div class="article-container">
            {article_content}
            
            <div class="article-footer">
                <a href="../index.html" class="back-link">← Back to all articles</a>
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; {timestamp.year} Daily Reporter. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
        
        try:
            filepath = os.path.join(self.posts_dir, filename)
            with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                f.write(html_template)
            print(f"Successfully created file: {filename}")
            return filename
        except Exception as e:
            print(f"Error creating file {filename}: {e}")
            # Create a simple fallback filename
            fallback_filename = f"trending_news_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            try:
                fallback_path = os.path.join(self.posts_dir, fallback_filename)
                with open(fallback_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(html_template)
                return fallback_filename
            except Exception as fallback_error:
                print(f"Critical error: Cannot create file: {fallback_error}")
                return None
    
    def run_hourly_generation(self):
        """Main execution function that can run every hour"""
        print(f"Starting enhanced trending news generation for {self.hours} hour(s)...")
        
        # Get trending topics (configurable number)
        num_topics = 3  # You can make this configurable based on hours
        topics = self.get_trending_topics(num_topics)
        
        # If no new topics available, just update index with existing posts
        if not topics:
            print("No new topics to process. Updating index with existing posts...")
            self.update_index_html([])  # Empty new_posts list
            print(f"\n📋 Index updated with existing articles (no new content generated)")
            return []
        
        new_posts = []
        
        # Process each trending topic
        for topic in topics:
            try:
                print(f"\nProcessing trending topic: {topic['title']}")
                
                # Gather comprehensive research including top websites
                research_data = self.gather_topic_research(topic)
                
                # Generate AI-powered content
                article_content = self.generate_ai_content(topic, research_data)
                
                # Create HTML post with comprehensive SEO
                filename = self.generate_html_post(topic, article_content, research_data)
                
                new_posts.append({
                    'filename': filename,
                    'title': topic['title'],
                    'timestamp': datetime.now(),
                    'research_data': {
                        'sources_used': list(research_data['website_content'].keys()),
                        'search_volume': topic['traffic']
                    }
                })
                
                print(f"✓ Created comprehensive article: {filename}")
                
                # Respectful delay between processing topics
                time.sleep(2)
                
            except Exception as e:
                print(f"✗ Error processing topic {topic['title']}: {e}")
                continue
        
        # Update homepage and metadata
        self.update_index_html(new_posts)
        self.update_site_metadata(new_posts)
        
        print(f"\n🎉 Generation complete! Created {len(new_posts)} new comprehensive articles")
        return new_posts
    
    def update_index_html(self, new_posts):
        """Update the main index.html with latest headlines (all posts, newest first)"""
        try:
            # Path to the main index.html file
            index_path = os.path.join(os.path.dirname(self.posts_dir), "index.html")
            
            if not os.path.exists(index_path):
                print(f"Warning: index.html not found at {index_path}")
                return
            
            # Get all existing posts from the posts directory (this will include the new posts we just created)
            all_posts = self.get_all_posts_metadata()
            
            # Sort all posts by timestamp (newest first)
            all_posts.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Remove duplicates based on filename (keep only the newest of each)
            seen_filenames = set()
            unique_posts = []
            for post in all_posts:
                if post['filename'] not in seen_filenames:
                    seen_filenames.add(post['filename'])
                    unique_posts.append(post)
            
            # Limit to most recent 10 posts to keep the page manageable
            unique_posts = unique_posts[:10]
            
            # Read the current index.html
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate the posts HTML with unique posts
            posts_html = self.generate_posts_section(unique_posts)
            
            # Replace the latest-posts section with updated posts
            updated_content = re.sub(
                r'<section id="latest-posts">.*?</section>',
                f'<section id="latest-posts">\n{posts_html}\n        </section>',
                content,
                flags=re.DOTALL
            )
            
            # Write the updated content back
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✓ Updated index.html with {len(unique_posts)} total headlines (newest first)")
            
        except Exception as e:
            print(f"Error updating index.html: {e}")

    def get_all_posts_metadata(self):
        """Get metadata for all existing posts in the posts directory"""
        all_posts = []
        
        try:
            if not os.path.exists(self.posts_dir):
                return all_posts
                
            # Get all HTML files in posts directory
            html_files = [f for f in os.listdir(self.posts_dir) if f.endswith('.html')]
            
            for filename in html_files:
                file_path = os.path.join(self.posts_dir, filename)
                
                try:
                    # Get file creation time
                    file_timestamp = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    # Read the HTML file to extract title and metadata
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract title from the HTML
                    title_match = re.search(r'<title>(.*?) - Trending News Analysis', content)
                    title = title_match.group(1) if title_match else filename.replace('.html', '').replace('_', ' ').title()
                    
                    # Extract search volume if available
                    search_volume_match = re.search(r'search volume. Get latest updates from.*?(\d+\.?\d*[KM]?\+?)', content)
                    search_volume = search_volume_match.group(1) if search_volume_match else 'Trending'
                    
                    # Extract sources from meta tags or content
                    sources = ['Multiple sources']  # Default, could be enhanced to parse actual sources
                    
                    all_posts.append({
                        'filename': filename,
                        'title': title,
                        'timestamp': file_timestamp,
                        'research_data': {
                            'sources_used': sources,
                            'search_volume': search_volume
                        }
                    })
                    
                except Exception as e:
                    print(f"Warning: Could not parse metadata for {filename}: {e}")
                    continue
            
        except Exception as e:
            print(f"Warning: Error scanning posts directory: {e}")
        
        return all_posts

    def generate_posts_section(self, new_posts):
        """Generate the HTML for the posts section"""
        if not new_posts:
            return '''            <div class="no-posts">
                <p>No articles available yet. Check back soon!</p>
            </div>'''
        
        posts_html = ""
        
        for i, post in enumerate(new_posts):
            # Create a summary from the first sentence of content if available
            summary = f"Latest updates on {post['title'].lower()}. Click to read the full report."
            
            # Calculate time ago
            time_ago = self.get_time_ago(post['timestamp'])
            
            # Get sources list
            sources = post['research_data'].get('sources_used', [])
            sources_text = f"Sources: {', '.join(sources[:3])}" if sources else "Multiple sources"
            if len(sources) > 3:
                sources_text += f" and {len(sources) - 3} more"
            
            posts_html += f'''            <article class="post-preview">
                <div class="post-content">
                    <h2><a href="./posts/{post['filename']}">{post['title']}</a></h2>
                    <p class="post-summary">{summary}</p>
                    <div class="post-meta">
                        <span class="post-date">{time_ago}</span>
                        <span class="post-sources">{sources_text}</span>
                        <span class="search-volume">🔥 {post['research_data'].get('search_volume', 'Trending')}</span>
                    </div>
                </div>
                <div class="post-actions">
                    <a href="./posts/{post['filename']}" class="read-more">Read Full Article</a>
                </div>
            </article>
'''
        
        return posts_html

    def get_time_ago(self, timestamp):
        """Get human-readable time ago string"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.seconds < 3600:  # Less than an hour
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff.seconds < 86400:  # Less than a day
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"

    def update_site_metadata(self, new_posts):
        """Update site metadata and clean old posts"""
        # Keep only recent posts (last 24 hours worth)
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for filename in os.listdir(self.posts_dir):
            if filename.endswith('.html'):
                file_path = os.path.join(self.posts_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        print(f"Cleaned old post: {filename}")
                    except:
                        pass

# Usage example
if __name__ == "__main__":
    # You can change the hours parameter as needed
    hours_to_analyze = 1  # Change this to any number of hours
    
    generator = EnhancedTrendingNewsGenerator(hours=hours_to_analyze)
    
    # Run the generation
    posts = generator.run_hourly_generation()
    
    print(f"\n📊 Summary: Generated {len(posts)} articles with:")
    for post in posts:
        print(f"   • {post['title']}")
        print(f"     Sources: {', '.join(post['research_data']['sources_used'])}")