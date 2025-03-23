import json
from typing import Dict
from threading import Event
from websocket import WebSocketApp

class VTSRequester():
    def __init__(self, ws: WebSocketApp, ws_event: Event):
        """Handles requests to the VTubeStudio API via the connected WebSocket.
        Also requires an Event to handle thread execution turns."""
        self.ws = ws
        self.ws_event = ws_event
        self.non_main_thread_blocking_requests = ["parameter_inject", "subscription", "auth_request", "auth_token_request"]

    def base_request(
            self, 
            request_id: str, 
            message_type: str, 
            data: Dict = None
        ):
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": message_type,
            "data": data
        }
        self.ws.send(json.dumps(request))

        # Block the ws_thread to process the current request before continuing
        if request_id not in self.non_main_thread_blocking_requests:
            self.ws_event.clear()
            self.ws_event.wait()

    def request_authentication(
            self, 
            plugin_name: str, 
            plugin_dev: str, 
            auth_token: str
        ):
        request_id = "auth_request"
        message_type = "AuthenticationRequest"
        data = {
            "pluginName": plugin_name,
            "pluginDeveloper": plugin_dev,
            "authenticationToken": auth_token
        }
        self.base_request(request_id, message_type, data)

    def request_authentication_token(
            self, 
            plugin_name: str, 
            plugin_dev: str
        ):
        request_id = "auth_token_request"
        message_type = "AuthenticationTokenRequest"
        data = {
            "pluginName": plugin_name,
            "pluginDeveloper": plugin_dev,
        }
        self.base_request(request_id, message_type, data)
            
    def request_parameter_values(self, parameter_name):
        request_id = "parameter_request"
        message_type = "ParameterValueRequest"
        data = {
		    "name": parameter_name
	    }
        self.base_request(request_id, message_type, data)

    def inject_parameter_values(
            self, 
            parameter_name: str, 
            value: float,
            mode: str = "set",
            face_found: bool = True
        ):
        request_id = "parameter_inject"
        message_type = "InjectParameterDataRequest"
        data = {
            "faceFound": face_found,
            "mode": mode,
            "parameterValues": [
                {
                    "id": parameter_name,
                    "value": value
                }
            ]
        }
        self.base_request(request_id, message_type, data)

    def request_current_model(self):
        request_id = "model_current"
        message_type = "CurrentModelRequest"
        self.base_request(request_id, message_type)

    def request_item_load(
            self, 
            name: str, 
            x: float = 0, 
            y: float = 0, 
            size: float = 0, 
            rotation: float = 0, 
            fade_time: float = 0.5, 
            order: int = 1, 
            fail_if_order_taken: bool = False, 
            smoothing: float = 0, 
            censored: bool = False, 
            flipped: bool = False, 
            locked: bool = False, 
            unload_when_plugin_disconnects: bool = True, 
            custom_data_base64: str = "", 
            custom_data_ask_user_first: bool = True, 
            custom_data_skip_asking_user_if_whitelisted: bool = True, 
            custom_data_ask_timer: float = -1
        ):
        request_id = "item_load"
        message_type = "ItemLoadRequest"
        data = {
            "fileName": name,
            "positionX": x,
            "positionY": y,
            "size": size,
            "rotation": rotation,
            "fadeTime": fade_time,
            "order": order,
            "failIfOrderTaken": fail_if_order_taken,
            "smoothing": smoothing,
            "censored": censored,
            "flipped": flipped,
            "locked": locked,
            "unloadWhenPluginDisconnects": unload_when_plugin_disconnects,
            "customDataBase64": custom_data_base64,
            "customDataAskUserFirst": custom_data_ask_user_first,
            "customDataSkipAskingUserIfWhitelisted": custom_data_skip_asking_user_if_whitelisted,
            "customDataAskTimer": custom_data_ask_timer
        }
        self.base_request(request_id, message_type, data)

    def request_item_unload(
            self,
            instance_ids: list,
            unload_all_in_scene: bool = False,
            unload_all_loaded_by_this_plugin: bool = False,
            allow_unloading_items_loaded_by_user_or_other_plugins: bool = True
        ):
        request_id = "item_unload"
        message_type = "ItemUnloadRequest"
        data = {
            "unloadAllInScene": unload_all_in_scene,
            "unloadAllLoadedByThisPlugin": unload_all_loaded_by_this_plugin,
            "allowUnloadingItemsLoadedByUserOrOtherPlugins": allow_unloading_items_loaded_by_user_or_other_plugins,
            "instanceIDs": instance_ids
    	}
        self.base_request(request_id, message_type, data)

    def request_model_move(
            self,
            time_in_seconds: float = 0.2,
            values_are_relative_to_movel: bool = False,
            x: float = 0,
            y: float = 0,
            rotation: float = 0,
            size: float = -50
        ):
        request_id = "model_move"
        message_type = "MoveModelRequest"
        data = {
            "timeInSeconds": time_in_seconds,
            "valuesAreRelativeToModel": values_are_relative_to_movel,
            "positionX": x,
            "positionY": y,
            "rotation": rotation,
            "size": size
        }
        self.base_request(request_id, message_type, data)

    def request_item_pin(
            self,
            item_id: str,
            model_id: str,
            art_mesh_id: str,
            vertex_id1: int,
            vertex_id2: int,
            vertex_id3: int,
            vertex_weight1: float,
            vertex_weight2: float,
            vertex_weight3: float,
            angle_relative_to: str = "RelativeToModel",
            size_relative_to: str = "RelativeToWorld",
            vertex_pin_type: str = "Provided",
            angle: float = 0,
            size: float = 0.32
        ):
        request_id = "item_pin"
        message_type = "ItemPinRequest"
        data = {
            "pin": True,
            "itemInstanceID": item_id,
            "angleRelativeTo": angle_relative_to,
            "sizeRelativeTo": size_relative_to,
            "vertexPinType": vertex_pin_type,
            "pinInfo": {
                "modelID": model_id,
                "artMeshID": art_mesh_id,
                "angle": angle,
                "size": size,
                "vertexID1": vertex_id1,
                "vertexID2": vertex_id2,
                "vertexID3": vertex_id3,
                "vertexWeight1": vertex_weight1,
                "vertexWeight2": vertex_weight2,
                "vertexWeight3": vertex_weight3
            }
        }
        self.base_request(request_id, message_type, data)

    def request_event_subscription(
            self,
            name: str,
            config: Dict
        ):
        request_id = "subscription"
        message_type = "EventSubscriptionRequest"
        data = {
            "eventName": name,
            "config": config
        }
        self.base_request(request_id, message_type, data)