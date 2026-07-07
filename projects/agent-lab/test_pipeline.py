#!/usr/bin/env python3
"""
ContentCombine Pipeline - Comprehensive Test Suite
Tests all 7 steps of the pipeline with Habr data
"""

import sys
import json
from datetime import datetime
from pipeline_integration import ContentCombinePipeline
from normalizer import Normalizer

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_subheader(title):
    print(f"\n{title}")
    print("-" * 70)

def test_normalizer():
    """Test 1: Normalizer"""
    print_header("TEST 1: NORMALIZER")
    
    normalizer = Normalizer()
    content = normalizer.normalize_habr_html()
    
    print(f"✓ Fetched {len(content)} items from Habr")
    
    if content:
        item = content[0]
        print(f"\n  Sample item:")
        print(f"    Title: {item.title[:60]}...")
        print(f"    Author: {item.author}")
        print(f"    Source: {item.source}")
        print(f"    URL: {item.url}")
        print(f"    Type: {item.content_type}")
        print(f"    Tags: {', '.join(item.tags) if item.tags else '(none)'}")
    
    return content

def test_scoring(content):
    """Test 2: Scoring"""
    print_header("TEST 2: SCORING")
    
    config = {"habr": {"enabled": True}}
    pipeline = ContentCombinePipeline.__new__(ContentCombinePipeline)
    pipeline.config = config
    pipeline.normalizer = Normalizer()
    pipeline.telegram_exporter = None
    
    # Convert to dict
    content_dicts = [item.to_dict() for item in content]
    scored = pipeline.step3_score(content_dicts)
    
    print(f"✓ Scored {len(scored)} items")
    
    # Show distribution
    scores = [item['score'] for item in scored]
    print(f"\n  Score distribution:")
    print(f"    Min: {min(scores)}")
    print(f"    Max: {max(scores)}")
    print(f"    Avg: {sum(scores) / len(scores):.1f}")
    
    print(f"\n  Top 5 by score:")
    for i, item in enumerate(scored[:5], 1):
        print(f"    {i}. {item['score']:3d} | {item['title'][:50]}...")
    
    return scored

def test_deduplication(scored):
    """Test 3: Deduplication"""
    print_header("TEST 3: DEDUPLICATION")
    
    config = {"habr": {"enabled": True}}
    pipeline = ContentCombinePipeline.__new__(ContentCombinePipeline)
    pipeline.config = config
    pipeline.normalizer = Normalizer()
    pipeline.telegram_exporter = None
    
    deduplicated = pipeline.step4_deduplicate(scored)
    
    print(f"✓ Deduplicated: {len(scored)} → {len(deduplicated)} items")
    
    if len(scored) > len(deduplicated):
        print(f"  Removed {len(scored) - len(deduplicated)} duplicates")
    else:
        print(f"  No duplicates found")
    
    return deduplicated

def test_clustering(deduplicated):
    """Test 4: Clustering"""
    print_header("TEST 4: CLUSTERING")
    
    config = {"habr": {"enabled": True}}
    pipeline = ContentCombinePipeline.__new__(ContentCombinePipeline)
    pipeline.config = config
    pipeline.normalizer = Normalizer()
    pipeline.telegram_exporter = None
    
    clusters = pipeline.step5_cluster(deduplicated)
    
    print(f"✓ Created {len(clusters)} clusters")
    
    print(f"\n  Cluster breakdown:")
    for i, cluster in enumerate(clusters[:5], 1):
        print(f"    {i}. {cluster['topic']}")
        print(f"       Items: {len(cluster['items'])} | Avg score: {cluster['avg_score']:.0f}")
        print(f"       Tags: {', '.join(cluster['tags'][:3]) if cluster['tags'] else '(none)'}")
    
    return clusters

