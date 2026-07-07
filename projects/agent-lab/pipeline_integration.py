"""
Integration script for ContentCombine pipeline
Connects all components: normalizer, prioritizer, telegram exporter

Usage:
  python3 pipeline_integration.py --config config.json
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import requests
import argparse

# Import local modules
from normalizer import Normalizer
from telegram_exporter import TelegramExporter

class ContentCombinePipeline:
    """Main integration class"""
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.normalizer = Normalizer()
        self.telegram_exporter = None
        
        if self.config.get('telegram_bot_token'):
            self.telegram_exporter = TelegramExporter(
                self.config['telegram_bot_token']
            )
    
    @staticmethod
    def load_config(config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def step1_fetch(self) -> List[Dict]:
        """Step 1: Fetch content from all sources"""
        print("\n[pipeline] STEP 1: Fetching content from all sources...")
        
        all_content = []
        
        # Fetch from all configured sources
        normalized_content = self.normalizer.normalize_all_sources(self.config)
        
        # Convert to dict
        content_dicts = [item.to_dict() for item in normalized_content]
        all_content.extend(content_dicts)
        
        print(f"[pipeline] Fetched {len(all_content)} items total")
        return all_content
    
    def step2_normalize(self, content: List[Dict]) -> List[Dict]:
        """Step 2: Normalize (already done by normalizer)"""
        print("\n[pipeline] STEP 2: Content already normalized")
        return content
    
    def step3_score(self, content: List[Dict]) -> List[Dict]:
        """Step 3: Score content using prioritizer service"""
        print("\n[pipeline] STEP 3: Scoring content...")
        
        scored_content = []
        
        for i, item in enumerate(content):
            try:
                # Score using inline scoring (no external service)
                score, priority, signals = self.score_item(item)
                
                item['score'] = score
                item['priority'] = priority
                item['signals'] = signals
                
                scored_content.append(item)
                
                if (i + 1) % 10 == 0:
                    print(f"[pipeline] Scored {i + 1}/{len(content)} items")
            
            except Exception as e:
                print(f"[pipeline] Error scoring item: {e}")
                # Add with default score
                item['score'] = 50
                item['priority'] = 'medium'
                item['signals'] = {
                    'trigger_score': 0,
                    'entity_score': 0,
                    'combo_score': 0,
                    'freshness_multiplier': 1.0
                }
                scored_content.append(item)
        
        # Sort by score
        scored_content.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"[pipeline] Scored {len(scored_content)} items")
        return scored_content
    
    @staticmethod
    def score_item(item: Dict) -> tuple:
        """Score single item"""
        title = item.get('title', '')
        content = item.get('content', '')
        source = item.get('source', 'unknown')
        
        full_text = f"{title} {content}".lower()
        
        # Trigger signals (0-25)
        trigger_score = 0
        trigger_keywords = {
            'bug': 5, 'error': 5, 'feature': 4, 'tutorial': 3,
            'guide': 3, 'fix': 5, 'breaking': 6, 'critical': 6,
            'security': 7, 'vulnerability': 7,
        }
        
        for keyword, score in trigger_keywords.items():
            if keyword in full_text:
                trigger_score = max(trigger_score, score)
        
        # Entity signals (0-35)
        entity_score = 0
        s_tier = ['production', 'critical', 'security', 'data loss', 'outage']
        a_tier = ['api', 'database', 'performance', 'optimization']
        b_tier = ['ui', 'ux', 'documentation', 'testing']
        c_tier = ['formatting', 'typo', 'comment']
        
        for keyword in s_tier:
            if keyword in full_text:
                entity_score = 35
                break
        
        if entity_score == 0:
            for keyword in a_tier:
                if keyword in full_text:
                    entity_score = 25
                    break
        
        if entity_score == 0:
            for keyword in b_tier:
                if keyword in full_text:
                    entity_score = 15
                    break
        
        if entity_score == 0:
            for keyword in c_tier:
                if keyword in full_text:
                    entity_score = 5
                    break
        
        # Combo signals (0-20)
        combo_score = 0
        signal_count = len([s for s in [trigger_score, entity_score] if s > 0])
        if signal_count >= 2:
            combo_score = 20
        elif signal_count >= 1:
            combo_score = 10
        
        # Freshness multiplier
        freshness_multiplier = 1.1 if source == 'habr' else 1.0
        
        # Total score
        base_score = trigger_score + entity_score + combo_score
        final_score = min(100, int(base_score * freshness_multiplier))
        
        # Priority
        if final_score >= 80:
            priority = 'critical'
        elif final_score >= 60:
            priority = 'high'
        elif final_score >= 40:
            priority = 'medium'
        else:
            priority = 'low'
        
        signals = {
            'trigger_score': trigger_score,
            'entity_score': entity_score,
            'combo_score': combo_score,
            'freshness_multiplier': freshness_multiplier,
        }
        
        return final_score, priority, signals
    
    def step4_deduplicate(self, content: List[Dict]) -> List[Dict]:
        """Step 4: Deduplicate"""
        print("\n[pipeline] STEP 4: Deduplicating...")
        
        seen = set()
        unique = []
        
        for item in content:
            content_hash = self.hash_content(item['title'] + item['content'])
            if content_hash not in seen:
                seen.add(content_hash)
                unique.append(item)
        
        print(f"[pipeline] Deduplicated: {len(content)} → {len(unique)}")
        return unique
    
    @staticmethod
    def hash_content(text: str) -> str:
        """Generate content hash"""
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def step5_cluster(self, content: List[Dict]) -> List[Dict]:
        """Step 5: Cluster by topic"""
        print("\n[pipeline] STEP 5: Clustering...")
        
        clusters = {}
        
        for item in content:
            tags = item.get('tags', [])
            primary_tag = tags[0] if tags else item.get('source', 'unknown')
            cluster_id = f"{item['source']}:{primary_tag}"
            
            if cluster_id not in clusters:
                clusters[cluster_id] = {
                    'cluster_id': cluster_id,
                    'topic': cluster_id,
                    'items': [],
                    'tags': set(),
                }
            
            clusters[cluster_id]['items'].append(item)
            clusters[cluster_id]['tags'].update(item.get('tags', []))
        
        # Convert to list and calculate avg_score
        clustered = []
        for cluster_data in clusters.values():
            items = cluster_data['items']
            avg_score = sum(item.get('score', 50) for item in items) / len(items)
            
            clustered.append({
                'cluster_id': cluster_data['cluster_id'],
                'topic': cluster_data['topic'],
                'items': items,
                'avg_score': avg_score,
                'tags': list(cluster_data['tags'])[:10],
            })
        
        # Sort by avg_score
        clustered.sort(key=lambda x: x['avg_score'], reverse=True)
        
        print(f"[pipeline] Created {len(clustered)} clusters")
        return clustered
    
    def step6_generate_outputs(
        self,
        content: List[Dict],
        clusters: List[Dict],
        min_score: int = 50
    ) -> Dict:
        """Step 6: Generate three outputs"""
        print("\n[pipeline] STEP 6: Generating outputs...")
        
        # Alerts: high priority
        alerts = [item for item in content if item.get('priority') in ['critical', 'high']]
        
        # Digest: all items above min_score
        digest = [item for item in content if item.get('score', 0) >= min_score]
        
        # Trending: clusters with high avg_score
        trending = [c for c in clusters if c.get('avg_score', 0) >= min_score]
        
        print(f"[pipeline] Generated: {len(alerts)} alerts, {len(digest)} digest, {len(trending)} trending")
        
        return {
            'alerts': alerts,
            'digest': digest,
            'trending': trending,
        }
    
    async def step7_export(self, outputs: Dict) -> int:
        """Step 7: Export to Telegram"""
        print("\n[pipeline] STEP 7: Exporting to Telegram...")
        
        if not self.telegram_exporter:
            print("[pipeline] Telegram exporter not configured")
            return 0
        
        chat_id = self.config.get('telegram_chat_id')
        if not chat_id:
            print("[pipeline] Telegram chat_id not configured")
            return 0
        
        # Calculate statistics
        all_items = outputs['digest']
        stats = {
            'total_items': len(all_items),
            'alerts_count': len(outputs['alerts']),
            'digest_count': len(outputs['digest']),
            'trending_count': len(outputs['trending']),
            'avg_score': sum(item.get('score', 0) for item in all_items) / len(all_items) if all_items else 0,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Export
        sent = await self.telegram_exporter.export_pipeline_results(
            chat_id,
            outputs['alerts'],
            outputs['digest'],
            outputs['trending'],
            stats
        )
        
        print(f"[pipeline] Sent {sent} messages to Telegram")
        return sent
    
    async def run(self):
        """Run full pipeline"""
        print("\n" + "="*60)
        print("ContentCombine Pipeline - Full Integration")
        print("="*60)
        
        try:
            # Step 1: Fetch
            content = self.step1_fetch()
            if not content:
                print("[pipeline] No content fetched")
                return
            
            # Step 2: Normalize (already done)
            content = self.step2_normalize(content)
            
            # Step 3: Score
            content = self.step3_score(content)
            
            # Step 4: Deduplicate
            content = self.step4_deduplicate(content)
            
            # Step 5: Cluster
            clusters = self.step5_cluster(content)
            
            # Step 6: Generate outputs
            outputs = self.step6_generate_outputs(
                content,
                clusters,
                min_score=self.config.get('min_score', 50)
            )
            
            # Step 7: Export
            await self.step7_export(outputs)
            
            print("\n" + "="*60)
            print("Pipeline completed successfully!")
            print("="*60 + "\n")
        
        except Exception as e:
            print(f"\n[pipeline] Error: {e}")
            import traceback
            traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description='ContentCombine Pipeline')
    parser.add_argument('--config', default='config.json', help='Config file path')
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)
    
    pipeline = ContentCombinePipeline(args.config)
    asyncio.run(pipeline.run())


if __name__ == '__main__':
    main()
