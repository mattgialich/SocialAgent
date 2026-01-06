#!/usr/bin/env python3
"""
Demo script to show how the Social Agent works with sample data.
"""

# Sample articles about asteroid mining
sample_articles = [
    {
        'title': 'AstroForge Partners with NASA for Asteroid Mining Mission',
        'url': 'https://example.com/astroforge-nasa-partnership',
        'authors': ['Sarah Johnson'],
        'text': '''AstroForge, a leading asteroid mining company, has announced a groundbreaking partnership
        with NASA to demonstrate platinum-group metal extraction from near-Earth asteroids. The mission,
        scheduled for 2025, will test refining techniques in microgravity. This represents a major step
        forward in space resource utilization and could revolutionize access to rare metals. The company
        plans to target M-type asteroids rich in valuable metals like platinum, palladium, and rhodium,
        which are essential for clean energy technologies and electronics manufacturing.'''
    },
    {
        'title': 'Space Force Awards $50M Contract for Asteroid Defense System',
        'url': 'https://example.com/space-force-asteroid-defense',
        'authors': ['Michael Chen', 'Dr. Lisa Anderson'],
        'text': '''The U.S. Space Force has awarded a $50 million contract to develop advanced tracking and
        deflection systems for potentially hazardous asteroids. The defense contractor will build a network
        of space-based sensors and kinetic impactors capable of redirecting asteroids that pose a threat to
        Earth. This military application of asteroid technology demonstrates the growing importance of space
        security in national defense strategy. The system will integrate with existing early warning networks
        and provide real-time threat assessment capabilities.'''
    },
    {
        'title': 'Private Space Companies Race to Mine Asteroids for Rare Earth Elements',
        'url': 'https://example.com/asteroid-mining-race',
        'authors': ['Jennifer Williams'],
        'text': '''Several private space companies are competing to be the first to successfully mine asteroids
        for rare earth elements and precious metals. The commercial space race includes players like AstroForge,
        TransAstra, and Planetary Resources successor companies. Industry analysts predict the asteroid mining
        market could be worth trillions of dollars within the next two decades. These companies are developing
        innovative technologies for prospecting, extraction, and refining in the harsh environment of space,
        with potential applications for both Earth-based industries and future space settlements.'''
    }
]

print("="*80)
print("SOCIAL AGENT DEMO - Asteroid Mining Articles")
print("="*80)

print("\n📰 Sample Articles Found:")
print("-"*80)

for i, article in enumerate(sample_articles, 1):
    print(f"\n[{i}] {article['title']}")
    print(f"    URL: {article['url']}")
    print(f"    Authors: {', '.join(article['authors'])}")
    print(f"    Preview: {article['text'][:150]}...")

print("\n" + "="*80)
print("🤖 AI ANALYSIS (with Anthropic API key)")
print("="*80)

# Simulated analysis results
analyses = [
    {'article_num': 1, 'is_defense': False, 'confidence': 0.85,
     'reasoning': 'Focuses on commercial space mining and NASA partnership, not military/defense'},
    {'article_num': 2, 'is_defense': True, 'confidence': 0.95,
     'reasoning': 'Clearly military-focused: Space Force contract for asteroid defense system'},
    {'article_num': 3, 'is_defense': False, 'confidence': 0.90,
     'reasoning': 'Commercial space industry article about private companies and rare earth mining'}
]

for analysis in analyses:
    article = sample_articles[analysis['article_num'] - 1]
    print(f"\n[Article {analysis['article_num']}] {article['title'][:60]}...")
    print(f"  ✓ Defense-related: {'YES' if analysis['is_defense'] else 'NO'}")
    print(f"  ✓ Confidence: {analysis['confidence']:.0%}")
    print(f"  ✓ Reasoning: {analysis['reasoning']}")

print("\n" + "="*80)
print("📱 GENERATED SOCIAL MEDIA POSTS")
print("="*80)

# Sample generated posts
print("\n🐦 TWITTER POST (Article 2 - Defense-related):")
print("-"*80)
print("""Breaking: Space Force awards $50M for asteroid defense tech! 🛡️

Building on innovations like @AstroForge's asteroid mining work, military applications are expanding rapidly in space.

Read more: https://example.com/space-force-asteroid-defense
via @Michael_Chen @DrLisaAnderson

#SpaceDefense #AsteroidMining""")
print(f"({len('Breaking: Space Force awards $50M for asteroid defense tech! Building on innovations like @AstroForge')} chars)")

print("\n\n💼 LINKEDIN POST (Article 1 - Commercial/Non-defense):")
print("-"*80)
print("""Exciting news from the commercial space sector! AstroForge's partnership with NASA marks a pivotal moment for asteroid mining.

This collaboration builds on the broader vision of space resource utilization that companies like AstroForge have been pioneering. The focus on platinum-group metal extraction could transform both space exploration and terrestrial industries.

Key highlights:
• 2025 mission to test refining in microgravity
• Targeting M-type asteroids rich in rare metals
• Applications for clean energy & electronics

The convergence of private innovation and government support is accelerating our path to becoming a true spacefaring civilization. This isn't just about mining asteroids—it's about building the industrial infrastructure for humanity's future in space.

What implications do you see for Earth-based industries as space resources become economically viable?

Read the full story: https://example.com/astroforge-nasa-partnership
Credit: Sarah Johnson

#SpaceMining #AsteroidMining #CommercialSpace #CleanTech #Innovation""")

print("\n" + "="*80)
print("✨ NEXT STEPS")
print("="*80)
print("""
To run this for real with live articles:

1. Add your Anthropic API key to .env:
   ANTHROPIC_API_KEY=your_key_here

2. Run the full script:
   python main.py "asteroid mining"

3. Get real-time articles, AI analysis, and generated posts!
""")
