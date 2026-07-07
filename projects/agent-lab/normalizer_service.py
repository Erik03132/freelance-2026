"""
Normalizer Microservice for ContentCombine
Exposes REST API for content normalization
"""

from flask import Flask, request, jsonify
from normalizer import Normalizer, NormalizedContent
from typing import Dict, List
import json

app = Flask(__name__)
normalizer = Normalizer()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'normalizer'})

@app.route('/normalize', methods=['POST'])
def normalize():
    """
    Normalize content from all sources
    
    Request body:
    {
      "config": {
        "habr": {"enabled": true},
        "medium": {"enabled": false, "usernames": []},
        "twitter": {"enabled": false, "bearer_token": "...", "query": "AI"},
        "telegram": {"enabled": false, "bot_token": "...", "channel_id": "..."}
      }
    }
    """
    try:
        data = request.get_json()
        config = data.get('config', {})
        
        # Normalize from all sources
        all_content = normalizer.normalize_all_sources(config)
        
        # Deduplicate
        unique_content = normalizer.deduplicate(all_content)
        
        # Convert to dict
        content_dicts = [item.to_dict() for item in unique_content]
        
        return jsonify({
            'status': 'success',
            'count': len(content_dicts),
            'content': content_dicts
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/normalize/habr', methods=['POST'])
def normalize_habr():
    """Normalize Habr content only"""
    try:
        content = normalizer.normalize_habr_html()
        content = normalizer.deduplicate(content)
        content_dicts = [item.to_dict() for item in content]
        
        return jsonify({
            'status': 'success',
            'source': 'habr',
            'count': len(content_dicts),
            'content': content_dicts
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/normalize/medium', methods=['POST'])
def normalize_medium():
    """Normalize Medium content"""
    try:
        data = request.get_json()
        usernames = data.get('usernames', [])
        
        all_content = []
        for username in usernames:
            content = normalizer.normalize_medium_rss(username)
            all_content.extend(content)
        
        unique_content = normalizer.deduplicate(all_content)
        content_dicts = [item.to_dict() for item in unique_content]
        
        return jsonify({
            'status': 'success',
            'source': 'medium',
            'count': len(content_dicts),
            'content': content_dicts
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/normalize/twitter', methods=['POST'])
def normalize_twitter():
    """Normalize Twitter content"""
    try:
        data = request.get_json()
        bearer_token = data.get('bearer_token')
        query = data.get('query', 'AI')
        
        if not bearer_token:
            return jsonify({
                'status': 'error',
                'message': 'bearer_token required'
            }), 400
        
        content = normalizer.normalize_twitter_api(query, bearer_token)
        unique_content = normalizer.deduplicate(content)
        content_dicts = [item.to_dict() for item in unique_content]
        
        return jsonify({
            'status': 'success',
            'source': 'twitter',
            'count': len(content_dicts),
            'content': content_dicts
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/normalize/telegram', methods=['POST'])
def normalize_telegram():
    """Normalize Telegram content"""
    try:
        data = request.get_json()
        bot_token = data.get('bot_token')
        channel_id = data.get('channel_id')
        
        if not bot_token or not channel_id:
            return jsonify({
                'status': 'error',
                'message': 'bot_token and channel_id required'
            }), 400
        
        content = normalizer.normalize_telegram_channel(channel_id, bot_token)
        unique_content = normalizer.deduplicate(content)
        content_dicts = [item.to_dict() for item in unique_content]
        
        return jsonify({
            'status': 'success',
            'source': 'telegram',
            'count': len(content_dicts),
            'content': content_dicts
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("[normalizer-service] Starting on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
