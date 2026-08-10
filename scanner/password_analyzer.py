import re
import math
import string
import hashlib
import requests
import logging

logger = logging.getLogger(__name__)

COMMON_PASSWORDS = {
    'password', '123456', '123456789', 'qwerty', 'abc123', 'password1',
    'iloveyou', 'admin', 'welcome', 'monkey', 'dragon', 'master',
    'sunshine', 'princess', 'shadow', 'superman', 'michael', 'football',
    '111111', '1234567', 'letmein', 'trustno1', 'baseball', 'batman'
}

DICTIONARY_WORDS = {
    'hello', 'world', 'test', 'user', 'login', 'pass', 'secure',
    'computer', 'network', 'cyber', 'security', 'hack', 'root', 'admin'
}


def analyze_password(password: str) -> dict:
    result = {
        'password': '*' * len(password),
        'length': len(password),
        'strength': 'weak',
        'strength_score': 0,
        'entropy': 0.0,
        'checks': {},
        'crack_time': {},
        'issues': [],
        'suggestions': [],
        'is_common': False,
        'leaked': False,
        'leaked_count': 0
    }

    if not password:
        result['issues'].append('Password cannot be empty.')
        return result

    # 1. Character set analysis
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?`~]', password))
    has_space = ' ' in password

    result['checks'] = {
        'has_lowercase': has_lower,
        'has_uppercase': has_upper,
        'has_digits': has_digit,
        'has_special': has_special,
        'has_space': has_space,
        'length_ok': len(password) >= 12,
        'no_repeating': not bool(re.search(r'(.)\1{2,}', password)),
        'no_sequential': not _has_sequential(password),
    }

    # 2. Entropy calculation
    charset_size = 0
    if has_lower: charset_size += 26
    if has_upper: charset_size += 26
    if has_digit: charset_size += 10
    if has_special: charset_size += 32
    if has_space: charset_size += 1
    if charset_size == 0: charset_size = 26

    result['entropy'] = round(len(password) * math.log2(charset_size), 2)

    # 3. Strength scoring
    score = 0
    if len(password) >= 8: score += 10
    if len(password) >= 12: score += 15
    if len(password) >= 16: score += 15
    if has_lower: score += 10
    if has_upper: score += 10
    if has_digit: score += 10
    if has_special: score += 20
    if result['entropy'] > 50: score += 10

    if re.search(r'(.)\1{2,}', password): score -= 10
    if _has_sequential(password): score -= 10

    result['strength_score'] = max(0, min(100, score))

    if result['strength_score'] >= 80:
        result['strength'] = 'very_strong'
    elif result['strength_score'] >= 60:
        result['strength'] = 'strong'
    elif result['strength_score'] >= 40:
        result['strength'] = 'moderate'
    elif result['strength_score'] >= 20:
        result['strength'] = 'weak'
    else:
        result['strength'] = 'very_weak'

    # 4. Common password check
    result['is_common'] = password.lower() in COMMON_PASSWORDS
    if result['is_common']:
        result['issues'].append('This is one of the most commonly used passwords.')

    # 5. Dictionary word check
    if password.lower() in DICTIONARY_WORDS:
        result['issues'].append('Password is a common dictionary word.')

    # 6. Crack time estimation
    result['crack_time'] = _estimate_crack_time(result['entropy'])

    # 7. Issues
    if len(password) < 8:
        result['issues'].append('Password is too short (minimum 8 characters).')
    if not has_upper:
        result['issues'].append('Add uppercase letters (A-Z).')
    if not has_lower:
        result['issues'].append('Add lowercase letters (a-z).')
    if not has_digit:
        result['issues'].append('Add numbers (0-9).')
    if not has_special:
        result['issues'].append('Add special characters (!@#$%^&*).')
    if re.search(r'(.)\1{2,}', password):
        result['issues'].append('Avoid repeating characters (aaa, 111).')
    if _has_sequential(password):
        result['issues'].append('Avoid sequential characters (123, abc, qwerty).')

    # 8. Suggestions
    result['suggestions'] = _generate_suggestions(password)

    # 9. HaveIBeenPwned check
    pwned = _check_haveibeenpwned(password)
    result['leaked'] = pwned['found']
    result['leaked_count'] = pwned['count']
    if pwned['found']:
        result['issues'].append(f"This password appears in {pwned['count']:,} known data breaches!")

    return result


def _has_sequential(password: str) -> bool:
    sequences = ['abcdefghijklmnopqrstuvwxyz', '0123456789', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm']
    p = password.lower()
    for seq in sequences:
        for i in range(len(seq) - 2):
            if seq[i:i+3] in p or seq[i:i+3][::-1] in p:
                return True
    return False


def _estimate_crack_time(entropy: float) -> dict:
    # Guesses per second for different attack types
    attack_speeds = {
        'online_slow': 100,
        'online_fast': 10_000,
        'offline_slow': 1_000_000,
        'offline_fast': 1_000_000_000,
        'gpu_cluster': 100_000_000_000,
    }
    total_combinations = 2 ** entropy
    times = {}
    for attack, speed in attack_speeds.items():
        seconds = total_combinations / (speed * 2)  # average case
        times[attack] = _format_time(seconds)
    return times


def _format_time(seconds: float) -> str:
    if seconds < 1:
        return 'Instantly'
    if seconds < 60:
        return f'{int(seconds)} seconds'
    if seconds < 3600:
        return f'{int(seconds/60)} minutes'
    if seconds < 86400:
        return f'{int(seconds/3600)} hours'
    if seconds < 2592000:
        return f'{int(seconds/86400)} days'
    if seconds < 31536000:
        return f'{int(seconds/2592000)} months'
    if seconds < 3153600000:
        return f'{int(seconds/31536000)} years'
    return 'Centuries'


def _generate_suggestions(password: str) -> list:
    suggestions = []
    if len(password) < 16:
        suggestions.append('Increase length to at least 16 characters for stronger security.')
    suggestions.append('Use a passphrase: combine 4+ random words (e.g., Tiger$Blue9Mountain!).')
    suggestions.append('Use a password manager to generate and store unique passwords.')
    suggestions.append('Enable two-factor authentication (2FA) wherever possible.')
    if password.lower() in {password, password.upper()}:
        suggestions.append('Mix uppercase and lowercase letters throughout the password.')
    return suggestions


def _check_haveibeenpwned(password: str) -> dict:
    try:
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        resp = requests.get(
            f'https://api.pwnedpasswords.com/range/{prefix}',
            timeout=5,
            headers={'Add-Padding': 'true'}
        )
        for line in resp.text.splitlines():
            h, count = line.split(':')
            if h == suffix:
                return {'found': True, 'count': int(count)}
        return {'found': False, 'count': 0}
    except Exception as e:
        logger.debug(f"HIBP check error: {e}")
        return {'found': False, 'count': 0}
