class SafetyManager:
    def __init__(self):
        self.dangerous_patterns = [
            # System shutdown/restart
            "shutdown", "restart", "reboot", "poweroff", "halt",
            
            # File operations
            "delete", "remove", "rm ", "del ", "format", "fdisk", "mkfs",
            "rmdir", "rd ", "erase", "wipe", "shred",
            
            # Process control
            "kill", "taskkill", "pkill", "killall", "terminate",
            
            # Registry operations
            "regedit", "reg add", "reg delete", "registry",
            
            # Network/security
            "netsh", "firewall", "iptables", "ufw",
            
            # Financial/payment
            "send money", "transfer funds", "payment", "paypal", "venmo",
            "bitcoin", "crypto", "bank transfer", "wire money",
            
            # Malware/suspicious
            "download exe", "install malware", "virus", "trojan",
            "backdoor", "keylogger", "ransomware",
            
            # Data exfiltration
            "copy to usb", "upload files", "send files", "exfiltrate",
            "steal data", "backup to cloud", "sync files",
            
            # System modification
            "chmod 777", "sudo rm", "rm -rf", "del /f /q",
            "format c:", "diskpart", "bcdedit",
            
            # Administrative
            "net user", "useradd", "passwd", "password",
            "admin", "administrator", "root access"
        ]
    
    def is_safe(self, command: str) -> bool:
        """Check if command is safe to execute."""
        command_lower = command.lower().strip()
        
        # Check against dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern in command_lower:
                return False
        
        # Additional checks for suspicious combinations
        if any(word in command_lower for word in ["delete", "remove"]) and \
           any(word in command_lower for word in ["system", "windows", "program"]):
            return False
        
        if "format" in command_lower and any(drive in command_lower for drive in ["c:", "d:", "e:"]):
            return False
        
        return True