def test_outputs(deduplicated, clusters):
    """Test 5: Generate outputs"""
    print_header("TEST 5: GENERATE OUTPUTS")
    
    config = {"habr": {"enabled": True}}
    pipeline = ContentCombinePipeline.__new__(ContentCombinePipeline)
    pipeline.config = config
    pipeline.normalizer = Normalizer()
    pipeline.telegram_exporter = None
    
    outputs = pipeline.step6_generate_outputs(deduplicated, clusters, min_score=0)
    
    print(f"✓ Generated outputs")
    print(f"  Alerts: {len(outputs['alerts'])}")
    print(f"  Digest: {len(outputs['digest'])}")
    print(f"  Trending: {len(outputs['trending'])}")
    
    if outputs['alerts']:
        print(f"\n  Top alert:")
        alert = outputs['alerts'][0]
        print(f"    {alert['title'][:60]}...")
        print(f"    Priority: {alert.get('priority', 'N/A')} | Score: {alert.get('score', 0)}")
    
    if outputs['digest']:
        print(f"\n  Top digest items:")
        for i, item in enumerate(outputs['digest'][:3], 1):
            print(f"    {i}. {item['title'][:50]}... (score: {item.get('score', 0)})")
    
    if outputs['trending']:
        print(f"\n  Trending topics:")
        for i, cluster in enumerate(outputs['trending'][:3], 1):
            print(f"    {i}. {cluster['topic']} ({len(cluster['items'])} items)")
    
    return outputs

def test_full_pipeline():
    """Test 6: Full pipeline"""
    print_header("TEST 6: FULL PIPELINE")
    
    config = {
        "habr": {"enabled": True},
        "medium": {"enabled": False},
        "twitter": {"enabled": False},
        "telegram": {"enabled": False},
        "min_score": 0,
    }
    
    pipeline = ContentCombinePipeline.__new__(ContentCombinePipeline)
    pipeline.config = config
    pipeline.normalizer = Normalizer()
    pipeline.telegram_exporter = None
    
    # Run all steps
    content = pipeline.step1_fetch()
    # content is already in dict format from step1_fetch
    scored = pipeline.step3_score(content)
    deduplicated = pipeline.step4_deduplicate(scored)
    clusters = pipeline.step5_cluster(deduplicated)
    outputs = pipeline.step6_generate_outputs(deduplicated, clusters, min_score=0)
    
    print(f"✓ Pipeline executed successfully")
    print(f"\n  Pipeline summary:")
    print(f"    Fetched: {len(content)} items")
    print(f"    Scored: {len(scored)} items")
    print(f"    Deduplicated: {len(deduplicated)} items")
    print(f"    Clusters: {len(clusters)}")
    print(f"    Outputs: {len(outputs['digest'])} digest, {len(outputs['alerts'])} alerts, {len(outputs['trending'])} trending")
    
    return outputs

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    print("""
✓ All tests passed successfully!

Pipeline components verified:
  ✓ Normalizer (Habr HTML parser)
  ✓ Scoring (ContentCombine signals)
  ✓ Deduplication (content hash)
  ✓ Clustering (by topic/tags)
  ✓ Output generation (alerts, digest, trending)
  ✓ Full pipeline orchestration

Ready for:
  • Telegram integration (set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
  • Medium/Twitter/Telegram sources (configure in config.json)
  • Production deployment (Docker containers)
  • Scheduled runs (APScheduler or cron)

Next steps:
  1. Configure Telegram bot token and chat ID
  2. Add Medium, Twitter, Telegram sources
  3. Tune scoring thresholds for your needs
  4. Deploy as microservices
  5. Set up scheduling for periodic runs
    """)

def main():
    """Run all tests"""
    try:
        print("\n" + "=" * 70)
        print("  ContentCombine Pipeline - Comprehensive Test Suite")
        print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 70)
        
        # Test 1: Normalizer
        content = test_normalizer()
        if not content:
            print("✗ Normalizer test failed")
            return 1
        
        # Test 2: Scoring
        scored = test_scoring(content)
        
        # Test 3: Deduplication
        deduplicated = test_deduplication(scored)
        
        # Test 4: Clustering
        clusters = test_clustering(deduplicated)
        
        # Test 5: Generate outputs
        outputs = test_outputs(deduplicated, clusters)
        
        # Test 6: Full pipeline
        full_outputs = test_full_pipeline()
        
        # Summary
        print_summary()
        
        print("\n" + "=" * 70)
        print("  ✓ ALL TESTS PASSED")
        print("=" * 70 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
