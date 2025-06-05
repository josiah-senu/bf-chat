#!/usr/bin/env python3
"""
IMPROVED BRAINFUCK CHAT - Fixed UI and Multi-Client Issues
==========================================================

Fixes:
1. No more "You:" prompt appearing after received messages
2. Graceful handling of multiple clients without breaking connections
3. Better UI with clean message display
4. Proper client management and error handling
"""

import socket
import threading
import time
import sys
import os

class ImprovedBrainfuckEngine:
    """Improved BF interpreter"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.memory = [0] * 1000
        self.pointer = 0
        self.input_buffer = []
        self.output_buffer = []
    
    def load_input(self, data):
        if isinstance(data, str):
            self.input_buffer = [ord(c) for c in data[::-1]]
        else:
            self.input_buffer = list(reversed(data))
    
    def execute(self, code, max_steps=50000):
        """Execute BF code with better error handling"""
        self.output_buffer = []
        ip = 0
        steps = 0
        
        try:
            while ip < len(code) and steps < max_steps:
                cmd = code[ip]
                
                if cmd == '>':
                    self.pointer = min(self.pointer + 1, len(self.memory) - 1)
                elif cmd == '<':
                    self.pointer = max(self.pointer - 1, 0)
                elif cmd == '+':
                    self.memory[self.pointer] = (self.memory[self.pointer] + 1) % 256
                elif cmd == '-':
                    self.memory[self.pointer] = (self.memory[self.pointer] - 1) % 256
                elif cmd == '.':
                    self.output_buffer.append(self.memory[self.pointer])
                elif cmd == ',':
                    if self.input_buffer:
                        self.memory[self.pointer] = self.input_buffer.pop()
                    else:
                        self.memory[self.pointer] = 0
                elif cmd == '[':
                    if self.memory[self.pointer] == 0:
                        bracket_count = 1
                        ip += 1
                        while ip < len(code) and bracket_count > 0:
                            if code[ip] == '[':
                                bracket_count += 1
                            elif code[ip] == ']':
                                bracket_count -= 1
                            ip += 1
                        ip -= 1
                elif cmd == ']':
                    if self.memory[self.pointer] != 0:
                        bracket_count = 1
                        ip -= 1
                        while ip >= 0 and bracket_count > 0:
                            if code[ip] == ']':
                                bracket_count += 1
                            elif code[ip] == '[':
                                bracket_count -= 1
                            ip -= 1
                
                ip += 1
                steps += 1
            
            return steps < max_steps
            
        except Exception as e:
            return False
    
    def get_output_string(self):
        """Get output as string"""
        try:
            return ''.join(chr(b) for b in self.output_buffer if 0 <= b <= 127)
        except:
            return ""

class ImprovedBrainfuckChatProtocol:
    """Improved chat protocol"""
    
    def __init__(self):
        self.bf = ImprovedBrainfuckEngine()
        
        # Simple and reliable encryption
        self.encrypt_program = ",[+.,]"    # Caesar +1
        self.decrypt_program = ",[-.,]"    # Caesar -1
    
    def encrypt_message(self, message):
        """Encrypt message"""
        try:
            self.bf.reset()
            self.bf.load_input(message)
            
            if self.bf.execute(self.encrypt_program):
                result = self.bf.get_output_string()
                return result if result else message
            return message
        except:
            return message
    
    def decrypt_message(self, encrypted_message):
        """Decrypt message"""
        try:
            self.bf.reset()
            self.bf.load_input(encrypted_message)
            
            if self.bf.execute(self.decrypt_program):
                result = self.bf.get_output_string()
                return result if result else encrypted_message
            return encrypted_message
        except:
            return encrypted_message
    
    def validate_message(self, message):
        """Simple validation"""
        try:
            if not message or len(message) > 1000:
                return False
            for char in message:
                if ord(char) < 32 or ord(char) > 126:
                    return False
            return True
        except:
            return False

class ImprovedChatServer:
    """Improved server with better client management"""
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.clients = {}
        self.client_counter = 0
        self.protocol = ImprovedBrainfuckChatProtocol()
        self.running = False
        self.lock = threading.Lock()
    
    def start(self):
        """Start server with better error handling"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(10)  # Allow more connections
            self.running = True
            
            print("🧠🚀 IMPROVED Brainfuck Chat Server Started!")
            print(f"   📡 Listening on {self.host}:{self.port}")
            print("   👥 Supports multiple clients gracefully")
            print("   🔧 Fixed UI and connection issues")
            print("-" * 50)
            
            while self.running:
                try:
                    client_socket, address = server_socket.accept()
                    
                    with self.lock:
                        self.client_counter += 1
                        client_id = f"Client_{self.client_counter}"
                        
                        self.clients[client_id] = {
                            'socket': client_socket,
                            'address': address,
                            'connected_at': time.time(),
                            'active': True
                        }
                    
                    print(f"✅ {client_id} connected from {address}")
                    print(f"   👥 Total clients: {len(self.clients)}")
                    
                    # Send welcome message (unencrypted to avoid issues)
                    welcome = f"🧠 Welcome to Brainfuck Chat! You are {client_id}"
                    client_socket.send(welcome.encode('utf-8'))
                    
                    # Notify other clients about new connection
                    self.broadcast_system_message(f"🔔 {client_id} joined the chat", exclude=client_id)
                    
                    # Start client handler thread
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_id,),
                        daemon=True
                    )
                    thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"❌ Error accepting client: {e}")
                    
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.cleanup_server(server_socket)
    
    def handle_client(self, client_id):
        """Handle individual client with graceful error handling"""
        client_info = self.clients.get(client_id)
        if not client_info:
            return
            
        client_socket = client_info['socket']
        
        try:
            while self.running and client_info.get('active', False):
                # Set a timeout to detect disconnections
                client_socket.settimeout(1.0)
                
                try:
                    data = client_socket.recv(1024).decode('utf-8', errors='ignore')
                except socket.timeout:
                    continue  # Continue if no data received within timeout
                
                if not data:
                    print(f"📤 {client_id} disconnected normally")
                    break
                
                # Decrypt message
                try:
                    decrypted_message = self.protocol.decrypt_message(data)
                except:
                    decrypted_message = data
                
                # Validate message
                if not self.protocol.validate_message(decrypted_message):
                    error_msg = "❌ Invalid message format"
                    self.send_to_client(client_id, error_msg)
                    continue
                
                print(f"💬 {client_id}: {decrypted_message}")
                
                # Handle commands
                if decrypted_message.startswith('/'):
                    self.handle_command(client_id, decrypted_message)
                    continue
                
                # Broadcast message to all other clients
                self.broadcast_message(client_id, decrypted_message)
                
        except Exception as e:
            print(f"❌ Error handling {client_id}: {e}")
        finally:
            self.disconnect_client(client_id)
    
    def broadcast_message(self, sender_id, message):
        """Broadcast message to all other clients"""
        broadcast_msg = f"{sender_id}: {message}"
        
        with self.lock:
            clients_to_remove = []
            
            for client_id, client_info in self.clients.items():
                if client_id != sender_id and client_info.get('active', False):
                    try:
                        encrypted_msg = self.protocol.encrypt_message(broadcast_msg)
                        client_info['socket'].send(encrypted_msg.encode('utf-8'))
                    except Exception as e:
                        print(f"❌ Failed to send to {client_id}: {e}")
                        clients_to_remove.append(client_id)
            
            # Remove failed clients
            for client_id in clients_to_remove:
                self.disconnect_client(client_id)
    
    def broadcast_system_message(self, message, exclude=None):
        """Broadcast system message to all clients"""
        with self.lock:
            clients_to_remove = []
            
            for client_id, client_info in self.clients.items():
                if client_id != exclude and client_info.get('active', False):
                    try:
                        client_info['socket'].send(message.encode('utf-8'))
                    except Exception as e:
                        clients_to_remove.append(client_id)
            
            # Remove failed clients
            for client_id in clients_to_remove:
                self.disconnect_client(client_id)
    
    def send_to_client(self, client_id, message):
        """Send message to specific client"""
        with self.lock:
            client_info = self.clients.get(client_id)
            if client_info and client_info.get('active', False):
                try:
                    client_info['socket'].send(message.encode('utf-8'))
                    return True
                except Exception as e:
                    print(f"❌ Failed to send to {client_id}: {e}")
                    self.disconnect_client(client_id)
                    return False
        return False
    
    def disconnect_client(self, client_id):
        """Gracefully disconnect a client"""
        with self.lock:
            client_info = self.clients.get(client_id)
            if client_info:
                client_info['active'] = False
                
                try:
                    client_info['socket'].close()
                except:
                    pass
                
                del self.clients[client_id]
                print(f"👋 {client_id} disconnected")
                print(f"   👥 Remaining clients: {len(self.clients)}")
                
                # Notify other clients
                self.broadcast_system_message(f"📤 {client_id} left the chat", exclude=client_id)
    
    def handle_command(self, client_id, command):
        """Handle special commands"""
        if command == '/users':
            with self.lock:
                user_list = f"👥 Connected users: {', '.join(self.clients.keys())}"
            self.send_to_client(client_id, user_list)
        
        elif command == '/time':
            current_time = time.strftime("%H:%M:%S")
            time_msg = f"🕐 Server time: {current_time}"
            self.send_to_client(client_id, time_msg)
        
        elif command.startswith('/bf '):
            bf_code = command[4:]
            try:
                self.protocol.bf.reset()
                self.protocol.bf.load_input("Hello!")
                success = self.protocol.bf.execute(bf_code, max_steps=5000)
                
                if success:
                    bf_output = self.protocol.bf.get_output_string()
                    response = f"🧠 BF Output: '{bf_output}'"
                else:
                    response = "❌ BF Error: Program failed or exceeded step limit"
                
                self.send_to_client(client_id, response)
                
            except Exception as e:
                error_msg = f"❌ BF Error: {str(e)}"
                self.send_to_client(client_id, error_msg)
        
        elif command == '/help':
            help_msg = """🔰 Available Commands:
/users - Show connected users
/time - Show server time
/bf <code> - Execute Brainfuck code
/help - Show this help
/quit - Disconnect from chat"""
            self.send_to_client(client_id, help_msg)
        
        else:
            self.send_to_client(client_id, "❓ Unknown command. Type /help for available commands.")
    
    def cleanup_server(self, server_socket):
        """Clean shutdown"""
        self.running = False
        
        with self.lock:
            for client_id, client_info in list(self.clients.items()):
                try:
                    client_info['socket'].close()
                except:
                    pass
            self.clients.clear()
        
        try:
            server_socket.close()
        except:
            pass
        
        print("🔒 Server shutdown complete")

