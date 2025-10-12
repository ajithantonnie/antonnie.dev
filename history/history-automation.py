import requests, datetime
import json
import os

# File to store cached events data
DATA_FILE = "on_this_day_data.json"

def load_cached_data():
    """Load cached events data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cached_data(data):
    """Save events data to JSON file"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def cleanup_old_cache():
    """Remove cached data only if it's extremely old (2+ years) to preserve historical data"""
    cached_data = load_cached_data()
    if not cached_data:
        return
    
    # Only remove data older than 2 years to preserve most historical data
    cutoff_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=730)  # 2 years
    cleaned_data = {}
    removed_count = 0
    
    for date_key, entry in cached_data.items():
        keep_entry = True
        
        if 'fetched_date' in entry:
            try:
                fetched_date = datetime.datetime.fromisoformat(entry['fetched_date'])
                if fetched_date < cutoff_date:
                    keep_entry = False
                    removed_count += 1
            except:
                # Keep entry if we can't parse the date
                pass
        
        if keep_entry:
            cleaned_data[date_key] = entry
    
    if removed_count > 0:
        save_cached_data(cleaned_data)
        print(f"🧹 Cleaned up {removed_count} entries older than 2 years")
        print(f"📊 Preserved {len(cleaned_data)} date entries in cache")
    else:
        print(f"📊 Cache contains {len(cached_data)} date entries (no cleanup needed)")

def fetch_on_this_day(lang="en", mm=None, dd=None, force_update=False):
    """Fetch events for a specific date, with smart caching that preserves all dates"""
    if mm is None or dd is None:
        now = datetime.datetime.now(datetime.UTC)
        mm = now.month
        dd = now.day
    
    date_key = f"{mm:02d}-{dd:02d}"
    
    # Load cached data
    cached_data = load_cached_data()
    
    # Check if we should update this date's data
    should_fetch_new = force_update
    
    if date_key in cached_data:
        if 'fetched_date' in cached_data[date_key]:
            try:
                fetched_date = datetime.datetime.fromisoformat(cached_data[date_key]['fetched_date'])
                current_time = datetime.datetime.now(datetime.UTC)
                
                # Check if data is from a previous year - if so, update it
                if fetched_date.year < current_time.year:
                    should_fetch_new = True
                    print(f"🔄 Updating {mm:02d}-{dd:02d} data from {fetched_date.year} to {current_time.year}")
                
                # If it's the same year, check if it's been more than 24 hours
                elif (current_time - fetched_date).total_seconds() > 86400:  # 24 hours
                    should_fetch_new = True
                    print(f"� Refreshing {mm:02d}-{dd:02d} data (last updated: {fetched_date.strftime('%Y-%m-%d %H:%M')})")
                
                else:
                    print(f"�📁 Using cached data for {mm:02d}-{dd:02d} (fetched: {fetched_date.strftime('%Y-%m-%d %H:%M')})")
                    return cached_data[date_key]['data']
            except:
                # If we can't parse the date, fetch new data
                should_fetch_new = True
        else:
            # No fetched_date field, update the data
            should_fetch_new = True
    else:
        # No cached data for this date
        should_fetch_new = True
    
    if should_fetch_new:
        # Fetch new data from API
        print(f"🌐 Fetching fresh data for {mm:02d}-{dd:02d}")
        url = f"https://api.wikimedia.org/feed/v1/wikipedia/{lang}/onthisday/all/{mm:02d}/{dd:02d}"
        resp = requests.get(url, headers={"User-Agent":"HistoryTimeline/2.0"})
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Update only this date's data (preserve all other dates)
            cached_data[date_key] = {
                'data': data,
                'fetched_date': datetime.datetime.now(datetime.UTC).isoformat(),
                'updated_from_year': cached_data.get(date_key, {}).get('fetched_date', 'new')
            }
            
            # Save updated cache (preserves all existing dates)
            if save_cached_data(cached_data):
                print(f"💾 Data updated for {mm:02d}-{dd:02d} (total cached dates: {len(cached_data)})")
            
            return data
        else:
            print(f"❌ API request failed with status: {resp.status_code}")
    
    # If API fails or we don't need to fetch, try to return cached data if available
    if date_key in cached_data:
        print(f"⚠️ Using cached data for {mm:02d}-{dd:02d}")
        return cached_data[date_key]['data']
    
    return None

