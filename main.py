import uuid
import time
import json
import logging
from .typegpt import TypeGPT
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Logger Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log')
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

@app.route('/chat/completions', methods=['POST'])
def chat_completion():
    try:
        # Parse input JSON
        data = request.get_json()
        if not data or 'messages' not in data or 'model' not in data:
            return jsonify({"error": "Invalid request, 'messages' and 'model' fields are required"}), 400

        messages = data['messages']
        model = data['model']
        
        # Ensure messages are in the correct format
        chat = []
        for msg in messages:
            if msg['role'] in {"system", "user", "assistant"}:
                if isinstance(msg['content'], list):  # Handle list format content
                    msg['content'] = ''.join([x['text'] for x in msg['content'] if 'text' in x])
                chat.append(msg)

        # Check if TypeGPT is being used
        if model.startswith("typegpt*"):
            model_name = model.split("*", 1)[1]  # Extract actual model name
            generator = TypeGPT()
        else:
            return jsonify({"error": "Unsupported model"}), 400

        def generate():
            response_id = f"chatcmpl-{uuid.uuid4()}"
            created_at = int(time.time())

            # Stream responses chunk-by-chunk
            for chunk in generator.generate(chat, model_name):
                yield "data: " + json.dumps({
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created_at,
                    "model": model,
                    "choices": [{"index": 0, "delta": {"content": chunk, "role": "assistant"}, "finish_reason": None}],
                    "usage": None
                }) + "\n\n"

            # Send final stop chunk
            yield "data: "+json.dumps({
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created_at,
                "model": model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                "usage": None
            }) + "\n\n"
            try:
                if(data['stream_options']['include_usage'] == True):
                    yield "data: "+json.dumps({
                        "id":"chatcmpl-AyFpzQflrrKQcxcrdimjQgU3HhnCN",
                        "created":time.time(),"model":model,
                        "object":"chat.completion.chunk",
                        "system_fingerprint":"fp_something",
                        "choices":[{"index":0,"delta":{}}],
                        "stream_options":{"include_usage":True},
                        "usage":{
                            "completion_tokens":10,
                            "prompt_tokens":167,
                            "total_tokens":177,
                            "completion_tokens_details":{"accepted_prediction_tokens":0,"audio_tokens":0,"reasoning_tokens":0,"rejected_prediction_tokens":0},
                            "prompt_tokens_details":{"audio_tokens":0,"cached_tokens":0}
                            }}) + "\n\n"
            except:
                pass
            # yield "data: [DONE]"
        return Response(generate(), mimetype='application/json')

        

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/models",methods=["GET"])
def models():
    models = []
    typegpt = TypeGPT()
    models = models + typegpt.models()
    return jsonify(models), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
