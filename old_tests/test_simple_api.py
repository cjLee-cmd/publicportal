#!/usr/bin/env python3
"""
나라장터 API 단순 테스트
"""

import requests
import json
from datetime import datetime, timedelta

# SSL 경고 무시
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_simple():
    """단순 API 테스트"""
    
    # 서비스 키
    service_key = "C/DmY1C/445dB75aJfaKmTWKMKQNQ+QiH5D8mlitz+1eEqpARlRBYC5qvL11TnVJ86V+sJsnJyhLkKPB/UAp+A=="
    
    # 날짜 설정
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 기본 URL - data.go.kr에서 확인한 정확한 URL
    base_url = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoCnstwk"
    
    # 필수 파라미터만 사용
    params = {
        'serviceKey': service_key,
        'pageNo': '1',
        'numOfRows': '10',
        'inqryDiv': '1',  # 조회 구분 추가
        'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
        'inqryEndDt': end_date.strftime('%Y%m%d%H%M')
    }
    
    print("="*70)
    print("나라장터 API 단순 테스트")
    print("="*70)
    print(f"\nURL: {base_url}")
    print(f"파라미터:")
    for key, value in params.items():
        if key == 'serviceKey':
            print(f"  {key}: {value[:20]}...{value[-20:]}")
        else:
            print(f"  {key}: {value}")
    
    try:
        # 요청 보내기
        print("\n요청 전송 중...")
        response = requests.get(
            base_url, 
            params=params, 
            verify=False,  # SSL 검증 비활성화
            timeout=30,     # 타임아웃 30초로 증가
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/xml, */*',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8'
            }
        )
        
        print(f"상태 코드: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        
        if response.status_code == 200:
            # 응답 내용 확인
            if 'json' in response.headers.get('Content-Type', ''):
                data = response.json()
                print(f"✅ JSON 응답 수신")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            else:
                # XML 또는 다른 형식
                print(f"응답 내용 (처음 1000자):")
                print(response.text[:1000])
        else:
            print(f"❌ HTTP 에러: {response.status_code}")
            print(f"응답: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과 (30초)")
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL 에러: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 에러: {e}")
    except Exception as e:
        print(f"❌ 예외: {type(e).__name__}: {e}")


if __name__ == "__main__":
    test_simple()