def generate_html_page():
    """Generate a cutting-edge modern HTML page with advanced responsive design"""
    now = datetime.datetime.now(datetime.UTC)
    mm, dd = now.month, now.day
    date_str = now.strftime("%B %d")
    
    data = fetch_on_this_day(mm=mm, dd=dd)
    if not data:
        return None
    
    events = sorted(data.get("events", []), 
                   key=lambda x: int(x.get("year", 0)) if str(x.get("year", "0")).lstrip('-').isdigit() else 0, 
                   reverse=True)
    
    event_count = len(events)
    
    # SEO-optimized keywords and descriptions
    current_year = now.year
    month_name = now.strftime("%B")
    day_ordinal = now.strftime("%d").lstrip("0") + ("th" if 4 <= int(now.strftime("%d")) <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(int(now.strftime("%d")) % 10, "th"))
    
    # Generate rich keywords from events
    event_keywords = []
    for event in events[:10]:  # Top 10 events for keywords
        year = event.get("year", "")
        text = event.get("text", "")
        if year and text:
            # Extract key terms from event text
            words = text.lower().split()
            important_words = [w for w in words if len(w) > 4 and w not in ['that', 'this', 'with', 'from', 'were', 'when', 'what', 'they', 'have', 'been', 'said', 'will', 'would', 'could', 'should']][:3]
            if important_words:
                event_keywords.extend(important_words)
    
    unique_keywords = list(dict.fromkeys(event_keywords))[:15]  # Remove duplicates, keep top 15
    keywords_str = f"history, historical events, {date_str}, {month_name} {day_ordinal}, today in history, on this day, historical timeline, {current_year}, world history, historical facts, " + ", ".join(unique_keywords)
    
    # Create rich description
    historical_periods = []
    for event in events[:5]:
        year = event.get("year", "")
        if year and str(year).lstrip('-').isdigit():
            year_int = int(year)
            if year_int < 0:
                historical_periods.append("Ancient times")
            elif year_int < 500:
                historical_periods.append("Classical antiquity")
            elif year_int < 1500:
                historical_periods.append("Medieval period")
            elif year_int < 1800:
                historical_periods.append("Early modern era")
            elif year_int < 1900:
                historical_periods.append("19th century")
            elif year_int < 2000:
                historical_periods.append("20th century")
            else:
                historical_periods.append("Modern era")
    
    unique_periods = list(dict.fromkeys(historical_periods))
    periods_text = ", ".join(unique_periods[:3]) if unique_periods else "various historical periods"
    
    seo_description = f"Explore {event_count} fascinating historical events that occurred on {date_str} throughout history. Discover significant moments from {periods_text} that shaped our world. Updated daily with comprehensive historical timeline and detailed event information."
    
    # Canonical URL
    canonical_url = f"https://antonnie.dev/history/"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en" prefix="og: http://ogp.me/ns# article: http://ogp.me/ns/article#">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Primary SEO Meta Tags -->
    <title>Historical Events on {date_str} | Today in History | antonnie.dev</title>
    <meta name="title" content="Historical Events on {date_str} | Today in History | antonnie.dev">
    <meta name="description" content="{seo_description}">
    <meta name="keywords" content="{keywords_str}">
    <meta name="author" content="Antonnie">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="googlebot" content="index, follow">
    <meta name="bingbot" content="index, follow">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{canonical_url}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:title" content="Historical Events on {date_str} | Today in History">
    <meta property="og:description" content="{seo_description}">
    <meta property="og:image" content="https://antonnie.dev/history/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Historical Timeline for {date_str}">
    <meta property="og:site_name" content="antonnie.dev">
    <meta property="og:locale" content="en_US">
    <meta property="article:author" content="https://antonnie.dev">
    <meta property="article:published_time" content="{now.isoformat()}">
    <meta property="article:modified_time" content="{now.isoformat()}">
    <meta property="article:section" content="History">
    <meta property="article:tag" content="History">
    <meta property="article:tag" content="Timeline">
    <meta property="article:tag" content="{date_str}">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{canonical_url}">
    <meta name="twitter:title" content="Historical Events on {date_str} | Today in History">
    <meta name="twitter:description" content="{seo_description}">
    <meta name="twitter:image" content="https://antonnie.dev/history/twitter-card.png">
    <meta name="twitter:image:alt" content="Historical Timeline for {date_str}">
    <meta name="twitter:creator" content="@antonnie_dev">
    <meta name="twitter:site" content="@antonnie_dev">
    
    <!-- Additional SEO Meta -->
    <meta name="theme-color" content="#4f46e5">
    <meta name="msapplication-TileColor" content="#4f46e5">
    <meta name="application-name" content="Historia - Today in History">
    <meta name="apple-mobile-web-app-title" content="Historia">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    
    <!-- Language and geographic targeting -->
    <meta name="language" content="en">
    <meta name="geo.region" content="Global">
    <meta name="geo.placename" content="Worldwide">
    <meta name="coverage" content="Worldwide">
    <meta name="distribution" content="Global">
    <meta name="rating" content="General">
    <meta name="revisit-after" content="1 day">
    
    <!-- Verification tags for search engines -->
    <meta name="google-site-verification" content="">
    <meta name="msvalidate.01" content="">
    
    <!-- Social media optimization -->
    <meta property="fb:app_id" content="">
    <meta name="pinterest-rich-pin" content="true">
    
    <!-- Performance hints -->
    <meta http-equiv="x-dns-prefetch-control" content="on">
    <meta name="format-detection" content="telephone=no">
    
    <!-- Content security and cache control -->
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' https://api.wikimedia.org;">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
    <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
    
    <!-- Favicons -->
    <link rel="icon" type="image/x-icon" href="https://antonnie.dev/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="https://antonnie.dev/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="https://antonnie.dev/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="https://antonnie.dev/apple-touch-icon.png">
    <link rel="manifest" href="https://antonnie.dev/site.webmanifest">
    
    <!-- Performance optimizations -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://cdnjs.cloudflare.com">
    <link rel="dns-prefetch" href="https://wikipedia.org">
    <link rel="dns-prefetch" href="https://api.wikimedia.org">
    
    <!-- Critical CSS - fonts loaded with display=swap for better performance -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&display=swap" rel="stylesheet">
    
    <!-- Non-critical CSS loaded with media attribute to prevent render blocking -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"></noscript>
    
    <!-- JSON-LD Structured Data for Rich Snippets -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@graph": [
            {{
                "@type": "WebSite",
                "@id": "https://antonnie.dev/#website",
                "url": "https://antonnie.dev/",
                "name": "antonnie.dev",
                "description": "Personal website and portfolio of Antonnie - Full Stack Developer and History Enthusiast",
                "publisher": {{
                    "@id": "https://antonnie.dev/#person"
                }},
                "potentialAction": [
                    {{
                        "@type": "SearchAction",
                        "target": {{
                            "@type": "EntryPoint",
                            "urlTemplate": "https://antonnie.dev/search?q={{search_term_string}}"
                        }},
                        "query-input": "required name=search_term_string"
                    }}
                ]
            }},
            {{
                "@type": "WebPage",
                "@id": "{canonical_url}#webpage",
                "url": "{canonical_url}",
                "name": "Historical Events on {date_str} | Today in History",
                "isPartOf": {{
                    "@id": "https://antonnie.dev/#website"
                }},
                "about": {{
                    "@id": "{canonical_url}#article"
                }},
                "datePublished": "{now.isoformat()}",
                "dateModified": "{now.isoformat()}",
                "description": "{seo_description}",
                "breadcrumb": {{
                    "@id": "{canonical_url}#breadcrumb"
                }},
                "inLanguage": "en-US",
                "potentialAction": [
                    {{
                        "@type": "ReadAction",
                        "target": ["{canonical_url}"]
                    }}
                ]
            }},
            {{
                "@type": "Article",
                "@id": "{canonical_url}#article",
                "isPartOf": {{
                    "@id": "{canonical_url}#webpage"
                }},
                "author": {{
                    "@id": "https://antonnie.dev/#person"
                }},
                "headline": "Historical Events on {date_str} | Today in History",
                "datePublished": "{now.isoformat()}",
                "dateModified": "{now.isoformat()}",
                "mainEntityOfPage": {{
                    "@id": "{canonical_url}#webpage"
                }},
                "wordCount": "{event_count * 25}",
                "commentCount": 0,
                "publisher": {{
                    "@id": "https://antonnie.dev/#person"
                }},
                "image": {{
                    "@type": "ImageObject",
                    "@id": "https://antonnie.dev/history/og-image.png",
                    "url": "https://antonnie.dev/history/og-image.png",
                    "contentUrl": "https://antonnie.dev/history/og-image.png",
                    "width": 1200,
                    "height": 630,
                    "caption": "Historical Timeline for {date_str}"
                }},
                "keywords": "{keywords_str}",
                "articleSection": "History",
                "inLanguage": "en-US",
                "about": [
                    {{
                        "@type": "Thing",
                        "name": "History",
                        "description": "Historical events and timeline"
                    }},
                    {{
                        "@type": "Thing", 
                        "name": "{date_str}",
                        "description": "Historical events on {date_str}"
                    }}
                ]
            }},
            {{
                "@type": "Person",
                "@id": "https://antonnie.dev/#person",
                "name": "Antonnie",
                "url": "https://antonnie.dev/",
                "image": {{
                    "@type": "ImageObject",
                    "@id": "https://antonnie.dev/avatar.jpg",
                    "url": "https://antonnie.dev/avatar.jpg",
                    "caption": "Antonnie - Full Stack Developer"
                }},
                "description": "Full Stack Developer and History Enthusiast",
                "sameAs": [
                    "https://github.com/ajithantonnie",
                    "https://linkedin.com/in/antonnie"
                ]
            }},
            {{
                "@type": "BreadcrumbList",
                "@id": "{canonical_url}#breadcrumb",
                "itemListElement": [
                    {{
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": "https://antonnie.dev/"
                    }},
                    {{
                        "@type": "ListItem",
                        "position": 2,
                        "name": "History",
                        "item": "{canonical_url}"
                    }},
                    {{
                        "@type": "ListItem",
                        "position": 3,
                        "name": "{date_str}",
                        "item": "{canonical_url}"
                    }}
                ]
            }}
        ]
    }}
    </script>
    
    <style>
        :root {{
            /* Dark Mode Colors */
            --bg-primary: #0a0a0a;
            --bg-secondary: #111111;
            --bg-tertiary: #1a1a1a;
            --bg-glass: rgba(26, 26, 26, 0.8);
            --surface: #202020;
            --surface-elevated: #2a2a2a;
            
            /* Light accents on dark */
            --text-primary: #ffffff;
            --text-secondary: #a3a3a3;
            --text-muted: #737373;
            --text-inverse: #0a0a0a;
            
            /* Vibrant accent colors */
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-tertiary: #06b6d4;
            --accent-success: #10b981;
            --accent-warning: #f59e0b;
            --accent-error: #ef4444;
            
            /* Gradients */
            --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
            --gradient-secondary: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            --gradient-hero: linear-gradient(135deg, #0a0a0a 0%, #111111 50%, #1a1a1a 100%);
            --gradient-card: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            
            /* Borders and shadows */
            --border-primary: rgba(255, 255, 255, 0.1);
            --border-secondary: rgba(255, 255, 255, 0.05);
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -1px rgb(0 0 0 / 0.3);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.5), 0 4px 6px -2px rgb(0 0 0 / 0.4);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.6), 0 10px 10px -5px rgb(0 0 0 / 0.4);
            --shadow-neon: 0 0 20px rgba(99, 102, 241, 0.3);
            
            /* Animation speeds */
            --animation-fast: 0.15s;
            --animation-normal: 0.3s;
            --animation-slow: 0.5s;
            
            /* Spacing scale */
            --space-xs: 0.25rem;
            --space-sm: 0.5rem;
            --space-md: 1rem;
            --space-lg: 1.5rem;
            --space-xl: 2rem;
            --space-2xl: 3rem;
            --space-3xl: 4rem;
            
            /* Border radius scale */
            --radius-sm: 0.375rem;
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            --radius-2xl: 1.5rem;
            --radius-full: 9999px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        *::before,
        *::after {{
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
            font-size: 16px;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--bg-primary);
            overflow-x: hidden;
            min-height: 100vh;
            position: relative;
        }}

        /* Background effects */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 60%, rgba(6, 182, 212, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }}

        /* Container system */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 var(--space-xl);
        }}

        .container-sm {{
            max-width: 768px;
            margin: 0 auto;
            padding: 0 var(--space-xl);
        }}

        .container-lg {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 0 var(--space-xl);
        }}

        /* Header with glass morphism */
        .header {{
            position: sticky;
            top: 0;
            background: var(--bg-glass);
            backdrop-filter: blur(20px) saturate(180%);
            border-bottom: 1px solid var(--border-primary);
            z-index: 1000;
            padding: var(--space-lg) 0;
            transition: all var(--animation-normal) ease;
        }}

        .header.scrolled {{
            padding: var(--space-md) 0;
            box-shadow: var(--shadow-lg);
        }}

        .nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1.5rem, 3vw, 2rem);
            font-weight: 700;
            background: var(--gradient-primary);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-decoration: none;
            position: relative;
        }}

        .logo::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--gradient-primary);
            transition: width var(--animation-normal) ease;
        }}

        .logo:hover::after {{
            width: 100%;
        }}

        .nav-links {{
            display: flex;
            gap: var(--space-xl);
            align-items: center;
        }}

        .nav-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            padding: var(--space-sm) var(--space-md);
            border-radius: var(--radius-full);
            transition: all var(--animation-normal) ease;
            position: relative;
            overflow: hidden;
        }}

        .nav-link::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: var(--gradient-primary);
            opacity: 0.1;
            transition: left var(--animation-normal) ease;
        }}

        .nav-link:hover {{
            color: var(--text-primary);
            transform: translateY(-2px);
        }}

        .nav-link:hover::before {{
            left: 0;
        }}

        .mobile-menu-btn {{
            display: none;
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 1.5rem;
            cursor: pointer;
            padding: var(--space-sm);
            border-radius: var(--radius-md);
            transition: all var(--animation-normal) ease;
        }}

        .mobile-menu-btn:hover {{
            background: var(--surface);
            transform: scale(1.1);
        }}

        /* Hero section with animated background */
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
            background: var(--gradient-hero);
            overflow: hidden;
        }}

        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120" preserveAspectRatio="none"><path d="M1200,60C1100,20 1000,20 900,60C800,100 700,100 600,60C500,20 400,20 300,60C200,100 100,100 0,60V120H1200V60Z" fill="rgba(99,102,241,0.1)"/></svg>') repeat-x;
            background-size: 1200px 120px;
            animation: wave 10s linear infinite;
            pointer-events: none;
        }}

        @keyframes wave {{
            0% {{ background-position-x: 0; }}
            100% {{ background-position-x: 1200px; }}
        }}

        .hero-content {{
            position: relative;
            z-index: 2;
            max-width: 900px;
            margin: 0 auto;
            padding: var(--space-3xl) 0;
        }}

        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: var(--space-sm);
            background: var(--gradient-card);
            backdrop-filter: blur(10px);
            color: var(--text-primary);
            padding: var(--space-sm) var(--space-lg);
            border-radius: var(--radius-full);
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: var(--space-xl);
            border: 1px solid var(--border-primary);
            box-shadow: var(--shadow-md);
            animation: pulse 2s infinite;
        }}

        .hero-badge::before {{
            content: '🕰️';
            font-size: 1.2em;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.8; }}
        }}

        .hero-title {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(2.5rem, 8vw, 5rem);
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: var(--space-lg);
            background: var(--gradient-primary);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeInUp 1s ease-out;
        }}

        .hero-subtitle {{
            font-size: clamp(1.1rem, 3vw, 1.4rem);
            color: var(--text-secondary);
            margin-bottom: var(--space-3xl);
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            font-weight: 400;
            line-height: 1.6;
            animation: fadeInUp 1s ease-out 0.2s both;
        }}

        .cta-button {{
            display: inline-flex;
            align-items: center;
            gap: var(--space-sm);
            background: var(--gradient-primary);
            color: var(--text-inverse);
            padding: var(--space-md) var(--space-xl);
            border-radius: var(--radius-full);
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            box-shadow: var(--shadow-lg);
            transition: all var(--animation-normal) ease;
            margin-bottom: var(--space-3xl);
            animation: fadeInUp 1s ease-out 0.4s both;
        }}

        .cta-button:hover {{
            transform: translateY(-3px) scale(1.05);
            box-shadow: var(--shadow-xl), var(--shadow-neon);
        }}

        .cta-button::after {{
            content: '→';
            transition: transform var(--animation-normal) ease;
        }}

        .cta-button:hover::after {{
            transform: translateX(5px);
        }}

        /* Stats grid with glass cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--space-xl);
            margin-top: var(--space-3xl);
            animation: fadeInUp 1s ease-out 0.6s both;
        }}

        .stat-card {{
            background: var(--gradient-card);
            backdrop-filter: blur(15px);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-xl);
            padding: var(--space-xl);
            text-align: center;
            transition: all var(--animation-normal) ease;
            position: relative;
            overflow: hidden;
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-primary);
            transform: scaleX(0);
            transition: transform var(--animation-normal) ease;
        }}

        .stat-card:hover {{
            transform: translateY(-8px);
            box-shadow: var(--shadow-xl);
        }}

        .stat-card:hover::before {{
            transform: scaleX(1);
        }}

        .stat-number {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            background: var(--gradient-primary);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: block;
            margin-bottom: var(--space-sm);
            line-height: 1;
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        /* Timeline section */
        .timeline-section {{
            padding: var(--space-3xl) 0;
            position: relative;
        }}

        .section-header {{
            text-align: center;
            margin-bottom: var(--space-3xl);
        }}

        .section-title {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 700;
            margin-bottom: var(--space-lg);
            background: var(--gradient-primary);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .section-subtitle {{
            color: var(--text-secondary);
            font-size: clamp(1rem, 2.5vw, 1.25rem);
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.6;
        }}

        /* Advanced Timeline */
        .timeline {{
            position: relative;
            max-width: 1100px;
            margin: 0 auto;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            left: 3rem;
            top: 0;
            bottom: 0;
            width: 3px;
            background: var(--gradient-primary);
            border-radius: var(--radius-full);
            box-shadow: var(--shadow-neon);
        }}

        .timeline-item {{
            position: relative;
            padding-left: 6rem;
            margin-bottom: var(--space-3xl);
            opacity: 0;
            transform: translateX(50px);
            animation: slideInLeft 0.8s ease forwards;
        }}

        .timeline-item:nth-child(even) {{
            animation-delay: 0.1s;
        }}

        .timeline-item:nth-child(odd) {{
            animation-delay: 0.2s;
        }}

        @keyframes slideInLeft {{
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        .timeline-marker {{
            position: absolute;
            left: 2.1rem;
            top: 2rem;
            width: 1.8rem;
            height: 1.8rem;
            background: var(--gradient-primary);
            border: 4px solid var(--bg-primary);
            border-radius: 50%;
            z-index: 3;
            box-shadow: var(--shadow-neon);
        }}

        .timeline-content {{
            background: var(--gradient-card);
            backdrop-filter: blur(15px);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-xl);
            padding: var(--space-xl);
            box-shadow: var(--shadow-lg);
            transition: all var(--animation-normal) ease;
            position: relative;
            overflow: hidden;
        }}

        .timeline-content::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: var(--gradient-primary);
            opacity: 0;
            transition: opacity var(--animation-normal) ease;
        }}

        .timeline-content:hover {{
            transform: translateY(-5px) translateX(10px);
            box-shadow: var(--shadow-xl);
            border-color: rgba(99, 102, 241, 0.3);
        }}

        .timeline-content:hover::before {{
            opacity: 1;
        }}

        .timeline-year {{
            display: inline-flex;
            align-items: center;
            background: var(--gradient-primary);
            color: var(--text-inverse);
            padding: var(--space-sm) var(--space-lg);
            border-radius: var(--radius-full);
            font-size: 0.9rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: var(--space-lg);
            box-shadow: var(--shadow-md);
            gap: var(--space-md);
            flex-wrap: wrap;
        }}

        .era-badge {{
            background: rgba(255, 255, 255, 0.2);
            color: var(--text-inverse);
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-full);
            font-size: 0.8rem;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            white-space: nowrap;
        }}

        .timeline-title {{
            color: var(--text-primary);
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: var(--space-md);
            line-height: 1.4;
            font-family: 'Playfair Display', serif;
        }}

        .timeline-text {{
            color: var(--text-primary);
            font-size: 1.1rem;
            line-height: 1.7;
            margin-bottom: var(--space-lg);
            font-weight: 400;
        }}

        .timeline-footer {{
            margin-top: var(--space-md);
        }}

        .sr-only {{
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }}

        .copyright {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: var(--space-sm);
        }}

        .timeline-link {{
            display: inline-flex;
            align-items: center;
            gap: var(--space-sm);
            color: var(--accent-primary);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            padding: var(--space-sm) var(--space-md);
            border-radius: var(--radius-md);
            border: 1px solid transparent;
            transition: all var(--animation-normal) ease;
        }}

        .timeline-link:hover {{
            background: rgba(99, 102, 241, 0.1);
            border-color: var(--accent-primary);
            transform: translateX(5px);
        }}

        .timeline-link::after {{
            content: '↗';
            font-size: 1.1em;
            transition: transform var(--animation-normal) ease;
        }}

        .timeline-link:hover::after {{
            transform: translate(3px, -3px);
        }}

        /* Era Filter Buttons */
        .era-filters {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: var(--space-sm);
            margin: var(--space-2xl) 0;
            padding: var(--space-lg);
            background: var(--gradient-card);
            backdrop-filter: blur(15px);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-md);
        }}

        .era-filter-btn {{
            background: var(--surface);
            color: var(--text-secondary);
            border: 1px solid var(--border-primary);
            padding: var(--space-sm) var(--space-lg);
            border-radius: var(--radius-full);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all var(--animation-normal) ease;
            position: relative;
            overflow: hidden;
            white-space: nowrap;
        }}

        .era-filter-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: var(--gradient-primary);
            opacity: 0.1;
            transition: left var(--animation-normal) ease;
        }}

        .era-filter-btn:hover {{
            color: var(--text-primary);
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}

        .era-filter-btn:hover::before {{
            left: 0;
        }}

        .era-filter-btn.active {{
            background: var(--gradient-primary);
            color: var(--text-inverse);
            border-color: var(--accent-primary);
            box-shadow: var(--shadow-neon);
            transform: scale(1.05);
        }}

        .era-filter-btn.active::before {{
            display: none;
        }}

        .era-count {{
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 0.2rem 0.5rem;
            border-radius: var(--radius-full);
            font-size: 0.8rem;
            font-weight: 700;
            margin-left: var(--space-sm);
            min-width: 1.5rem;
            text-align: center;
            display: inline-block;
        }}

        .era-filter-btn.active .era-count {{
            background: rgba(255, 255, 255, 0.2);
            color: var(--text-inverse);
        }}

        /* Timeline item filtering */
        .timeline-item.hidden {{
            display: none;
        }}

        .timeline-item.fade-out {{
            opacity: 0;
            transform: translateX(50px);
            transition: all var(--animation-normal) ease;
        }}

        .timeline-item.fade-in {{
            opacity: 1;
            transform: translateX(0);
            transition: all var(--animation-normal) ease;
        }}

        /* Footer */
        .footer {{
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-primary);
            padding: var(--space-3xl) 0 var(--space-xl);
            margin-top: var(--space-3xl);
        }}

        .footer-content {{
            text-align: center;
        }}

        .footer-links {{
            display: flex;
            justify-content: center;
            gap: var(--space-xl);
            margin-bottom: var(--space-xl);
            flex-wrap: wrap;
        }}

        .footer-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            padding: var(--space-sm) var(--space-md);
            border-radius: var(--radius-md);
            transition: all var(--animation-normal) ease;
        }}

        .footer-link:hover {{
            color: var(--accent-primary);
            background: rgba(99, 102, 241, 0.1);
        }}

        .footer-text {{
            color: var(--text-muted);
            font-size: 0.9rem;
            line-height: 1.6;
        }}

        .footer-text strong {{
            color: var(--accent-primary);
            font-weight: 600;
        }}

        /* Animations */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* Loading spinner */
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(99, 102, 241, 0.3);
            border-radius: 50%;
            border-top-color: var(--accent-primary);
            animation: spin 1s ease-in-out infinite;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        /* Responsive Design */
        @media (max-width: 1024px) {{
            .container {{
                padding: 0 var(--space-lg);
            }}
            
            .timeline::before {{
                left: 2rem;
            }}
            
            .timeline-item {{
                padding-left: 4.5rem;
            }}
            
            .timeline-marker {{
                left: 1.1rem;
            }}
        }}

        @media (max-width: 768px) {{
            .nav-links {{
                display: none;
            }}
            
            .mobile-menu-btn {{
                display: block;
            }}
            
            .hero {{
                min-height: 90vh;
                padding: var(--space-xl) 0;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: var(--space-lg);
            }}
            
            .timeline::before {{
                left: 1.5rem;
            }}
            
            .timeline-item {{
                padding-left: 3.5rem;
                margin-bottom: var(--space-xl);
            }}
            
            .timeline-marker {{
                left: 0.6rem;
                width: 1.5rem;
                height: 1.5rem;
            }}
            
            .timeline-content {{
                padding: var(--space-lg);
            }}
            
            .footer-links {{
                flex-direction: column;
                gap: var(--space-md);
            }}
        }}

        @media (max-width: 480px) {{
            .container {{
                padding: 0 var(--space-md);
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
                gap: var(--space-md);
            }}
            
            .hero-content {{
                padding: var(--space-xl) 0;
            }}
        }}

        /* High contrast mode support */
        @media (prefers-contrast: high) {{
            :root {{
                --border-primary: rgba(255, 255, 255, 0.3);
                --text-secondary: #cccccc;
            }}
        }}

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {{
            *,
            *::before,
            *::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}

        /* Print styles */
        @media print {{
            .header,
            .footer {{
                display: none;
            }}
            
            .hero {{
                min-height: auto;
                padding: var(--space-lg) 0;
            }}
            
            .timeline-content {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <header class="header" id="header">
        <div class="container">
            <nav class="nav">
                <a href="javascript:window.location.reload()" class="logo">Historia</a>
                <div class="nav-links" id="navLinks">
                    <a href="#timeline" class="nav-link">Timeline</a>
                    <a href="#stats" class="nav-link">Statistics</a>
                </div>
                <button class="mobile-menu-btn" id="mobileMenuBtn" aria-label="Toggle mobile menu">
                    ☰
                </button>
            </nav>
        </div>
    </header>

    <main role="main">
        <section class="hero" id="hero" itemscope itemtype="https://schema.org/Article">
            <div class="container">
                <div class="hero-content">
                    <div class="hero-badge" role="banner">
                        <time datetime="{now.strftime('%Y-%m-%d')}">Today in History - {date_str}, {current_year}</time>
                    </div>
                    <h1 class="hero-title" itemprop="headline">Historical Events on {date_str}: {event_count} Remarkable Moments in History</h1>
                    <p class="hero-subtitle" itemprop="description">
                        Discover the fascinating historical events that occurred on {date_str} throughout history. Explore {event_count} significant moments from {periods_text} that shaped our world, from ancient civilizations to modern times. Updated daily with comprehensive details and historical context.
                    </p>
                    <nav role="navigation" aria-label="Page navigation">
                        <a href="#timeline" class="cta-button" aria-describedby="hero-description">
                            Explore Historical Timeline
                        </a>
                    </nav>
                    <p id="hero-description" class="sr-only">Navigate to the detailed historical timeline showing all {event_count} events that happened on {date_str}</p>
                
                <div class="stats-grid" id="stats">
                    <div class="stat-card">
                        <span class="stat-number" data-count="{event_count}">{event_count}</span>
                        <span class="stat-label">Historical Events</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number" id="centuriesSpan" data-count="0">0</span>
                        <span class="stat-label">Centuries Spanned</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number" data-count="{now.year}">{now.year}</span>
                        <span class="stat-label">Current Year</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

        <section class="timeline-section" id="timeline" itemscope itemtype="https://schema.org/ItemList">
            <div class="container">
                <header class="section-header">
                    <h2 class="section-title" itemprop="name">Complete Historical Timeline for {date_str}</h2>
                    <p class="section-subtitle" itemprop="description">
                        Explore the comprehensive chronological timeline of {event_count} significant historical events that occurred on {date_str}. From ancient civilizations to modern history, discover how this date has been pivotal throughout human civilization across multiple centuries and cultures.
                    </p>
                    <meta itemprop="numberOfItems" content="{event_count}">
                </header>

                <nav class="era-filters" id="eraFilters" role="navigation" aria-label="Filter events by historical era">
                    <button class="era-filter-btn active" data-era="all" aria-pressed="true" aria-describedby="filter-description">
                        All Events <span class="era-count" id="count-all">{event_count}</span>
                    </button>
                </nav>
                <p id="filter-description" class="sr-only">Filter historical events by time period to focus on specific eras</p>

                <div class="timeline" role="main" aria-label="Historical events timeline" itemscope itemtype="https://schema.org/ItemList">
"""

    # Calculate centuries span and era counts
    era_counts = {}
    if events:
        years = [abs(int(ev.get("year", 0))) for ev in events if str(ev.get("year", "0")).lstrip('-').isdigit()]
        if years:
            centuries_span = (max(years) - min(years)) // 100
        else:
            centuries_span = 0
        
        # Count events by era
        for event in events:
            year = event.get("year", "Unknown")
            try:
                year_int = int(year) if str(year).lstrip('-').isdigit() else 0
                if year_int < 0:
                    era = "BCE"
                elif year_int < 500:
                    era = "Ancient"
                elif year_int < 1500:
                    era = "Medieval"
                elif year_int < 1800:
                    era = "Early Modern"
                elif year_int < 1900:
                    era = "19th Century"
                elif year_int < 2000:
                    era = "20th Century"
                else:
                    era = "Modern"
            except:
                era = "Unknown"
            
            era_counts[era] = era_counts.get(era, 0) + 1
    else:
        centuries_span = 0

    # Update centuries span
    html_content = html_content.replace('id="centuriesSpan" data-count="0">0', f'id="centuriesSpan" data-count="{centuries_span}">{centuries_span}')
    
    # Generate era filter buttons
    era_buttons = ""
    era_order = ["Modern", "20th Century", "19th Century", "Early Modern", "Medieval", "Ancient", "BCE", "Unknown"]
    for era in era_order:
        if era in era_counts:
            era_buttons += f'''
                <button class="era-filter-btn" data-era="{era.lower().replace(' ', '-')}">
                    {era} <span class="era-count" id="count-{era.lower().replace(' ', '-')}">{era_counts[era]}</span>
                </button>'''
    
    # Add era buttons to HTML
    html_content = html_content.replace(
        '</button>\n                </nav>',
        f'</button>{era_buttons}\n                </nav>'
    )

    # Add timeline events with enhanced styling
    for i, event in enumerate(events):
        year = event.get("year", "Unknown")
        text = event.get("text", "No description available")
        
        # Get Wikipedia link
        wiki_link = "#"
        if event.get("pages") and len(event.get("pages")) > 0:
            content_urls = event.get("pages")[0].get("content_urls", {})
            if content_urls.get("desktop"):
                wiki_link = content_urls.get("desktop").get("page", "#")
        
        # Determine era for additional context
        era = ""
        try:
            year_int = int(year) if str(year).lstrip('-').isdigit() else 0
            if year_int < 0:
                era = "BCE"
            elif year_int < 500:
                era = "Ancient"
            elif year_int < 1500:
                era = "Medieval"
            elif year_int < 1800:
                era = "Early Modern"
            elif year_int < 1900:
                era = "19th Century"
            elif year_int < 2000:
                era = "20th Century"
            else:
                era = "Modern"
        except:
            era = "Unknown"
        
        era_class = era.lower().replace(' ', '-')
        
        # Extract event title from text (first sentence or up to 100 chars)
        event_title = text.split('.')[0][:100] + ("..." if len(text.split('.')[0]) > 100 else "")
        
        # Clean text for meta description
        clean_text = text.replace('"', '&quot;').replace("'", "&#39;")
        
        html_content += f"""
                <article class="timeline-item" data-era="{era_class}" style="animation-delay: {i * 0.05}s;" 
                         itemscope itemtype="https://schema.org/HistoricalEvent" itemprop="itemListElement">
                    <div class="timeline-marker" title="{era} Era" role="img" aria-label="Timeline marker for {era} era"></div>
                    <div class="timeline-content">
                        <header class="timeline-year">
                            <time datetime="{year}" itemprop="startDate">{year}</time> 
                            <span class="era-badge" itemprop="temporalCoverage">{era}</span>
                        </header>
                        <h3 class="timeline-title" itemprop="name">{event_title}</h3>
                        <p class="timeline-text" itemprop="description">{clean_text}</p>
                        <footer class="timeline-footer">
                            <a href="{wiki_link}" target="_blank" class="timeline-link" rel="noopener noreferrer" 
                               itemprop="url" aria-label="Read more about {event_title} on Wikipedia">
                                Read Full Article
                            </a>
                        </footer>
                        <meta itemprop="location" content="Global">
                        <meta itemprop="category" content="Historical Event">
                    </div>
                </article>
        """

    html_content += f"""
                </div>
            </div>
        </section>
    </main>

    <footer class="footer" role="contentinfo" itemscope itemtype="https://schema.org/WPFooter">
        <div class="container">
            <div class="footer-content">
                <nav class="footer-links" role="navigation" aria-label="Footer navigation">
                    <a href="https://wikipedia.org" target="_blank" class="footer-link" rel="noopener noreferrer" 
                       aria-label="Visit Wikipedia - Data source">Wikipedia API</a>
                    <a href="https://antonnie.dev" target="_blank" class="footer-link" rel="noopener noreferrer"
                       aria-label="Visit antonnie.dev homepage">antonnie.dev</a>
                    <a href="#hero" class="footer-link" aria-label="Return to top of page">Back to Top</a>
                </nav>
                <div class="footer-text" itemscope itemtype="https://schema.org/Organization">
                    <p>
                        <span itemprop="description">Historical data sourced from Wikipedia API</span> • 
                        Last updated: <time datetime="{now.isoformat()}">{now.strftime("%Y-%m-%d %H:%M UTC")}</time> •
                        <span itemprop="name">Historia by antonnie.dev</span>
                    </p>
                    <p>
                        Part of <strong><a href="https://antonnie.dev" itemprop="url">antonnie.dev</a></strong> - 
                        Exploring technology, history, and human stories through interactive experiences.
                    </p>
                    <p class="copyright">
                        © {current_year} antonnie.dev. Historical content via Wikipedia under Creative Commons licensing.
                    </p>
                </div>
            </div>
        </div>
    </footer>

    <script>
        // Enhanced JavaScript functionality
        document.addEventListener('DOMContentLoaded', function() {{
            // Header scroll effect
            const header = document.getElementById('header');
            let lastScrollTop = 0;
            
            window.addEventListener('scroll', function() {{
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > 100) {{
                    header.classList.add('scrolled');
                }} else {{
                    header.classList.remove('scrolled');
                }}
                
                lastScrollTop = scrollTop;
            }});

            // Mobile menu toggle
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            const navLinks = document.getElementById('navLinks');
            
            if (mobileMenuBtn && navLinks) {{
                mobileMenuBtn.addEventListener('click', function() {{
                    navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
                    navLinks.style.position = 'absolute';
                    navLinks.style.top = '100%';
                    navLinks.style.left = '0';
                    navLinks.style.right = '0';
                    navLinks.style.background = 'var(--bg-glass)';
                    navLinks.style.backdropFilter = 'blur(20px)';
                    navLinks.style.flexDirection = 'column';
                    navLinks.style.padding = 'var(--space-lg)';
                    navLinks.style.borderTop = '1px solid var(--border-primary)';
                }});
            }}

            // Smooth scrolling for anchor links
            document.querySelectorAll('a[href^="#"]').forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        const headerHeight = header.offsetHeight;
                        const targetPosition = target.offsetTop - headerHeight - 20;
                        
                        window.scrollTo({{
                            top: targetPosition,
                            behavior: 'smooth'
                        }});
                    }}
                }});
            }});

            // Intersection Observer for animations
            const observerOptions = {{
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            }};

            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateX(0)';
                    }}
                }});
            }}, observerOptions);

            // Observe timeline items
            document.querySelectorAll('.timeline-item').forEach(item => {{
                observer.observe(item);
            }});

            // Animated counters for stats
            function animateCounter(element, target) {{
                let current = 0;
                const increment = target / 60; // 60 frames for smooth animation
                const timer = setInterval(() => {{
                    current += increment;
                    if (current >= target) {{
                        current = target;
                        clearInterval(timer);
                    }}
                    element.textContent = Math.floor(current);
                }}, 16); // ~60fps
            }}

            // Trigger counter animations when stats come into view
            const statsObserver = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const statNumbers = entry.target.querySelectorAll('.stat-number');
                        statNumbers.forEach(stat => {{
                            const target = parseInt(stat.dataset.count);
                            if (target && !stat.classList.contains('animated')) {{
                                stat.classList.add('animated');
                                animateCounter(stat, target);
                            }}
                        }});
                        statsObserver.unobserve(entry.target);
                    }}
                }});
            }}, {{ threshold: 0.5 }});

            const statsGrid = document.getElementById('stats');
            if (statsGrid) {{
                statsObserver.observe(statsGrid);
            }}

            // Add loading states
            document.querySelectorAll('.timeline-link').forEach(link => {{
                link.addEventListener('click', function() {{
                    if (this.href !== '#') {{
                        const originalText = this.textContent;
                        this.innerHTML = '<span class="loading"></span> Loading...';
                        setTimeout(() => {{
                            this.textContent = originalText;
                        }}, 2000);
                    }}
                }});
            }});

            // Keyboard navigation
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'ArrowUp' && e.ctrlKey) {{
                    e.preventDefault();
                    window.scrollTo({{ top: 0, behavior: 'smooth' }});
                }}
                if (e.key === 'ArrowDown' && e.ctrlKey) {{
                    e.preventDefault();
                    window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
                }}
            }});

            // Era filtering functionality
            const eraFilterBtns = document.querySelectorAll('.era-filter-btn');
            const timelineItems = document.querySelectorAll('.timeline-item');
            
            eraFilterBtns.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const selectedEra = this.getAttribute('data-era');
                    
                    // Update active button
                    eraFilterBtns.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Filter timeline items with animation
                    timelineItems.forEach((item, index) => {{
                        const itemEra = item.getAttribute('data-era');
                        
                        if (selectedEra === 'all' || itemEra === selectedEra) {{
                            item.classList.remove('hidden', 'fade-out');
                            item.classList.add('fade-in');
                            item.style.animationDelay = `${{index * 0.05}}s`;
                        }} else {{
                            item.classList.add('fade-out');
                            setTimeout(() => {{
                                item.classList.add('hidden');
                                item.classList.remove('fade-out');
                            }}, 300);
                        }}
                    }});
                    
                    // Update URL hash for bookmarking
                    if (selectedEra !== 'all') {{
                        window.history.replaceState(null, null, `#era-${{selectedEra}}`);
                    }} else {{
                        window.history.replaceState(null, null, '#timeline');
                    }}
                    
                    // Scroll to timeline section
                    const timelineSection = document.getElementById('timeline');
                    if (timelineSection) {{
                        const headerHeight = header.offsetHeight;
                        const targetPosition = timelineSection.offsetTop - headerHeight - 20;
                        
                        window.scrollTo({{
                            top: targetPosition,
                            behavior: 'smooth'
                        }});
                    }}
                }});
            }});
            
            // Check URL hash on load for era filtering
            window.addEventListener('load', function() {{
                const hash = window.location.hash;
                if (hash.startsWith('#era-')) {{
                    const era = hash.replace('#era-', '');
                    const targetBtn = document.querySelector(`[data-era="${{era}}"]`);
                    if (targetBtn) {{
                        targetBtn.click();
                    }}
                }}
            }});

            // Performance monitoring
            if ('performance' in window) {{
                window.addEventListener('load', function() {{
                    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
                    console.log(`⚡ Historia loaded in ${{loadTime}}ms`);
                }});
            }}

            console.log('✨ Historia v2.0 - Modern Timeline Experience Loaded');
            console.log('🎨 Features: Glass morphism, Advanced animations, Responsive design, Accessibility');
            console.log('⚡ Performance: Optimized loading, Intersection observers, Smooth scrolling');
        }});

        // Service Worker for caching (optional)
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', function() {{
                // Register service worker for offline functionality
                console.log('🔧 Service Worker support detected');
            }});
        }}
    </script>
