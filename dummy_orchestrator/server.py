from flask import Flask, request, jsonify
import os
import json
import websockets_api_example
import websocket
import asyncio
import uuid

app = Flask(__name__)

@app.route('/process_data', methods=['POST'])
def process_data():
    # Get the JSON data from the request
    data = request.get_json()

    # Process the JSON data (e.g., validate, extract relevant information, etc.)
    json_text = json.dumps(data)

    # Print the JSON data
    print(json_text)

    # Handle image files (if any)
    for file in request.files.getlist('images'):
        if file.filename != '':
            # Save the image file to the "uploads" directory
            file.save(os.path.join("uploads", file.filename))
            print(f"Saved {file.filename} successfully.")
        else:
            print("Received an empty image file.")

    # Send prompt json to comfy server
    asyncio.run(send_prompt_to_comfy_server(json.loads(json_text)))

    # Return a response (e.g., success message, processed data, etc.)        
    return jsonify({"message": "Data processed successfully."}), 200

async def send_prompt_to_comfy_server(prompt):
    # This is an example that uses the websockets api to know when a prompt execution is done
    # Once the prompt execution is done it downloads the images using the /history endpoint
    client_id = str(uuid.uuid4())
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(websockets_api_example.server_address, client_id))
    output_images = websockets_api_example.get_images(ws, prompt)
    # save output images
    for node_id in output_images:
        for image_data in output_images[node_id]:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))
            image.save(f"output_image_{node_id}.png")
        ws.close()

if __name__ == '__main__':
    app.run(debug=True)