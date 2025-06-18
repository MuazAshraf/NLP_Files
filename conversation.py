from flask import Flask, request, jsonify, render_template, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Conversation(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversation.id'))
    content = db.Column(db.Text)
    is_user = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return redirect('/chat')

@app.route('/chat')
def chat():
    conversations = db.session.execute(db.select(Conversation).order_by(Conversation.created_at.desc())).scalars().all()
    return render_template('chat.html', conversations=conversations)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/conversations', methods=['GET', 'POST'])
def get_conversations():
    if request.method == 'GET':
        conversations = db.session.execute(
            db.select(Conversation)
            .order_by(Conversation.created_at.desc())
        ).scalars().all()
        return jsonify([{
            'id': conv.id,
            'title': conv.title,
            'created_at': conv.created_at.isoformat()
        } for conv in conversations])
    elif request.method == 'POST':
        conv_id = str(uuid.uuid4())
        new_conv = Conversation(id=conv_id, title="New Chat")
        db.session.add(new_conv)
        db.session.commit()
        return jsonify({
            'id': conv_id,
            'title': new_conv.title,
            'created_at': new_conv.created_at.isoformat()
        }), 201

@app.route('/api/conversations/<conv_id>', methods=['GET'])
def get_conversation(conv_id):
    messages = db.session.execute(
        db.select(Message)
        .filter_by(conversation_id=conv_id)
        .order_by(Message.timestamp)
    ).scalars().all()
    return jsonify([{
        'content': msg.content,
        'is_user': msg.is_user,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages])

@app.route('/api/conversations/<conv_id>/messages', methods=['POST'])
def add_message(conv_id):
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Invalid request data'}), 400
            
        # Add user message
        user_message = Message(
            conversation_id=conv_id,
            content=data['content'],
            is_user=True
        )
        db.session.add(user_message)
        
        # Update conversation title if first message
        if db.session.execute(
            db.select(db.func.count())
            .select_from(Message)
            .filter_by(conversation_id=conv_id)
        ).scalar() == 1:
            conv = db.session.get(Conversation, conv_id)
            conv.title = data['content'][:50] + ('...' if len(data['content']) > 50 else '')
            db.session.add(conv)
        
        # Generate bot response
        bot_message = Message(
            conversation_id=conv_id,
            content=f"Received your message: {data['content']}",
            is_user=False
        )
        db.session.add(bot_message)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': {
                'content': bot_message.content,
                'is_user': bot_message.is_user,
                'timestamp': bot_message.timestamp.isoformat()
            }
        }), 201
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/api/conversations/<conv_id>', methods=['DELETE'])
def delete_conversation(conv_id):
    try:
        # Delete all messages first
        Message.query.filter_by(conversation_id=conv_id).delete()
        # Then delete the conversation
        Conversation.query.filter_by(id=conv_id).delete()
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conv_id>/title', methods=['PUT'])
def update_conversation_title(conv_id):
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title required'}), 400
        
        conv = db.session.get(Conversation, conv_id)
        if not conv:
            return jsonify({'error': 'Conversation not found'}), 404
            
        conv.title = data['title'][:100]  # Limit to 100 chars
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)