</body>
</html>
"""
    
    return html_content

def show_cache_stats():
    """Display cache statistics"""
    cached_data = load_cached_data()
    if not cached_data:
        print("📊 No cached data found")
        return
    
    current_year = datetime.datetime.now(datetime.UTC).year
    stats = {
        'current_year': 0,
        'previous_years': 0,
        'total_dates': len(cached_data),
        'initial_fetch': 0,
        'updated_entries': 0
    }
    
    year_counts = {}
    
    for date_key, entry in cached_data.items():
        if 'fetched_date' in entry:
            try:
                fetched_date = datetime.datetime.fromisoformat(entry['fetched_date'])
                year = fetched_date.year
                year_counts[year] = year_counts.get(year, 0) + 1
                
                if year == current_year:
                    stats['current_year'] += 1
                else:
                    stats['previous_years'] += 1
                    
                # Track initial fetch vs updates
                if entry.get('initial_fetch', False):
                    stats['initial_fetch'] += 1
                else:
                    stats['updated_entries'] += 1
                    
            except:
                pass
    
    completion_percentage = (stats['total_dates'] / 366) * 100
    
    print("📊 Cache Statistics:")
    print(f"   • Total dates cached: {stats['total_dates']}/366 ({completion_percentage:.1f}% complete)")
    print(f"   • Current year ({current_year}): {stats['current_year']} dates")
    print(f"   • Previous years: {stats['previous_years']} dates")
    print(f"   • Initial fetches: {stats['initial_fetch']} dates")
    print(f"   • Updated entries: {stats['updated_entries']} dates")
    
    if completion_percentage < 100:
        remaining = 366 - stats['total_dates']
        print(f"   • Remaining to fetch: {remaining} dates")
    
    if year_counts:
        print("   • By year:")
        for year in sorted(year_counts.keys(), reverse=True):
            print(f"     - {year}: {year_counts[year]} dates")
            
    # Show database size
    try:
        import os
        if os.path.exists(DATA_FILE):
            size_mb = os.path.getsize(DATA_FILE) / (1024 * 1024)
            print(f"   • Database size: {size_mb:.1f} MB")
    except:
        pass

def fetch_all_dates(retry_failed=True):
    """Fetch data for all 366 possible dates (including Feb 29) on first run"""
    import calendar
    import time
    
    print("🌐 Fetching data for all dates...")
    print("⏰ This will take a few minutes but creates a complete database...")
    
    cached_data = load_cached_data()
    total_dates = 0
    fetched_count = 0
    failed_dates = []
    
    # Days in each month (including leap year Feb 29)
    days_in_month = {
        1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    
    def fetch_single_date(month, day, attempt=1):
        """Fetch data for a single date with retry logic"""
        date_key = f"{month:02d}-{day:02d}"
        url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{month:02d}/{day:02d}"
        
        try:
            resp = requests.get(url, headers={"User-Agent":"HistoryTimeline/2.0"}, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                cached_data[date_key] = {
                    'data': data,
                    'fetched_date': datetime.datetime.now(datetime.UTC).isoformat(),
                    'initial_fetch': True,
                    'attempt': attempt
                }
                return True, "✅"
            else:
                return False, f"❌ (HTTP {resp.status_code})"
                
        except requests.exceptions.Timeout:
            return False, "❌ (Timeout)"
        except requests.exceptions.ConnectionError:
            return False, "❌ (Connection Error)"
        except Exception as e:
            error_msg = str(e)[:30].replace('\n', ' ')
            return False, f"❌ (Error: {error_msg}...)"
    
    # First pass: fetch all dates
    for month in range(1, 13):
        for day in range(1, days_in_month[month] + 1):
            date_key = f"{month:02d}-{day:02d}"
            total_dates += 1
            
            # Skip if already cached successfully
            if date_key in cached_data and 'data' in cached_data[date_key]:
                print(f"📅 {date_key}... ({total_dates}/366) 📁 (cached)")
                fetched_count += 1
                continue
            
            print(f"📅 Fetching {date_key}... ({total_dates}/366) ", end="")
            
            success, status = fetch_single_date(month, day)
            print(status)
            
            if success:
                fetched_count += 1
            else:
                failed_dates.append((month, day, status))
            
            # Save progress every 20 dates to prevent data loss
            if total_dates % 20 == 0:
                save_cached_data(cached_data)
                success_rate = (fetched_count / total_dates) * 100
                print(f"💾 Progress saved... ({fetched_count}/{total_dates} = {success_rate:.1f}% success)")
                
            # Small delay to be respectful to Wikipedia's servers
            time.sleep(0.3)
    
    # Retry failed dates if requested
    if retry_failed and failed_dates:
        print(f"\n🔄 Retrying {len(failed_dates)} failed dates...")
        retry_success = 0
        
        for month, day, original_error in failed_dates[:]:
            date_key = f"{month:02d}-{day:02d}"
            print(f"🔄 Retry {date_key}... ", end="")
            
            success, status = fetch_single_date(month, day, attempt=2)
            print(status)
            
            if success:
                retry_success += 1
                fetched_count += 1
                failed_dates.remove((month, day, original_error))
            
            time.sleep(0.5)  # Longer delay for retries
    
    # Final save
    if save_cached_data(cached_data):
        print(f"\n🎉 Complete! Successfully fetched {fetched_count}/{total_dates} dates")
        success_rate = (fetched_count / total_dates) * 100
        print(f"� Success rate: {success_rate:.1f}%")
        print(f"💾 Database saved to {DATA_FILE}")
        
        if failed_dates:
            print(f"\n⚠️  {len(failed_dates)} dates still failed:")
            for month, day, error in failed_dates[:10]:  # Show first 10 failures
                print(f"   • {month:02d}-{day:02d}: {error}")
            if len(failed_dates) > 10:
                print(f"   • ... and {len(failed_dates) - 10} more")
            print("💡 You can run --fetch-all again to retry failed dates")
        else:
            print("🎉 All dates fetched successfully!")
            
    else:
        print("❌ Failed to save database")

def is_first_run():
    """Check if this is the first run (no cache file or very few entries)"""
    cached_data = load_cached_data()
    # Consider it first run if we have fewer than 50 dates cached
    return len(cached_data) < 50

def generate_sitemap():
    """Generate XML sitemap for SEO"""
    now = datetime.datetime.now(datetime.UTC)
    sitemap_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
    
    <!-- Main history page -->
    <url>
        <loc>https://antonnie.dev/history/</loc>
        <lastmod>{now.strftime("%Y-%m-%d")}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
        <mobile:mobile/>
    </url>
    
    <!-- Today's specific date -->
    <url>
        <loc>https://antonnie.dev/history/#{now.strftime("%m-%d")}</loc>
        <lastmod>{now.strftime("%Y-%m-%d")}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
        <mobile:mobile/>
    </url>
    
</urlset>'''
    
    try:
        with open("sitemap.xml", "w", encoding="utf-8") as f:
            f.write(sitemap_content)
        print("🗺️ Generated sitemap.xml")
        return True
    except:
        print("❌ Failed to generate sitemap")
        return False

def generate_robots_txt():
    """Generate robots.txt for SEO"""
    robots_content = '''User-agent: *
Allow: /
Allow: /history/
Allow: /history/index.html
Allow: /history/sitemap.xml

# Crawl-delay for respectful crawling
Crawl-delay: 1

# Sitemap location
Sitemap: https://antonnie.dev/history/sitemap.xml
Sitemap: https://antonnie.dev/sitemap.xml

# Specific instructions for major search engines
User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: Bingbot
Allow: /
Crawl-delay: 1

User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /
'''
    
    try:
        with open("robots.txt", "w", encoding="utf-8") as f:
            f.write(robots_content)
        print("🤖 Generated robots.txt")
        return True
    except:
        print("❌ Failed to generate robots.txt")
        return False

def main():
    """Main function to handle command line arguments and generate timeline"""
    import sys
    
    # Parse command line arguments
    show_stats = False
    force_fetch_all = False
    
    for arg in sys.argv:
        if arg == "--stats":
            show_stats = True
        elif arg == "--fetch-all":
            force_fetch_all = True
    
    # Show cache stats if requested
    if show_stats:
        show_cache_stats()
        return
    
    # Force fetch all dates if requested
    if force_fetch_all:
        fetch_all_dates()
        return
    
    # Check if this is first run - just notify, don't ask
    if is_first_run():
        print("🔍 First run detected - fetching data for today only")
        print("💡 Use 'python ai-scrape.py --fetch-all' to build complete database later")
    
    # Clean up old cache periodically
    cleanup_old_cache()
    
    # Generate HTML page for today
    html_page = generate_html_page()
    if html_page:
        filename = "index.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_page)
        
        # Generate SEO files
        print("\n🔍 Generating SEO optimization files...")
        generate_sitemap()
        generate_robots_txt()
        
        print(f"\n✨ Timeline generated for today: {filename}")
        print("🎨 Features:")
        print("   • Comprehensive SEO optimization")
        print("   • Structured data (JSON-LD) for rich snippets")
        print("   • Semantic HTML5 with microdata")
        print("   • Open Graph and Twitter Card support")
        print("   • XML sitemap generation")
        print("   • Optimized meta tags and descriptions")
        print("   • Cached data storage (JSON file)")
        print("   • Beautiful glass morphism design")
        print("   • Interactive timeline with animations")
        print("   • Era-based filtering system")
        print("   • Responsive mobile-friendly layout")
        print("   • ARIA accessibility features")
        print("\n📖 Usage:")
        print("   python history-automation.py           # Generate for today")
        print("   python history-automation.py --stats   # Show cache statistics")
        print("   python history-automation.py --fetch-all  # Fetch all 366 dates")
        print("\n🚀 SEO Optimization Level: MAXIMUM")
        print("   • Title optimization with keywords")
        print("   • Rich meta descriptions")
        print("   • Structured data for search engines")
        print("   • Semantic HTML markup")
        print("   • Performance optimizations")
        print("   • Mobile-first responsive design")
    else:
        print("❌ Failed to fetch data from Wikipedia API")

if __name__ == "__main__":
    main()