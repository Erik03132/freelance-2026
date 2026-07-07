"""
Task Prioritizer Microservice for ContentCombine
Exposes REST API for content scoring and prioritization
"""

from flask import Flask, request, jsonify
import sys
sys.path.insert(0, '/Users/igorvasin/freelance-2026/foundation/libraries/task-prioritizer')

from task_prioritizer import TaskPrioritizer, Trigger, Entity
from typing import Dict, List

app = Flask(__name__)
prioritizer = TaskPrioritizer()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'prioritizer'})

@app.route('/score', methods=['POST'])
def score():
    """
    Score content based on ContentCombine signals
    
    Request body:
    {
      "title": "Article title",
      "content": "Full content text",
      "tags": ["tag1", "tag2"],
      "source": "habr",
      "metadata": {}
    }
    
    Response:
    {
      "score": 75,
      "priority": "high",
      "signals": {
        "trigger_score": 20,
        "entity_score": 30,
        "combo_score": 15,
        "freshness_multiplier": 1.1
      }
    }
    """
    try:
        data = request.get_json()
        
        title = data.get('title', '')
        content = data.get('content', '')
        tags = data.get('tags', [])
        source = data.get('source', 'unknown')
        
        # Combine title and content for analysis
        full_text = f"{title} {content}".lower()
        
        # Calculate signals
        trigger_score = 0
        entity_score = 0
        combo_score = 0
        freshness_multiplier = 1.0
        
        # TRIGGER SIGNALS (0-25)
        trigger_keywords = {
            'bug': 5,
            'error': 5,
            'feature': 4,
            'tutorial': 3,
            'guide': 3,
            'fix': 5,
            'breaking': 6,
            'critical': 6,
            'security': 7,
            'vulnerability': 7,
        }
        
        for keyword, score in trigger_keywords.items():
            if keyword in full_text:
                trigger_score = max(trigger_score, score)
        
        # ENTITY SIGNALS (0-35)
        # S-tier (critical): 35
        # A-tier (high): 25
        # B-tier (medium): 15
        # C-tier (low): 5
        
        s_tier_keywords = ['production', 'critical', 'security', 'data loss', 'outage']
        a_tier_keywords = ['api', 'database', 'performance', 'optimization']
        b_tier_keywords = ['ui', 'ux', 'documentation', 'testing']
        c_tier_keywords = ['formatting', 'typo', 'comment']
        
        for keyword in s_tier_keywords:
            if keyword in full_text:
                entity_score = 35
                break
        
        if entity_score == 0:
            for keyword in a_tier_keywords:
                if keyword in full_text:
                    entity_score = 25
                    break
        
        if entity_score == 0:
            for keyword in b_tier_keywords:
                if keyword in full_text:
                    entity_score = 15
                    break
        
        if entity_score == 0:
            for keyword in c_tier_keywords:
                if keyword in full_text:
                    entity_score = 5
                    break
        
        # COMBO SIGNALS (0-20)
        # Multiple signals boost score
        signal_count = len([s for s in [trigger_score, entity_score] if s > 0])
        if signal_count >= 2:
            combo_score = 20
        elif signal_count >= 1:
            combo_score = 10
        
        # FRESHNESS MULTIPLIER (0.8-1.5)
        # Recent content gets boost
        freshness_multiplier = 1.1 if source == 'habr' else 1.0
        
        # TOTAL SCORE (0-100)
        base_score = trigger_score + entity_score + combo_score
        final_score = min(100, int(base_score * freshness_multiplier))
        
        # Determine priority
        if final_score >= 80:
            priority = 'critical'
        elif final_score >= 60:
            priority = 'high'
        elif final_score >= 40:
            priority = 'medium'
        else:
            priority = 'low'
        
        return jsonify({
            'status': 'success',
            'score': final_score,
            'priority': priority,
            'signals': {
                'trigger_score': trigger_score,
                'entity_score': entity_score,
                'combo_score': combo_score,
                'freshness_multiplier': freshness_multiplier,
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/score/batch', methods=['POST'])
def score_batch():
    """Score multiple items at once"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        results = []
        for item in items:
            # Call score endpoint logic
            title = item.get('title', '')
            content = item.get('content', '')
            tags = item.get('tags', [])
            source = item.get('source', 'unknown')
            
            # Same logic as /score
            full_text = f"{title} {content}".lower()
            
            trigger_score = 0
            entity_score = 0
            combo_score = 0
            freshness_multiplier = 1.0
            
            # ... (same scoring logic as above)
            trigger_keywords = {
                'bug': 5, 'error': 5, 'feature': 4, 'tutorial': 3,
                'guide': 3, 'fix': 5, 'breaking': 6, 'critical': 6,
                'security': 7, 'vulnerability': 7,
            }
            
            for keyword, score in trigger_keywords.items():
                if keyword in full_text:
                    trigger_score = max(trigger_score, score)
            
            s_tier_keywords = ['production', 'critical', 'security', 'data loss', 'outage']
            a_tier_keywords = ['api', 'database', 'performance', 'optimization']
            b_tier_keywords = ['ui', 'ux', 'documentation', 'testing']
            c_tier_keywords = ['formatting', 'typo', 'comment']
            
            for keyword in s_tier_keywords:
                if keyword in full_text:
                    entity_score = 35
                    break
            
            if entity_score == 0:
                for keyword in a_tier_keywords:
                    if keyword in full_text:
                        entity_score = 25
                        break
            
            if entity_score == 0:
                for keyword in b_tier_keywords:
                    if keyword in full_text:
                        entity_score = 15
                        break
            
            if entity_score == 0:
                for keyword in c_tier_keywords:
                    if keyword in full_text:
                        entity_score = 5
                        break
            
            signal_count = len([s for s in [trigger_score, entity_score] if s > 0])
            if signal_count >= 2:
                combo_score = 20
            elif signal_count >= 1:
                combo_score = 10
            
            freshness_multiplier = 1.1 if source == 'habr' else 1.0
            
            base_score = trigger_score + entity_score + combo_score
            final_score = min(100, int(base_score * freshness_multiplier))
            
            if final_score >= 80:
                priority = 'critical'
            elif final_score >= 60:
                priority = 'high'
            elif final_score >= 40:
                priority = 'medium'
            else:
                priority = 'low'
            
            results.append({
                'id': item.get('id', ''),
                'score': final_score,
                'priority': priority,
                'signals': {
                    'trigger_score': trigger_score,
                    'entity_score': entity_score,
                    'combo_score': combo_score,
                    'freshness_multiplier': freshness_multiplier,
                }
            })
        
        return jsonify({
            'status': 'success',
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("[prioritizer-service] Starting on http://localhost:8001")
    app.run(host='0.0.0.0', port=8001, debug=False)