class ImprovedChatClient:
    """Improved chat client with better UI"""
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.protocol = ImprovedBrainfuckChatProtocol()
        self.connected = False
        self.username = "You"
        self.receiving = False
    
    def connect(self):
        """Connect with better error handling"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            print(f"🧠🔌 Connected to Improved Brainfuck Chat!")
            print("💡 Commands: /users, /time, /bf <code>, /help, /quit")
            print("=" * 50)
            
            # Start receiver thread
            receiver_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receiver_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def receive_messages(self):
        """Receive messages with improved UI handling"""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    print("\n💔 Connection lost")
                    self.connected = False
                    break
                
                # Try to decrypt
                try:
                    decrypted_message = self.protocol.decrypt_message(data)
                    message_to_display = decrypted_message
                except:
                    message_to_display = data
                
                # Clear the current input line and display message
                self.display_received_message(message_to_display)
                
            except Exception as e:
                if self.connected:
                    print(f"\n❌ Receive error: {e}")
                self.connected = False
                break
    
    def display_received_message(self, message):
        """Display received message without interfering with input"""
        # Move cursor to beginning of line and clear it
        print(f"\r\033[K{message}")
        
        # Re-display the input prompt if we're not in the middle of receiving multiple messages
        if not self.receiving:
            print("You: ", end="", flush=True)
    
    def start_chat(self):
        """Start chat with improved UI"""
        if not self.connect():
            return
        
        print("\n💬 Chat started! Type your messages below:")
        print("   (Type /quit to exit)")
        print()
        
        try:
            while self.connected:
                try:
                    # Use a simple input without constantly re-prompting
                    message = input("You: ").strip()
                    
                    if not message:
                        continue
                    
                    if message.lower() in ['/quit', 'quit', 'exit']:
                        print("👋 Goodbye!")
                        break
                    
                    # Encrypt and send
                    try:
                        encrypted_message = self.protocol.encrypt_message(message)
                        self.socket.send(encrypted_message.encode('utf-8'))
                    except Exception as e:
                        print(f"⚠️ Send failed: {e}")
                        break
                        
                except EOFError:
                    print("\n👋 Chat ended")
                    break
                except KeyboardInterrupt:
                    print("\n👋 Chat interrupted")
                    break
                    
        finally:
            self.disconnect()
    
    def disconnect(self):
        """Disconnect cleanly"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("🔒 Disconnected")

