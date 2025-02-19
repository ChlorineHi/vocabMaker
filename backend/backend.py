from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from google import genai
import json
import logging
import traceback

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 更新CORS配置
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],  # 添加IP地址
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

client = genai.Client(api_key="AIzaSyAPho0iby74AjaMjcweHZn8Wh4a7HAx87g")

@app.route('/api/generate', methods=['POST'])
def generate_content():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        logger.info(f"Received prompt: {prompt}")
        
        def generate():
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                
                if hasattr(response, 'text'):
                    yield f"data: {json.dumps({'text': response.text})}\n\n"
                    logger.debug(f"Generated content: {response.text[:100]}...")
                else:
                    yield f"data: {json.dumps({'error': 'No response text generated'})}\n\n"
                        
            except Exception as e:
                error_msg = f"Generation error: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream'
        )
        
    except Exception as e:
        error_msg = f"API error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')