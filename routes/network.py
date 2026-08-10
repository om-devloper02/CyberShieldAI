from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.user import ScanHistory
from scanner.network.scanner import scan_network, scan_single_host

network_bp = Blueprint('network', __name__)


@network_bp.route('/')
@login_required
def index():
    return render_template('network/index.html')


@network_bp.route('/scan', methods=['POST'])
@login_required
def scan():
    data = request.get_json() if request.is_json else request.form
    target = data.get('target', '').strip() or None

    result = scan_network(target)
    risk_score = min(len(result.get('risk_findings', [])) * 15, 100)
    risk_level = 'dangerous' if risk_score >= 60 else ('suspicious' if risk_score >= 30 else 'safe')

    scan_record = ScanHistory(
        user_id=current_user.id,
        scan_type='network',
        input_data=target or 'local network',
        result=f"{len(result.get('devices', []))} devices found",
        risk_score=risk_score,
        risk_level=risk_level,
        details=result
    )
    db.session.add(scan_record)
    db.session.commit()

    return jsonify({'success': True, 'result': result})


@network_bp.route('/host-scan', methods=['POST'])
@login_required
def host_scan():
    data = request.get_json() if request.is_json else request.form
    ip = data.get('ip', '').strip()
    port_start = int(data.get('port_start', 1))
    port_end = int(data.get('port_end', 1024))

    if not ip:
        return jsonify({'success': False, 'message': 'IP address is required'}), 400

    port_end = min(port_end, port_start + 999)  # Max 1000 ports per scan
    result = scan_single_host(ip, (port_start, port_end))
    return jsonify({'success': True, 'result': result})