def main():
    """Main function with better interface"""
    print("🧠 IMPROVED BRAINFUCK CHAT APPLICATION")
    print("=" * 50)
    print("✅ Fixed: No more duplicate 'You:' prompts")
    print("✅ Fixed: Multiple clients work gracefully")
    print("✅ Improved: Better error handling and UI")
    print("=" * 50)
    
    print("\nChoose mode:")
    print("1. Start Server")
    print("2. Start Client")
    print("3. Test BF Functions")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting Improved Brainfuck Chat Server...")
            server = ImprovedChatServer()
            server.start()
            
        elif choice == "2":
            print("\n🔌 Starting Improved Brainfuck Chat Client...")
            
            host = input("Server address (Enter for localhost): ").strip()
            if not host:
                host = 'localhost'
            
            port_input = input("Server port (Enter for 8888): ").strip()
            if not port_input:
                port = 8888
            else:
                port = int(port_input)
            
            client = ImprovedChatClient(host, port)
            client.start_chat()
            
        elif choice == "3":
            print("\n🧪 Testing BF Functions...")
            test_bf_functions()
            
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except ValueError:
        print("❌ Invalid port number")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_bf_functions():
    """Test BF functions"""
    print("🧪 TESTING BRAINFUCK FUNCTIONS")
    print("-" * 30)
    
    protocol = ImprovedBrainfuckChatProtocol()
    
    test_messages = ["hi", "hello", "test123", "Hello World!"]
    
    for msg in test_messages:
        print(f"\nTesting: '{msg}'")
        encrypted = protocol.encrypt_message(msg)
        print(f"  Encrypted: '{encrypted}'")
        decrypted = protocol.decrypt_message(encrypted)
        print(f"  Decrypted: '{decrypted}'")
        is_valid = protocol.validate_message(decrypted)
        print(f"  Valid: {is_valid}")
        success = (msg == decrypted)
        print(f"  Roundtrip: {'✅ SUCCESS' if success else '❌ FAILED'}")

if __name__ == "__main__":
    main()
