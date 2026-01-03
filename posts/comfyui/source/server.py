from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import base64
import io
import os
import json
import requests
import time
from urllib.parse import urlparse

CORS_ORIGINS = "*"
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})
CORS(app)

# Directory to serve images from (relative to repo root: ../../.. / images)
IMAGES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'images'))

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '')
    # Load workflow template and replace node 6 inputs.text with the prompt
    base = os.path.dirname(__file__)
    workflow_path = os.path.join(base, 'simple_workflow.json')
    runtime_path = os.path.join(base, 'simple_workflow_runtime.json')
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            wf = json.load(f)

        # Navigate to node '6' -> inputs -> text and replace
        if '6' in wf and isinstance(wf['6'], dict):
            inputs = wf['6'].get('inputs', {})
            inputs['text'] = prompt
            wf['6']['inputs'] = inputs

        # Send the modified workflow to local ComfyUI endpoint
        payload = {
            'prompt': wf,
            'client_id': os.environ.get('COMFYUI_CLIENT_ID', 'my_client_123')
        }
        headers = {'Content-Type': 'application/json'}
        try:
            # send JSON with 'prompt' containing the workflow object
            resp = requests.post("http://127.0.0.1:8188/prompt", json=payload, headers=headers, timeout=30)
        except requests.RequestException as re:
            return jsonify({'error': 'failed to reach ComfyUI', 'detail': str(re), 'sent_payload_summary': str({'client_id': payload['client_id'], 'prompt_keys': list(wf.keys())})}), 502

        if resp.status_code != 200:
            return jsonify({'error': 'ComfyUI returned error', 'status_code': resp.status_code, 'detail': resp.text, 'sent_payload_summary': str({'client_id': payload['client_id'], 'prompt_keys': list(wf.keys())})}), 502

        # Expect JSON with prompt_id and number
        try:
            resp_json = resp.json()
        except Exception:
            return jsonify({'error': 'invalid json from ComfyUI', 'detail': resp.text}), 502

        prompt_id = resp_json.get('prompt_id') or resp_json.get('id')
        if not prompt_id:
            return jsonify({'error': 'ComfyUI did not return prompt_id', 'resp': resp_json}), 502

        print(f"prompt_id : {prompt_id}")

        # Poll history endpoint until the job is ready or timeout
        poll_url = f"http://127.0.0.1:8188/history/{prompt_id}"
        poll_timeout = int(os.environ.get('COMFYUI_POLL_TIMEOUT', '30'))
        poll_interval = float(os.environ.get('COMFYUI_POLL_INTERVAL', '1'))
        start = time.time()
        entry = None
        while True:
            try:
                hresp = requests.get(poll_url, timeout=10)
            except requests.RequestException as e:
                return jsonify({'error': 'failed to query history', 'detail': str(e)}), 502

            if hresp.status_code != 200:
                return jsonify({'error': 'history endpoint error', 'status_code': hresp.status_code, 'detail': hresp.text}), 502

            try:
                hjson = hresp.json()
            except Exception:
                return jsonify({'error': 'invalid json from history', 'detail': hresp.text}), 502

            # history response structure: { "<prompt_id>": { ... } }
            if isinstance(hjson, dict):
                if prompt_id in hjson:
                    entry = hjson[prompt_id]
                elif len(hjson) == 1:
                    # some implementations return single-key dict
                    entry = next(iter(hjson.values()))

            if entry:
                status = entry.get('status', {})
                # completed flag indicates finished
                if isinstance(status, dict) and status.get('completed'):
                    break
                # check outputs presence as alternative
                outputs_check = entry.get('outputs')
                if isinstance(outputs_check, dict) and any(outputs_check.values()):
                    break

            if time.time() - start > poll_timeout:
                return jsonify({'error': 'timeout waiting for ComfyUI result', 'prompt_id': prompt_id}), 504

            time.sleep(poll_interval)

        if not entry:
            return jsonify({'error': 'no history entry found', 'prompt_id': prompt_id}), 502

        # Extract image info from outputs: outputs -> node_id -> { images: [ {filename, subfolder, type}, ... ] }
        outputs = entry.get('outputs', {})
        image_info = None
        if isinstance(outputs, dict):
            for node_id, node_out in outputs.items():
                if not isinstance(node_out, dict):
                    continue
                imgs = node_out.get('images')
                if not imgs or not isinstance(imgs, list):
                    continue
                first = imgs[0]
                if not isinstance(first, dict):
                    continue
                filename = first.get('filename')
                subfolder = first.get('subfolder', '')
                ftype = first.get('type', 'output')
                if filename:
                    image_info = {'filename': filename, 'subfolder': subfolder, 'type': ftype}
                    break

        if not image_info:
            return jsonify({'error': 'no image info found in history outputs', 'outputs': outputs}), 502

        filename = image_info['filename']
        subfolder = image_info.get('subfolder', '')
        ftype = image_info.get('type', 'output')

        # Fetch the generated image via /view
        view_url = f"http://127.0.0.1:8188/view?filename={requests.utils.requote_uri(filename)}&subfolder={requests.utils.requote_uri(subfolder)}&type={requests.utils.requote_uri(ftype)}"
        try:
            vresp = requests.get(view_url, timeout=30)
        except requests.RequestException as e:
            return jsonify({'error': 'failed to fetch image from view', 'detail': str(e)}), 502

        if vresp.status_code != 200:
            return jsonify({'error': 'view endpoint error', 'status_code': vresp.status_code, 'detail': vresp.text}), 502

        v_content_type = vresp.headers.get('Content-Type', '')
        if v_content_type.startswith('image/'):
            b64 = base64.b64encode(vresp.content).decode('ascii')
            data_url = f'data:{v_content_type};base64,{b64}'
            return jsonify({'image': data_url, 'prompt': prompt, 'prompt_id': prompt_id})

        # If view returned JSON with an imageUrl, forward it
        if 'application/json' in v_content_type:
            try:
                vjson = vresp.json()
                if isinstance(vjson, dict) and ('image' in vjson or 'imageUrl' in vjson):
                    vjson.setdefault('prompt', prompt)
                    vjson.setdefault('prompt_id', prompt_id)
                    return jsonify(vjson)
            except Exception:
                pass

        return jsonify({'result_text': vresp.text, 'prompt': prompt, 'prompt_id': prompt_id})

    except Exception as e:
        return jsonify({'error': 'failed processing workflow', 'detail': str(e)}), 500

@app.route('/')
def index():
    # Serve the demo page so frontend and backend run on same origin
    base = os.path.dirname(__file__)
    return send_from_directory(base, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7627, debug=True)
