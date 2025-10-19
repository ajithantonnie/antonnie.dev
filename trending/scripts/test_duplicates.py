#!/usr/bin/env python3
"""
Test script to verify duplicate detection is working properly
"""
import sys
import os

# Add the script directory to the path so we can import the news generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_generator import EnhancedTrendingNewsGenerator

def test_normalize_title():
    """Test the normalize_title function with various duplicate scenarios"""
    generator = EnhancedTrendingNewsGenerator()
    
    test_cases = [
        ("Breaking: Major Tech Company Reports Strong Earnings", "major tech company reports strong earnings"),
        ("Update: Tech Company Reports Strong Earnings Today", "tech company reports strong earnings today"),
        ("Tech Company Reports Strong Q4 Earnings", "tech company reports strong q4 earnings"),
        ("BREAKING NEWS: Government Announces New Policy", "government announces new policy"),
        ("Government Announces New Policy Changes", "government announces new policy changes"),
        ("Live: Climate Summit Updates", "climate summit updates"),
        ("Trending: Climate Summit Latest News", "climate summit latest news"),
    ]
    
    print("Testing normalize_title function:")
    print("=" * 50)
    
    for original, expected in test_cases:
        normalized = generator.normalize_title(original)
        print(f"Original: {original}")
        print(f"Normalized: {normalized}")
        print(f"Expected: {expected}")
        print(f"Match: {'✓' if normalized == expected else '✗'}")
        print("-" * 30)

def test_duplicate_detection():
    """Test the get_trending_topics function with sample duplicate data"""
    generator = EnhancedTrendingNewsGenerator()
    
    # Create mock topics with duplicates
    mock_topics = [
        {'title': 'Breaking: Tech Companies Report Strong Earnings', 'traffic': '1M+', 'source': 'test1'},
        {'title': 'Update: Tech Companies Report Strong Q4 Earnings', 'traffic': '800K+', 'source': 'test2'},
        {'title': 'NASA Announces Mars Discovery', 'traffic': '600K+', 'source': 'test3'},
        {'title': 'Breaking: NASA Announces Major Mars Discovery', 'traffic': '500K+', 'source': 'test4'},
        {'title': 'Climate Policy Changes Announced', 'traffic': '400K+', 'source': 'test5'},
        {'title': 'New Climate Policy Announced at Summit', 'traffic': '300K+', 'source': 'test6'},
        {'title': 'Electric Vehicle Sales Surge', 'traffic': '200K+', 'source': 'test7'},
    ]
    
    print("Testing duplicate detection:")
    print("=" * 50)
    print("Original topics:")
    for i, topic in enumerate(mock_topics, 1):
        print(f"{i}. {topic['title']} (from {topic['source']})")
    
    # Test the deduplication logic
    seen_titles = set()
    unique_topics = []
    num_topics = 3
    
    for topic in mock_topics:
        clean_title = generator.normalize_title(topic['title'])
        if clean_title not in seen_titles and len(unique_topics) < num_topics:
            seen_titles.add(clean_title)
            unique_topics.append(topic)
    
    print(f"\nUnique topics (target: {num_topics}):")
    for i, topic in enumerate(unique_topics, 1):
        print(f"{i}. {topic['title']} (from {topic['source']})")
        print(f"   Normalized: {generator.normalize_title(topic['title'])}")
    
    print(f"\nResult: {len(unique_topics)} unique topics found")

if __name__ == "__main__":
    test_normalize_title()
    print("\n" + "=" * 70 + "\n")
    test_duplicate_detection()