import socket
import subprocess
import platform
import ipaddress
import concurrent.futures
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
    53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
    443: 'HTTPS', 445: 'SMB', 3306: 'MySQL', 3389: 'RDP',
    5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis',
    8080: 'HTTP-Alt', 8443: 'HTTPS-Alt', 27017: 'MongoDB'
}

RISKY_PORTS = {23: 'Telnet (unencrypted)', 21: 'FTP (unencrypted)',
               3389: 'RDP (remote access)', 5900: 'VNC (remote desktop)',
               445: 'SMB (ransomware target)', 6379: 'Redis (no auth by default)'}


def scan_network(target_range: str = None) -> dict:
    result = {
        'scan_time': datetime.utcnow().isoformat(),
        'local_ip': '',
        'network_range': target_range or '',
        'devices': [],
        'open_ports_summary': {},
        'risk_findings': [],
        'recommendations': []
    }

    try:
        result['local_ip'] = _get_local_ip()
        if not target_range:
            local = result['local_ip']
            parts = local.rsplit('.', 1)
            target_range = parts[0] + '.0/24'
            result['network_range'] = target_range

        network = ipaddress.IPv4Network(target_range, strict=False)
        hosts = list(network.hosts())[:50]  # Limit to 50 hosts for safety

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(_scan_host, str(h)): str(h) for h in hosts}
            for future in concurrent.futures.as_completed(futures, timeout=30):
                host_result = future.result()
                if host_result and host_result.get('alive'):
                    result['devices'].append(host_result)

        # Risk analysis
        for device in result['devices']:
            for port in device.get('open_ports', []):
                port_num = port['port']
                if port_num in RISKY_PORTS:
                    result['risk_findings'].append(
                        f"{device['ip']} has risky port open: {port_num} ({RISKY_PORTS[port_num]})"
                    )

        if result['risk_findings']:
            result['recommendations'].append('Close unused ports and disable unnecessary services.')
            result['recommendations'].append('Use firewall rules to restrict access to sensitive ports.')
            result['recommendations'].append('Replace Telnet/FTP with SSH/SFTP.')
        else:
            result['recommendations'].append('Network appears reasonably secure. Keep devices updated.')

    except Exception as e:
        logger.error(f"Network scan error: {e}")
        result['error'] = str(e)

    return result


def scan_single_host(ip: str, port_range: tuple = (1, 1024)) -> dict:
    result = {
        'ip': ip,
        'hostname': '',
        'alive': False,
        'open_ports': [],
        'os_hint': '',
        'risk_score': 0,
        'findings': []
    }

    if not _is_host_alive(ip):
        return result

    result['alive'] = True

    try:
        result['hostname'] = socket.gethostbyaddr(ip)[0]
    except Exception:
        result['hostname'] = ip

    start, end = port_range
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(_check_port, ip, p): p for p in range(start, min(end + 1, 65536))}
        for future in concurrent.futures.as_completed(futures, timeout=60):
            port_result = future.result()
            if port_result:
                open_ports.append(port_result)

    result['open_ports'] = sorted(open_ports, key=lambda x: x['port'])

    for port_info in result['open_ports']:
        p = port_info['port']
        if p in RISKY_PORTS:
            result['risk_score'] += 20
            result['findings'].append(f"Risky service on port {p}: {RISKY_PORTS[p]}")

    result['risk_score'] = min(result['risk_score'], 100)
    return result


def _scan_host(ip: str) -> dict:
    if not _is_host_alive(ip):
        return {'ip': ip, 'alive': False}

    host_result = {'ip': ip, 'alive': True, 'hostname': ip, 'open_ports': []}

    try:
        host_result['hostname'] = socket.gethostbyaddr(ip)[0]
    except Exception:
        pass

    for port in list(COMMON_PORTS.keys()):
        port_info = _check_port(ip, port)
        if port_info:
            host_result['open_ports'].append(port_info)

    return host_result


def _is_host_alive(ip: str) -> bool:
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(
            ['ping', param, '1', '-w', '1000', ip],
            capture_output=True, timeout=3
        )
        return result.returncode == 0
    except Exception:
        # Fallback: try TCP connect on port 80
        return _check_port(ip, 80) is not None


def _check_port(ip: str, port: int) -> dict:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            service = COMMON_PORTS.get(port, 'Unknown')
            banner = _grab_banner(ip, port)
            return {
                'port': port,
                'service': service,
                'banner': banner,
                'risky': port in RISKY_PORTS
            }
    except Exception:
        pass
    return None


def _grab_banner(ip: str, port: int) -> str:
    try:
        sock = socket.socket()
        sock.settimeout(2)
        sock.connect((ip, port))
        banner = sock.recv(1024).decode(errors='replace').strip()[:100]
        sock.close()
        return banner
    except Exception:
        return ''


def _get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'
