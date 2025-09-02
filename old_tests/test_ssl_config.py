#!/usr/bin/env python3
"""
나라장터 API - SSL/TLS 설정 테스트
"""

import requests
import ssl
import socket
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

class SSLAdapter(HTTPAdapter):
    """Custom SSL Adapter with different TLS versions"""
    def __init__(self, ssl_version=None, **kwargs):
        self.ssl_version = ssl_version
        super().__init__(**kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        if self.ssl_version:
            context.minimum_version = self.ssl_version
            context.maximum_version = self.ssl_version
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

def test_ssl_versions():
    """다양한 SSL/TLS 버전으로 테스트"""
    
    service_key = "C/DmY1C/445dB75aJfaKmTWKMKQNQ+QiH5D8mlitz+1eEqpARlRBYC5qvL11TnVJ86V+sJsnJyhLkKPB/UAp+A=="
    
    # 테스트할 URL
    test_urls = [
        "https://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoCnstwk",
        "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoCnstwk",
    ]
    
    # 간단한 파라미터
    params = {
        'serviceKey': service_key,
        'pageNo': '1',
        'numOfRows': '1'
    }
    
    print("="*70)
    print("SSL/TLS 버전별 테스트")
    print("="*70)
    
    # 다양한 TLS 버전 테스트
    tls_versions = [
        (None, "Default"),
        (ssl.TLSVersion.TLSv1_2, "TLS 1.2"),
        (ssl.TLSVersion.TLSv1_3, "TLS 1.3"),
    ]
    
    for url in test_urls:
        print(f"\n테스트 URL: {url}")
        print("-"*60)
        
        for tls_version, version_name in tls_versions:
            print(f"\n{version_name} 테스트:")
            
            session = requests.Session()
            adapter = SSLAdapter(ssl_version=tls_version)
            session.mount('https://', adapter)
            
            # 경고 무시
            import warnings
            warnings.filterwarnings('ignore')
            
            try:
                response = session.get(url, params=params, timeout=10)
                print(f"  ✅ 성공! 상태 코드: {response.status_code}")
                print(f"  응답 (처음 200자): {response.text[:200]}")
                
            except requests.exceptions.SSLError as e:
                print(f"  ❌ SSL 에러: {str(e)[:100]}")
            except requests.exceptions.Timeout:
                print(f"  ❌ 타임아웃")
            except Exception as e:
                print(f"  ❌ 에러: {type(e).__name__}: {str(e)[:100]}")
            
            session.close()

def check_server_ssl():
    """서버의 SSL 인증서 정보 확인"""
    print("\n" + "="*70)
    print("서버 SSL 인증서 정보")
    print("="*70)
    
    hostname = 'apis.data.go.kr'
    port = 443
    
    try:
        # SSL 컨텍스트 생성
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # 서버에 연결
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"SSL 버전: {ssock.version()}")
                print(f"암호화 방식: {ssock.cipher()}")
                
                # 인증서 정보
                cert = ssock.getpeercert()
                if cert:
                    print("인증서 정보 있음")
                else:
                    print("인증서 정보 없음 (검증 비활성화)")
                    
    except Exception as e:
        print(f"SSL 정보 확인 실패: {e}")

if __name__ == "__main__":
    check_server_ssl()
    test_ssl_versions()