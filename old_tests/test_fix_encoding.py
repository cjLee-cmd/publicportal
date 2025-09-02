#!/usr/bin/env python3
"""
나라장터 API - 인코딩 문제 해결
"""

import requests
import urllib.parse
import base64

def test_encoding_solutions():
    """다양한 인코딩 해결 방법 테스트"""
    
    # 원본 서비스 키
    service_key_encoded = "C%2FDmY1C%2F445dB75aJfaKmTWKMKQNQ%2BQiH5D8mlitz%2B1eEqpARlRBYC5qvL11TnVJ86V%2BsJsnJyhLkKPB%2FUAp%2BA%3D%3D"
    service_key_decoded = urllib.parse.unquote(service_key_encoded)
    
    print("="*70)
    print("서비스 키 인코딩 문제 해결 테스트")
    print("="*70)
    print(f"\n원본 (URL 인코딩): {service_key_encoded}")
    print(f"디코딩: {service_key_decoded}")
    print(f"키 길이: {len(service_key_decoded)} 문자")
    
    # Base64 디코딩 시도 (서비스 키가 Base64인 경우)
    try:
        decoded_bytes = base64.b64decode(service_key_decoded)
        print(f"Base64 디코딩 성공: {len(decoded_bytes)} 바이트")
        print(f"실제 키 (처음 20자): {decoded_bytes[:20]}")
    except:
        print("Base64 디코딩 실패 - 올바른 Base64 형식이 아님")
    
    # 테스트 URL
    base_url = "https://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoCnstwk"
    
    print("\n" + "="*70)
    print("해결 방법 테스트")
    print("="*70)
    
    # 방법 1: POST 요청으로 변경 (URL 길이 문제 회피)
    print("\n1. POST 요청 사용:")
    try:
        data = {
            'serviceKey': service_key_decoded,
            'pageNo': '1',
            'numOfRows': '10'
        }
        response = requests.post(base_url, data=data, timeout=10, verify=False)
        print(f"   상태 코드: {response.status_code}")
        if response.status_code != 200:
            print(f"   응답: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 실패: {str(e)[:100]}")
    
    # 방법 2: 헤더에 서비스 키 전달
    print("\n2. 헤더에 서비스 키 전달:")
    try:
        headers = {
            'Authorization': f'Bearer {service_key_decoded}',
            'X-API-Key': service_key_decoded
        }
        params = {
            'pageNo': '1',
            'numOfRows': '10'
        }
        response = requests.get(base_url, params=params, headers=headers, timeout=10, verify=False)
        print(f"   상태 코드: {response.status_code}")
        if response.status_code != 200:
            print(f"   응답: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 실패: {str(e)[:100]}")
    
    # 방법 3: 서비스 키를 쿼리 파라미터가 아닌 경로에 포함
    print("\n3. 경로에 서비스 키 포함:")
    try:
        # 일부 API는 이런 형식을 사용
        alt_url = f"https://apis.data.go.kr/1230000/BidPublicInfoService/{service_key_encoded}/getBidPblancListInfoCnstwk"
        params = {
            'pageNo': '1',
            'numOfRows': '10'
        }
        response = requests.get(alt_url, params=params, timeout=10, verify=False)
        print(f"   상태 코드: {response.status_code}")
        if response.status_code != 200:
            print(f"   응답: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 실패: {str(e)[:100]}")
    
    # 방법 4: 수동으로 URL 구성 (이중 인코딩 방지)
    print("\n4. 수동 URL 구성 (이중 인코딩 방지):")
    try:
        # URL을 직접 구성
        manual_url = f"{base_url}?serviceKey={service_key_encoded}&pageNo=1&numOfRows=10"
        print(f"   URL: {manual_url[:150]}...")
        
        # Session 사용하여 연결 재사용
        session = requests.Session()
        session.verify = False
        
        response = session.get(manual_url, timeout=10)
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 성공!")
            print(f"   응답: {response.text[:300]}")
        else:
            print(f"   응답: {response.text[:200]}")
            
        session.close()
    except Exception as e:
        print(f"   ❌ 실패: {str(e)[:100]}")

    # 방법 5: 짧은 서비스 키로 테스트 (키 자체가 문제인지 확인)
    print("\n5. 테스트용 짧은 키 사용:")
    try:
        test_key = "TEST_KEY_12345"  # 짧은 테스트 키
        params = {
            'serviceKey': test_key,
            'pageNo': '1',
            'numOfRows': '10'
        }
        response = requests.get(base_url, params=params, timeout=10, verify=False)
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {response.text[:200]}")
        if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in response.text:
            print("   ✅ 서버 연결 성공! (키는 유효하지 않지만 SSL 문제는 해결)")
    except Exception as e:
        print(f"   ❌ 실패: {str(e)[:100]}")

if __name__ == "__main__":
    # 경고 무시
    import warnings
    warnings.filterwarnings('ignore')
    
    test_encoding_solutions()