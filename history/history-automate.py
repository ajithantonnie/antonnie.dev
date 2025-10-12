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
    """Generate HTML page for today's date"""
    now = datetime.datetime.now(datetime.UTC)
    mm, dd = now.month, now.day
    date_str = now.strftime("%B %d")
    
    data = fetch_on_this_day(mm=mm, dd=dd)
    if not data:
        return None
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>History Timeline: What Happened on {date_str} | antonnie.dev</title>
    <meta name="description" content="Discover what happened on {date_str} in history. Explore {len(data.get('events', []))} historical events from ancient civilizations to modern times. Interactive timeline with detailed Wikipedia sources.">
    <meta name="keywords" content="history timeline, {date_str} in history, historical events, today in history, what happened on {date_str}, history facts, timeline events, world history">
    <meta name="author" content="antonnie.dev">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="https://antonnie.dev/history">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="History Timeline: What Happened on {date_str}">
    <meta property="og:description" content="Discover {len(data.get('events', []))} historical events that happened on {date_str}. From ancient civilizations to modern breakthroughs.">
    <meta property="og:url" content="https://antonnie.dev/history">
    <meta property="og:site_name" content="antonnie.dev">
    <meta property="og:image" content="https://antonnie.dev/history-timeline-preview.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="History Timeline: What Happened on {date_str}">
    <meta name="twitter:description" content="Discover {len(data.get('events', []))} historical events that happened on {date_str}">
    <meta name="twitter:image" content="https://antonnie.dev/history-timeline-preview.jpg">
    
    <!-- Structured Data for Rich Snippets -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "History Timeline: What Happened on {date_str}",
        "description": "Interactive timeline of historical events that happened on {date_str}",
        "url": "https://antonnie.dev/history",
        "datePublished": "{datetime.datetime.now(datetime.UTC).isoformat()}",
        "dateModified": "{datetime.datetime.now(datetime.UTC).isoformat()}",
        "author": {{
            "@type": "Person",
            "name": "antonnie.dev"
        }},
        "publisher": {{
            "@type": "Organization",
            "name": "antonnie.dev",
            "url": "https://antonnie.dev"
        }},
        "mainEntity": {{
            "@type": "Article",
            "headline": "Historical Events on {date_str}",
            "description": "Comprehensive timeline of """ + str(len(data.get('events', []))) + """ historical events that occurred on {date_str}",
            "datePublished": "{datetime.datetime.now(datetime.UTC).isoformat()}",
            "author": {{
                "@type": "Person",
                "name": "antonnie.dev"
            }}
        }},
        "breadcrumb": {{
            "@type": "BreadcrumbList",
            "itemListElement": [
                {{
                    "@type": "ListItem",
                    "position": 1,
                    "name": "antonnie.dev",
                    "item": "https://antonnie.dev"
                }},
                {{
                    "@type": "ListItem",
                    "position": 2,
                    "name": "History Timeline",
                    "item": "https://antonnie.dev/history"
                }}
            ]
        }}
    }}
    </script>
    
    <!-- Additional structured data for historical events -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Historical Events on {date_str}",
        "description": "Curated collection of significant historical events that occurred on {date_str}, sourced from Wikipedia",
        "url": "https://antonnie.dev/history",
        "keywords": ["history", "timeline", "historical events", "{date_str}", "world history", "today in history"],
        "creator": {{
            "@type": "Organization",
            "name": "antonnie.dev"
        }},
        "license": "https://creativecommons.org/licenses/by-sa/3.0/",
        "distribution": {{
            "@type": "DataDownload",
            "encodingFormat": "text/html"
        }}
    }}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --bg-primary: #0a0a0a;
            --bg-secondary: #111111;
            --bg-tertiary: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #a3a3a3;
            --text-muted: #525252;
            --accent-primary: #3b82f6;
            --accent-secondary: #8b5cf6;
            --accent-tertiary: #f59e0b;
            --accent-success: #10b981;
            --accent-error: #ef4444;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-muted: rgba(255, 255, 255, 0.12);
            --shadow-subtle: 0 1px 3px rgba(0, 0, 0, 0.2);
            --shadow-medium: 0 4px 12px rgba(0, 0, 0, 0.3);
            --shadow-large: 0 8px 32px rgba(0, 0, 0, 0.4);
            --glow-primary: 0 0 20px rgba(59, 130, 246, 0.3);
            --glow-secondary: 0 0 20px rgba(139, 92, 246, 0.3);
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-dark: linear-gradient(135deg, #1e3a8a 0%, #312e81 100%);
            --gradient-accent: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(245, 158, 11, 0.05) 0%, transparent 50%);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }}
        
        .visually-hidden {{
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
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
            pointer-events: none;
            z-index: -1;
        }}
        
        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: rgba(10, 10, 10, 0.8);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 1rem 0;
            transition: all 0.3s ease;
        }}
        
        .navbar.scrolled {{
            background: rgba(10, 10, 10, 0.95);
            box-shadow: var(--shadow-medium);
        }}
        
        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .nav-brand {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            background: var(--gradient-accent);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-decoration: none;
        }}
        
        .nav-menu {{
            display: flex;
            align-items: center;
            gap: 2rem;
            list-style: none;
        }}
        
        .nav-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .nav-link:hover {{
            color: var(--text-primary);
        }}
        
        .nav-link::after {{
            content: '';
            position: absolute;
            bottom: -4px;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--gradient-accent);
            transition: width 0.3s ease;
        }}
        
        .nav-link:hover::after {{
            width: 100%;
        }}
        

        
        .hero-section {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
            overflow: hidden;
            background: var(--gradient-dark);
            padding: 8rem 2rem 4rem;
        }}
        
        .hero-content {{
            max-width: 1000px;
            z-index: 2;
            position: relative;
        }}
        
        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-subtle);
            border-radius: 50px;
            padding: 0.5rem 1.5rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 2rem;
            animation: float 3s ease-in-out infinite;
        }}
        
        .hero-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(3rem, 8vw, 6rem);
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #ffffff 0%, #3b82f6 50%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 40px rgba(59, 130, 246, 0.3);
            animation: titleGlow 4s ease-in-out infinite alternate;
        }}
        
        .hero-subtitle {{
            font-size: clamp(1.1rem, 3vw, 1.4rem);
            color: var(--text-secondary);
            margin-bottom: 3rem;
            font-weight: 300;
            line-height: 1.7;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .cta-button {{
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            background: var(--gradient-accent);
            color: white;
            text-decoration: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: var(--glow-primary);
            position: relative;
            overflow: hidden;
        }}
        
        .cta-button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }}
        
        .cta-button:hover::before {{
            left: 100%;
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
        }}
        
        .stats-section {{
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-subtle);
            border-bottom: 1px solid var(--border-subtle);
            padding: 4rem 2rem;
        }}
        
        .stats-container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }}
        
        .stat-card {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border-subtle);
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: var(--gradient-accent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            border-color: var(--border-muted);
            box-shadow: var(--shadow-large);
        }}
        
        .stat-card:hover::before {{
            opacity: 1;
        }}
        
        .stat-icon {{
            font-size: 2rem;
            color: var(--accent-primary);
            margin-bottom: 1rem;
        }}
        
        .stat-number {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            background: var(--gradient-accent);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 0.9rem;
        }}
        
        .filters-section {{
            padding: 2rem;
        }}
        
        .filters-container {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        
        .filter-btn {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .filter-btn.active {{
            background: var(--gradient-accent);
            color: white;
            border-color: transparent;
            box-shadow: var(--glow-primary);
        }}
        
        .filter-btn:hover:not(.active) {{
            background: var(--bg-secondary);
            border-color: var(--border-muted);
            color: var(--text-primary);
        }}
        
        .timeline-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 4rem 2rem;
        }}
        
        .timeline {{
            position: relative;
            padding: 2rem 0;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 2px;
            height: 100%;
            background: linear-gradient(to bottom, 
                var(--accent-primary) 0%, 
                var(--accent-secondary) 50%, 
                var(--accent-tertiary) 100%);
            opacity: 0.3;
        }}
        
        .timeline-item {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 4rem 0;
            position: relative;
            opacity: 0;
            animation: fadeInUp 0.6s ease forwards;
            transition: all 0.2s ease;
        }}
        
        .timeline-content {{
            width: 45%;
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 1rem;
            padding: 2rem;
            position: relative;
            transition: all 0.4s ease;
            backdrop-filter: blur(10px);
        }}
        
        .timeline-content::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 3px;
            height: 100%;
            border-top-left-radius: 1rem;
            border-bottom-left-radius: 1rem;
        }}
        
        .timeline-content.left {{
            margin-right: auto;
            transform: translateX(-20px);
        }}
        
        .timeline-content.right {{
            margin-left: auto;
            transform: translateX(20px);
        }}
        
        .timeline-content:hover {{
            transform: translateY(-10px) scale(1.02);
            box-shadow: var(--shadow-large);
            border-color: var(--border-muted);
        }}
        
        .era-ancient .timeline-content::before {{ background: linear-gradient(to bottom, #8b5cf6, #a855f7); }}
        .era-medieval .timeline-content::before {{ background: linear-gradient(to bottom, #f59e0b, #f97316); }}
        .era-modern .timeline-content::before {{ background: linear-gradient(to bottom, #ef4444, #dc2626); }}
        .era-contemporary .timeline-content::before {{ background: linear-gradient(to bottom, #3b82f6, #2563eb); }}
        
        .year-badge {{
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-primary);
            border: 1px solid var(--border-muted);
            color: var(--text-primary);
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: var(--shadow-medium);
            backdrop-filter: blur(10px);
            z-index: 10;
        }}
        
        .event-text {{
            font-size: 1rem;
            line-height: 1.7;
            color: var(--text-secondary);
            margin-bottom: 1.5rem;
            font-weight: 400;
        }}
        
        .event-meta {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        .era-tag {{
            font-size: 0.75rem;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .era-ancient .era-tag {{
            background: rgba(139, 92, 246, 0.1);
            color: #a855f7;
            border: 1px solid rgba(139, 92, 246, 0.2);
        }}
        
        .era-medieval .era-tag {{
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }}
        
        .era-modern .era-tag {{
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }}
        
        .era-contemporary .era-tag {{
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        
        .event-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            padding: 0.75rem 1.25rem;
            border: 1px solid var(--border-subtle);
            border-radius: 50px;
            transition: all 0.3s ease;
            background: var(--bg-tertiary);
            font-size: 0.875rem;
        }}
        
        .event-link:hover {{
            background: var(--accent-primary);
            color: white;
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: var(--glow-primary);
        }}
        
        .footer {{
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-subtle);
            padding: 3rem 2rem 2rem;
            text-align: center;
        }}
        
        .footer-content {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .footer-text {{
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }}
        
        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .footer-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }}
        
        .footer-link:hover {{
            color: var(--accent-primary);
        }}
        
        .scroll-indicator {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--bg-secondary);
            z-index: 1001;
        }}
        
        .scroll-progress {{
            height: 100%;
            background: var(--gradient-accent);
            width: 0%;
            transition: width 0.1s ease;
        }}
        
        @keyframes titleGlow {{
            0% {{ text-shadow: 0 0 40px rgba(59, 130, 246, 0.3); }}
            100% {{ text-shadow: 0 0 60px rgba(139, 92, 246, 0.4), 0 0 80px rgba(59, 130, 246, 0.2); }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
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
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 0.4; }}
            50% {{ opacity: 0.8; }}
        }}
        
        .timeline-item:nth-child(odd) {{
            animation-delay: 0.1s;
        }}
        
        .timeline-item:nth-child(even) {{
            animation-delay: 0.2s;
        }}
        
        .loading-spinner {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid var(--border-subtle);
            border-radius: 50%;
            border-top-color: var(--accent-primary);
            animation: spin 1s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        @media (max-width: 1200px) {{
            .nav-container {{
                padding: 0 1.5rem;
            }}
            
            .timeline-container {{
                padding: 3rem 1.5rem;
            }}
        }}
        
        @media (max-width: 768px) {{
            .nav-menu {{
                display: none;
            }}
            
            .hero-section {{
                padding: 6rem 1rem 3rem;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}
            
            .filters-container {{
                gap: 0.5rem;
            }}
            
            .filter-btn {{
                padding: 0.5rem 1rem;
                font-size: 0.875rem;
            }}
            
            .timeline::before {{
                left: 2rem;
            }}
            
            .timeline-content {{
                width: calc(100% - 4rem);
                margin-left: 4rem !important;
                transform: none !important;
            }}
            
            .year-badge {{
                left: 2rem;
                transform: translateX(-50%);
            }}
            
            .timeline-item {{
                margin: 2rem 0;
            }}
        }}
        
        @media (max-width: 480px) {{
            .hero-section {{
                padding: 5rem 1rem 2rem;
            }}
            
            .stat-card {{
                padding: 1.5rem;
            }}
            
            .timeline-container {{
                padding: 2rem 1rem;
            }}
            
            .footer {{
                padding: 2rem 1rem 1rem;
            }}
            
            .footer-links {{
                flex-direction: column;
                gap: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="scroll-indicator">
        <div class="scroll-progress" id="scrollProgress"></div>
    </div>
    
    <nav class="navbar" id="navbar" role="navigation" aria-label="Main navigation">
        <div class="nav-container">
            <a href="https://antonnie.dev" class="nav-brand" aria-label="History Timeline - antonnie.dev homepage">
                <i class="fas fa-history" aria-hidden="true"></i> History Timeline
            </a>
            <ul class="nav-menu" role="menubar">
                <li role="none"><a href="#timeline" class="nav-link" role="menuitem">Timeline</a></li>
                <li role="none"><a href="#stats" class="nav-link" role="menuitem">Statistics</a></li>
            </ul>
        </div>
    </nav>
    
    <header class="hero-section">
        <div class="hero-content">
            <div class="hero-badge">
                <i class="fas fa-calendar-alt" aria-hidden="true"></i>
                Today in History
            </div>
            <h1 class="hero-title">What Happened on {date_str}? Journey Through Time</h1>
            <p class="hero-subtitle">
                Discover the {len(data.get('events', []))} remarkable events that shaped our world on {date_str}. 
                From ancient civilizations to modern breakthroughs, explore the pivotal moments that defined human history with detailed Wikipedia sources and interactive timeline navigation.
            </p>
            <a href="#timeline" class="cta-button" aria-label="Navigate to interactive timeline">
                <i class="fas fa-rocket" aria-hidden="true"></i>
                Explore Timeline
            </a>
        </div>
    </section>

    <section class="stats-section" id="stats">
        <div class="stats-container">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-scroll"></i>
                    </div>
                    <div class="stat-number" id="totalEvents">{len(data.get('events', []))}</div>
                    <div class="stat-label">Historical Events</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-history"></i>
                    </div>
                    <div class="stat-number" id="centuriesSpan">0</div>
                    <div class="stat-label">Centuries Span</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-calendar-check"></i>
                    </div>
                    <div class="stat-number">{datetime.datetime.now(datetime.UTC).year}</div>
                    <div class="stat-label">Current Year</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-globe"></i>
                    </div>
                    <div class="stat-number">∞</div>
                    <div class="stat-label">Possibilities</div>
                </div>
            </div>
            
            <div class="filters-section" role="region" aria-label="Timeline era filters">
                <div id="filter-description" class="visually-hidden">Filter historical events by time period: Ancient (up to 476 AD), Medieval (477-1491), Modern (1492-1944), or Contemporary (1945-present)</div>
                <div class="filters-container">
                    <button class="filter-btn active" data-era="all" aria-pressed="true" aria-describedby="filter-description">
                        <i class="fas fa-globe" aria-hidden="true"></i> All Eras
                    </button>
                    <button class="filter-btn" data-era="ancient" aria-pressed="false" aria-describedby="filter-description" title="Ancient Era: up to 476 AD">
                        <i class="fas fa-monument" aria-hidden="true"></i> Ancient
                    </button>
                    <button class="filter-btn" data-era="medieval" aria-pressed="false" aria-describedby="filter-description" title="Medieval Era: 477-1491 AD">
                        <i class="fas fa-chess-rook" aria-hidden="true"></i> Medieval
                    </button>
                    <button class="filter-btn" data-era="modern" aria-pressed="false" aria-describedby="filter-description" title="Modern Era: 1492-1944">
                        <i class="fas fa-industry" aria-hidden="true"></i> Modern
                    </button>
                    <button class="filter-btn" data-era="contemporary" aria-pressed="false" aria-describedby="filter-description" title="Contemporary Era: 1945-present">
                        <i class="fas fa-rocket"></i> Contemporary
                    </button>
                </div>
            </div>
        </div>
    </section>

    <main class="timeline-container" id="timeline" role="main">
        <div class="timeline" id="timelineContent" role="region" aria-label="Historical events timeline">
"""

    # Process and sort events from latest to oldest
    events = sorted(data.get("events", []), key=lambda x: int(x.get("year", 0)) if str(x.get("year", "0")).lstrip('-').isdigit() else 0, reverse=True)
    
    # Calculate centuries span
    if events:
        years = [abs(int(ev.get("year", 0))) for ev in events if str(ev.get("year", "0")).lstrip('-').isdigit()]
        if years:
            centuries_span = (max(years) - min(years)) // 100
        else:
            centuries_span = 0
    else:
        centuries_span = 0
    
    # Update the centuries span in the HTML
    html_content = html_content.replace('id="centuriesSpan">0', f'id="centuriesSpan">{centuries_span}')
    
    # Create timeline items
    for i, ev in enumerate(events):
        year = ev.get("year", "Unknown")
        text = ev.get("text", "No description available")
        
        # Get Wikipedia link
        wiki_link = "#"
        if ev.get("pages") and len(ev.get("pages")) > 0:
            content_urls = ev.get("pages")[0].get("content_urls", {})
            if content_urls.get("desktop"):
                wiki_link = content_urls.get("desktop").get("page", "#")
        
        # Determine era based on actual year value
        try:
            year_int = int(year) if str(year).lstrip('-').isdigit() else 2024
        except (ValueError, TypeError):
            year_int = 2024
            
        era_class = ""
        if year_int <= 476:  # Fall of Western Roman Empire
            era_class = "era-ancient"
            era_name = "ancient"
        elif year_int < 1492:  # Age of Discovery begins
            era_class = "era-medieval" 
            era_name = "medieval"
        elif year_int < 1945:  # End of WWII / Modern era
            era_class = "era-modern"
            era_name = "modern"
        else:
            era_class = "era-contemporary"
            era_name = "contemporary"
        
        # Alternate left/right positioning
        position_class = "left" if i % 2 == 0 else "right"
        
        html_content += f"""
            <article class="timeline-item {era_class}" data-era="{era_name}" style="animation-delay: {i * 0.1}s;" itemscope itemtype="https://schema.org/HistoricalEvent">
                <div class="year-badge">
                    <time datetime="{year}" itemprop="startDate">{year}</time>
                </div>
                <div class="timeline-content {position_class}">
                    <div class="event-meta">
                        <span class="era-tag" itemprop="temporal">{era_name.title()}</span>
                    </div>
                    <div class="event-text" itemprop="description">{text}</div>
                    {f'<a href="{wiki_link}" target="_blank" class="event-link" rel="noopener noreferrer" itemprop="url" aria-label="Learn more about this historical event on Wikipedia">' if wiki_link != "#" else '<span class="event-link disabled" aria-label="No additional information available">'}
                        <i class="fas fa-external-link-alt" aria-hidden="true"></i>
                        {'Learn More' if wiki_link != "#" else 'No Link Available'}
                    {'</a>' if wiki_link != "#" else '</span>'}
                </div>
            </div>
        """
    
    html_content += """
        </div>
    </div>

    </main>

    <footer class="footer" role="contentinfo">
        <div class="footer-content">
            <div class="footer-links">
                <a href="https://wikipedia.org" target="_blank" class="footer-link" rel="noopener noreferrer" aria-label="Visit Wikipedia">
                    <i class="fab fa-wikipedia-w" aria-hidden="true"></i> Wikipedia
                </a>
                <a href="https://antonnie.dev" target="_blank" class="footer-link" rel="noopener noreferrer" aria-label="Visit antonnie.dev">
                    <i class="fas fa-home" aria-hidden="true"></i> antonnie.dev
                </a>
                <a href="https://antonnie.dev/history" class="footer-link" aria-label="History Timeline home">
                    <i class="fas fa-history" aria-hidden="true"></i> Timeline
                </a>
            </div>
            <p class="footer-text">
                Historical data sourced from Wikipedia API • Last updated: """ + now.strftime("%Y-%m-%d %H:%M UTC") + """ • Showing """ + str(len(data.get('events', []))) + """ events
            </p>
            <p class="footer-text">
                <i class="fas fa-heart" style="color: #ef4444;" aria-hidden="true"></i> Discover history at <strong>antonnie.dev/history</strong>
            </p>
        </div>
    </footer>

    <script>
        // Scroll progress indicator
        function updateScrollProgress() {
            const scrollTop = window.pageYOffset;
            const docHeight = document.body.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            document.getElementById('scrollProgress').style.width = scrollPercent + '%';
        }
        
        // Navbar scroll effect
        function handleNavbarScroll() {
            const navbar = document.getElementById('navbar');
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
        
        // Smooth scrolling for navigation links
        function setupSmoothScroll() {
            const links = document.querySelectorAll('a[href^="#"]');
            links.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const target = document.querySelector(link.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        }

        // Fast era filtering without delays
        function setupEraFilter() {
            const filterBtns = document.querySelectorAll('.filter-btn');
            const timelineItems = document.querySelectorAll('.timeline-item');
            
            filterBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const era = btn.dataset.era;
                    
                    // Update active button
                    filterBtns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    
                    // Fast filtering without staggered delays
                    timelineItems.forEach(item => {
                        if (era === 'all' || item.dataset.era === era) {
                            item.style.display = 'flex';
                            item.style.opacity = '1';
                            item.style.transform = 'translateY(0)';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                });
            });
        }

        // Advanced timeline animations
        function animateTimeline() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, { 
                threshold: 0.1,
                rootMargin: '-50px'
            });
            
            document.querySelectorAll('.timeline-item').forEach((item, index) => {
                item.style.opacity = '0';
                item.style.transform = 'translateY(30px)';
                item.style.transition = `opacity 0.4s ease ${Math.min(index * 0.05, 1)}s, transform 0.4s ease ${Math.min(index * 0.05, 1)}s`;
                observer.observe(item);
            });
        }
        
        // Stats counter animation
        function animateStats() {
            const stats = document.querySelectorAll('.stat-number');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const target = entry.target;
                        const finalValue = target.textContent;
                        
                        if (!isNaN(finalValue) && finalValue !== '∞') {
                            const targetCount = parseInt(finalValue);
                            let currentCount = 0;
                            target.textContent = '0';
                            
                            const increment = Math.ceil(targetCount / 30);
                            const counter = setInterval(() => {
                                currentCount += increment;
                                if (currentCount >= targetCount) {
                                    currentCount = targetCount;
                                    clearInterval(counter);
                                }
                                target.textContent = currentCount;
                            }, 50);
                        }
                        
                        observer.unobserve(target);
                    }
                });
            }, { threshold: 0.5 });
            
            stats.forEach(stat => observer.observe(stat));
        }
        
        // Keyboard navigation
        function setupKeyboardNav() {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                    e.preventDefault();
                    const timelineItems = Array.from(document.querySelectorAll('.timeline-item[style*="flex"]'));
                    const currentIndex = timelineItems.findIndex(item => 
                        item.getBoundingClientRect().top > 0
                    );
                    
                    let targetIndex;
                    if (e.key === 'ArrowUp') {
                        targetIndex = Math.max(0, currentIndex - 1);
                    } else {
                        targetIndex = Math.min(timelineItems.length - 1, currentIndex + 1);
                    }
                    
                    if (timelineItems[targetIndex]) {
                        timelineItems[targetIndex].scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }
                }
            });
        }



        // Initialize everything when page loads
        document.addEventListener('DOMContentLoaded', function() {
            setupSmoothScroll();
            setupEraFilter();
            animateTimeline();
            animateStats();
            setupKeyboardNav();
            
            // Event listeners
            window.addEventListener('scroll', () => {
                updateScrollProgress();
                handleNavbarScroll();
            });
            
            // Initial calls
            updateScrollProgress();
            handleNavbarScroll();
            
            console.log('🚀 Chronos Timeline initialized successfully!');
        });
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
        print("💡 Use 'python history-automate.py --fetch-all' to build complete database later")
    
    # Clean up old cache periodically
    cleanup_old_cache()
    
    # Generate HTML page for today
    html_page = generate_html_page()
    if html_page:
        filename = "historical_timeline.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_page)
        
        print(f"✨ Timeline generated for today: {filename}")
        print("🎨 Features:")
        print("   • Cached data storage (JSON file)")
        print("   • Beautiful glass morphism design")
        print("   • Interactive timeline with animations")
        print("   • Era-based filtering system")
        print("   • Responsive mobile-friendly layout")
        print("   • Optimized loading and filtering")
        print("\n📖 Usage:")
        print("   python history-automate.py           # Generate for today")
        print("   python history-automate.py --stats   # Show cache statistics")
        print("   python history-automate.py --fetch-all  # Fetch all 366 dates")
    else:
        print("❌ Failed to fetch data from Wikipedia API")

if __name__ == "__main__":
    main()