"""Smart home control skill for JARVIS-X - Alexa-like functionality."""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from loguru import logger

class SmartHomeSkill:
    """Provides smart home control features similar to Alexa."""

    def __init__(self):
        self.devices_file = "jarvis_smart_devices.json"
        self.scenes_file = "jarvis_scenes.json"

        # Initialize with some default devices
        self.devices = self._load_devices()
        self.scenes = self._load_scenes()

        self.commands = {
            "control_device": ["turn on", "turn off", "dim", "brighten", "set temperature", "lock", "unlock"],
            "device_status": ["status of", "is the", "how is", "check"],
            "scene": ["activate scene", "run scene", "scene"],
            "list_devices": ["list devices", "show devices", "what devices"],
            "add_device": ["add device", "new device", "setup device"],
            "create_scene": ["create scene", "new scene", "setup scene"]
        }

    def can_handle(self, text: str) -> bool:
        """Check if this skill can handle the request."""
        text_lower = text.lower()
        for command_list in self.commands.values():
            if any(cmd in text_lower for cmd in command_list):
                return True
        return False

    def execute(self, text: str) -> str:
        """Execute smart home command."""
        text_lower = text.lower()

        try:
            # Device control
            if any(cmd in text_lower for cmd in self.commands["control_device"]):
                return self._control_device(text)

            # Device status
            elif any(cmd in text_lower for cmd in self.commands["device_status"]):
                return self._get_device_status(text)

            # Scene activation
            elif any(cmd in text_lower for cmd in self.commands["scene"]):
                return self._activate_scene(text)

            # List devices
            elif any(cmd in text_lower for cmd in self.commands["list_devices"]):
                return self._list_devices()

            # Add device
            elif any(cmd in text_lower for cmd in self.commands["add_device"]):
                return self._add_device(text)

            # Create scene
            elif any(cmd in text_lower for cmd in self.commands["create_scene"]):
                return self._create_scene(text)

            else:
                return self._get_smart_home_overview()

        except Exception as e:
            logger.error(f"Smart home skill error: {e}")
            return "Sorry, I'm having trouble with smart home controls right now."

    def _control_device(self, text: str) -> str:
        """Control a smart home device."""
        try:
            device_name = self._extract_device_name(text)
            action = self._extract_action(text)
            value = self._extract_value(text)

            if not device_name:
                return "Please specify which device you'd like to control."

            if not action:
                return "Please specify what you'd like to do with the device."

            # Find device
            device = self._find_device(device_name)
            if not device:
                return f"I couldn't find a device named '{device_name}'. Available devices: {', '.join(self.devices.keys())}"

            # Execute action
            result = self._execute_device_action(device, action, value)
            self._save_devices()

            return result

        except Exception as e:
            logger.error(f"Device control error: {e}")
            return "Sorry, I couldn't control that device."

    def _get_device_status(self, text: str) -> str:
        """Get status of a device."""
        try:
            device_name = self._extract_device_name(text)

            if not device_name:
                return "Please specify which device you'd like to check."

            device = self._find_device(device_name)
            if not device:
                return f"I couldn't find a device named '{device_name}'."

            status = self._get_device_status_text(device)
            return f"The {device['name']} is {status}."

        except Exception as e:
            logger.error(f"Device status error: {e}")
            return "Sorry, I couldn't check that device status."

    def _activate_scene(self, text: str) -> str:
        """Activate a smart home scene."""
        try:
            scene_name = self._extract_scene_name(text)

            if not scene_name:
                return "Please specify which scene you'd like to activate."

            if scene_name not in self.scenes:
                return f"I couldn't find a scene named '{scene_name}'. Available scenes: {', '.join(self.scenes.keys())}"

            scene = self.scenes[scene_name]
            results = []

            for action in scene['actions']:
                device_name = action['device']
                device_action = action['action']
                device_value = action.get('value')

                device = self._find_device(device_name)
                if device:
                    result = self._execute_device_action(device, device_action, device_value)
                    results.append(result)

            self._save_devices()
            return f"Scene '{scene_name}' activated. {len(results)} devices controlled."

        except Exception as e:
            logger.error(f"Scene activation error: {e}")
            return "Sorry, I couldn't activate that scene."

    def _list_devices(self) -> str:
        """List all smart home devices."""
        if not self.devices:
            return "You don't have any smart home devices set up yet. Try adding some devices first."

        response = f"You have {len(self.devices)} smart home devices:\\n\\n"

        for device_id, device in self.devices.items():
            status = self._get_device_status_text(device)
            response += f"• {device['name']} ({device['type']}): {status}\\n"

        return response

    def _add_device(self, text: str) -> str:
        """Add a new smart home device."""
        try:
            device_info = self._extract_device_info(text)

            if not device_info['name'] or not device_info['type']:
                return "Please specify the device name and type. For example: 'add device living room light'"

            device_id = f"{device_info['type']}_{len(self.devices) + 1}"
            device = {
                'id': device_id,
                'name': device_info['name'],
                'type': device_info['type'],
                'status': 'off',
                'created': datetime.now().isoformat()
            }

            # Add type-specific properties
            if device_info['type'] == 'light':
                device['brightness'] = 100
                device['color'] = 'white'
            elif device_info['type'] == 'thermostat':
                device['temperature'] = 72
                device['mode'] = 'auto'
            elif device_info['type'] == 'lock':
                device['locked'] = True

            self.devices[device_id] = device
            self._save_devices()

            return f"Added new {device_info['type']}: {device_info['name']}"

        except Exception as e:
            logger.error(f"Add device error: {e}")
            return "Sorry, I couldn't add that device."

    def _create_scene(self, text: str) -> str:
        """Create a new smart home scene."""
        try:
            scene_info = self._extract_scene_info(text)

            if not scene_info['name']:
                return "Please specify a name for the scene."

            scene = {
                'name': scene_info['name'],
                'actions': scene_info['actions'],
                'created': datetime.now().isoformat()
            }

            self.scenes[scene_info['name']] = scene
            self._save_scenes()

            return f"Created scene '{scene_info['name']}' with {len(scene_info['actions'])} actions."

        except Exception as e:
            logger.error(f"Create scene error: {e}")
            return "Sorry, I couldn't create that scene."

    def _get_smart_home_overview(self) -> str:
        """Get smart home overview."""
        device_count = len(self.devices)
        scene_count = len(self.scenes)

        return (f"Smart Home Overview:\\n"
               f"🏠 Devices: {device_count}\\n"
               f"🎭 Scenes: {scene_count}\\n\\n"
               f"Try commands like:\\n"
               f"• 'turn on living room light'\\n"
               f"• 'set temperature to 75 degrees'\\n"
               f"• 'activate goodnight scene'\\n"
               f"• 'add device kitchen light'")

    def _find_device(self, name: str) -> Dict[str, Any]:
        """Find device by name."""
        name_lower = name.lower()
        for device in self.devices.values():
            if device['name'].lower() == name_lower:
                return device
        return {}

    def _execute_device_action(self, device: Dict[str, Any], action: str, value: Any = None) -> str:
        """Execute action on device."""
        device_type = device['type']

        if device_type == 'light':
            return self._control_light(device, action, value)
        elif device_type == 'thermostat':
            return self._control_thermostat(device, action, value)
        elif device_type == 'lock':
            return self._control_lock(device, action, value)
        elif device_type == 'switch':
            return self._control_switch(device, action, value)
        else:
            return f"Unknown device type: {device_type}"

    def _control_light(self, device: Dict[str, Any], action: str, value: Any = None) -> str:
        """Control a light device."""
        if action == 'turn_on':
            device['status'] = 'on'
            return f"Turned on {device['name']}"
        elif action == 'turn_off':
            device['status'] = 'off'
            return f"Turned off {device['name']}"
        elif action == 'dim':
            if value and isinstance(value, int):
                device['brightness'] = max(0, min(100, value))
            else:
                device['brightness'] = max(0, device.get('brightness', 100) - 20)
            return f"Dimmed {device['name']} to {device['brightness']}%"
        elif action == 'brighten':
            if value and isinstance(value, int):
                device['brightness'] = max(0, min(100, value))
            else:
                device['brightness'] = min(100, device.get('brightness', 0) + 20)
            return f"Brightened {device['name']} to {device['brightness']}%"

        return f"Unknown action '{action}' for light"

    def _control_thermostat(self, device: Dict[str, Any], action: str, value: Any = None) -> str:
        """Control a thermostat device."""
        if action == 'set_temperature':
            if value and isinstance(value, (int, float)):
                device['temperature'] = value
                return f"Set {device['name']} to {value}°F"
            return "Please specify a temperature value"

        return f"Unknown action '{action}' for thermostat"

    def _control_lock(self, device: Dict[str, Any], action: str, value: Any = None) -> str:
        """Control a lock device."""
        if action == 'lock':
            device['locked'] = True
            return f"Locked {device['name']}"
        elif action == 'unlock':
            device['locked'] = False
            return f"Unlocked {device['name']}"

        return f"Unknown action '{action}' for lock"

    def _control_switch(self, device: Dict[str, Any], action: str, value: Any = None) -> str:
        """Control a switch device."""
        if action == 'turn_on':
            device['status'] = 'on'
            return f"Turned on {device['name']}"
        elif action == 'turn_off':
            device['status'] = 'off'
            return f"Turned off {device['name']}"

        return f"Unknown action '{action}' for switch"

    def _get_device_status_text(self, device: Dict[str, Any]) -> str:
        """Get human-readable device status."""
        if device['type'] == 'light':
            status = device.get('status', 'off')
            brightness = device.get('brightness', 100)
            return f"{status} at {brightness}% brightness"
        elif device['type'] == 'thermostat':
            temp = device.get('temperature', 72)
            return f"set to {temp}°F"
        elif device['type'] == 'lock':
            locked = device.get('locked', True)
            return "locked" if locked else "unlocked"
        elif device['type'] == 'switch':
            return device.get('status', 'off')
        else:
            return device.get('status', 'unknown')

    def _load_devices(self) -> Dict[str, Any]:
        """Load devices from file."""
        try:
            if os.path.exists(self.devices_file):
                with open(self.devices_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading devices: {e}")

        # Return default devices
        return {
            'light_1': {
                'id': 'light_1',
                'name': 'Living Room Light',
                'type': 'light',
                'status': 'off',
                'brightness': 100,
                'created': datetime.now().isoformat()
            },
            'thermostat_1': {
                'id': 'thermostat_1',
                'name': 'Home Thermostat',
                'type': 'thermostat',
                'temperature': 72,
                'mode': 'auto',
                'created': datetime.now().isoformat()
            }
        }

    def _save_devices(self):
        """Save devices to file."""
        try:
            with open(self.devices_file, 'w') as f:
                json.dump(self.devices, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving devices: {e}")

    def _load_scenes(self) -> Dict[str, Any]:
        """Load scenes from file."""
        try:
            if os.path.exists(self.scenes_file):
                with open(self.scenes_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading scenes: {e}")

        # Return default scenes
        return {
            'goodnight': {
                'name': 'Goodnight',
                'actions': [
                    {'device': 'Living Room Light', 'action': 'turn_off'},
                    {'device': 'Home Thermostat', 'action': 'set_temperature', 'value': 68}
                ],
                'created': datetime.now().isoformat()
            }
        }

    def _save_scenes(self):
        """Save scenes to file."""
        try:
            with open(self.scenes_file, 'w') as f:
                json.dump(self.scenes, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving scenes: {e}")

    # Text extraction helper methods
    def _extract_device_name(self, text: str) -> str:
        """Extract device name from text."""
        # Look for device names in the text
        device_names = [d['name'] for d in self.devices.values()]
        text_lower = text.lower()

        for name in device_names:
            if name.lower() in text_lower:
                return name

        # Try to extract from common patterns
        import re
        patterns = [
            r"the ([a-zA-Z\\s]+) (?:light|thermostat|lock|switch)",
            r"([a-zA-Z\\s]+) (?:light|thermostat|lock|switch)",
            r"turn (?:on|off) ([a-zA-Z\\s]+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_action(self, text: str) -> str:
        """Extract action from text."""
        text_lower = text.lower()

        if 'turn on' in text_lower:
            return 'turn_on'
        elif 'turn off' in text_lower:
            return 'turn_off'
        elif 'dim' in text_lower or 'dimmer' in text_lower:
            return 'dim'
        elif 'brighten' in text_lower or 'brighter' in text_lower:
            return 'brighten'
        elif 'set temperature' in text_lower or 'change temperature' in text_lower:
            return 'set_temperature'
        elif 'lock' in text_lower:
            return 'lock'
        elif 'unlock' in text_lower:
            return 'unlock'

        return ""

    def _extract_value(self, text: str) -> Any:
        """Extract value from text."""
        import re

        # Extract numbers
        numbers = re.findall(r'\\d+', text)
        if numbers:
            return int(numbers[0])

        # Extract temperature values
        temp_match = re.search(r'(\\d+) degrees?', text, re.IGNORECASE)
        if temp_match:
            return int(temp_match.group(1))

        return None

    def _extract_scene_name(self, text: str) -> str:
        """Extract scene name from text."""
        import re
        match = re.search(r'(?:activate|run) scene ([a-zA-Z\\s]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Check existing scenes
        text_lower = text.lower()
        for scene_name in self.scenes.keys():
            if scene_name.lower() in text_lower:
                return scene_name

        return ""

    def _extract_device_info(self, text: str) -> Dict[str, str]:
        """Extract device info from text."""
        import re

        # Pattern: "add device [name] [type]"
        match = re.search(r'add device ([a-zA-Z\\s]+) (light|thermostat|lock|switch)', text, re.IGNORECASE)
        if match:
            return {
                'name': match.group(1).strip(),
                'type': match.group(2).lower()
            }

        return {'name': '', 'type': ''}

    def _extract_scene_info(self, text: str) -> Dict[str, Any]:
        """Extract scene info from text."""
        # This is a simplified implementation
        # In a real implementation, you'd parse more complex scene creation commands
        return {
            'name': 'Custom Scene',
            'actions': []
        }
