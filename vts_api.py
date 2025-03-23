import os
import time
import json
import subprocess
from websocket import WebSocketApp
from threading import Thread, Event
from vts_requester import VTSRequester
from dotenv import load_dotenv

load_dotenv()

class VTSApi:
    def __init__(self, plugin_name: str, plugin_dev: str, websocket_url: str = "ws://localhost:8001"):
        self.game_id = 1325860 # Don't change, as this is the set ID for VTubeStudio on Steam
        self.websocket_url = websocket_url
        self.plugin_name = plugin_name
        self.plugin_dev = plugin_dev
        self.auth_token = os.getenv("VTS_TOKEN")
        self.is_connected = False
        self.ws_event = Event()
        self.ws_thread = Thread(target=self.open_websocket, daemon=True, args=(self.ws_event,))


    def on_message(self, ws: WebSocketApp, response: str):
        """Receives responses from VTube Studio and performs actions accordingly."""
        response = json.loads(response)
        match response["messageType"]:
            case "AuthenticationResponse":
                print("Authentication successful.")
            case "AuthenticationTokenResponse":
                # Save the token to the .env file
                with open(".env", "a+") as file:
                    auth_token = response["data"]["authenticationToken"]
                    file.write(f"\nVTS_TOKEN = \"{auth_token}\"")
                    self.auth_token = auth_token
                print("Saved VTS Authentication Token in: .env")
                self.vts_requester.request_authentication(plugin_name=self.plugin_name, plugin_dev=self.plugin_dev, auth_token=self.auth_token)
            case "APIError":
                print(f"API Error: {response["data"]["message"]}")
                ws.close()
            case _:
                # Unblock the main thread (usually you will be doing this for most requests)
                # Refer to the VTSRequester class to see/modify what requests block the main thread
                self.ws_event.set()


    def on_open(self, ws: WebSocketApp):
        """Authenticate with VTube Studio on connection."""
        self.is_connected = True
        self.vts_requester = VTSRequester(
            ws=ws, 
            ws_event=self.ws_event
        )
        print("WebSocket connection established.")
        self.vts_requester.request_authentication(self.plugin_name, self.plugin_dev, self.auth_token) if self.auth_token else self.vts_requester.request_authentication_token(self.plugin_name, self.plugin_dev)


    def on_close(self, ws: WebSocketApp, close_status_code, message: str):
        print(f"API Closed with Status: {close_status_code} and message: {message}")


    def on_error(self, ws: WebSocketApp, message: str):
        if "[WinError 10061]" in message:
            print("Connection to API failed. Retrying...")
        else:
            print(f"WebSocket Error: {message}.")


    def open_vts(self):
        """Runs VTubeStudio via steam."""
        subprocess.run(["start", f"steam://rungameid/{self.game_id}"], shell=True)


    def open_websocket(self, event):
        """Runs the WebSocket client in a loop."""
        # Continuously try to connect to the WebSocket until it connects
        while not self.is_connected:
            ws = WebSocketApp(
                self.websocket_url,
                on_message=self.on_message,
                on_open=self.on_open,
                on_close=self.on_close,
                on_error=self.on_error
            )
            ws.run_forever()
        self.is_connected = False
        print("API connection has shut down.")


    def connect(self):
        """Opens VTubeStudio app on steam, and starts the API thread."""
        self.open_vts()
        self.ws_thread.start()

# Connect to the API
vts_api = VTSApi("Test Plugin", "Test Dev")
vts_api.connect()

while True:
    # Simulates keeping the main thread alive to perform other actions while the API runs
    time.sleep(0.1)