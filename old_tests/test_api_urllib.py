#!/usr/bin/env python3
"""
나라장터 API 테스트 - urllib 버전
"""

import urllib.request
import urllib.parse
import ssl
import json
from datetime import datetime, timedelta

# SSL 인증서 검증 비활성화
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def test_api():
    """API 테스트"""
    
    # 서비스 키 (URL 인코딩 상태)
    service_key_encoded = "C%2FDmY1C%2F445dB75aJfaKmTWKMKQNQ%2BQiH5D8mlitz%2B1eEqpARlRBYC5qvL11TnVJ86V%2BsJsnJyhLkKPB%2FUAp%2BA%3D%3D"
    
    # 디코딩된 서비스 키
    service_key_decoded = urllib.parse.unquote(service_key_encoded)
    
    print("="*70)
    print("나라장터 API 테스트 (urllib 버전)")
    print("="*70)
    print(f"\n원본 키 (URL 인코딩): {service_key_encoded}")
    print(f"디코딩된 키: {service_key_decoded}")
    
    # 날짜 설정
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # 테스트할 URL 목록
    base_urls = [
        "https://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoCnstwk",
        "https://apis.data.go.kr/1230000/BidPublicInfoService01/getBidPblancListInfoCnstwk",
        "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoCnstwk",
    ]
    
    for base_url in base_urls:
        print(f"\n{'='*60}")
        print(f"테스트 URL: {base_url}")
        print(f"{'='*60}")
        
        # 파라미터 설정 (디코딩된 키 사용)
        params = {
            'serviceKey': service_key_decoded,
            'numOfRows': '10',
            'pageNo': '1',
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M'),
            'type': 'json'
        }
        
        # URL 생성
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"
        
        print(f"전체 URL (처음 200자): {full_url[:200]}...")
        
        try:
            # 요청 보내기
            request = urllib.request.Request(full_url)
            response = urllib.request.urlopen(request, context=ssl_context, timeout=10)
            
            # 응답 읽기
            data = response.read()
            encoding = response.info().get_content_charset('utf-8')
            text = data.decode(encoding)
            
            print(f"✅ 응답 받음! 상태 코드: {response.status}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"응답 길이: {len(text)} 문자")
            
            # JSON 파싱 시도
            try:
                json_data = json.loads(text)
                if 'response' in json_data:
                    header = json_data['response'].get('header', {})
                    result_code = header.get('resultCode', '')
                    result_msg = header.get('resultMsg', '')
                    print(f"결과 코드: {result_code}")
                    print(f"결과 메시지: {result_msg}")
                    
                    if result_code == '00':
                        body = json_data['response'].get('body', {})
                        total_count = body.get('totalCount', 0)
                        print(f"✅ 성공! 총 {total_count}개 결과")
                        return True
                else:
                    print(f"응답 (처음 500자): {text[:500]}")
            except json.JSONDecodeError:
                print(f"JSON 파싱 실패. 응답 (처음 500자): {text[:500]}")
                
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP 에러: {e.code} - {e.reason}")
            try:
                error_data = e.read().decode('utf-8')
                print(f"에러 응답: {error_data[:500]}")
            except:
                pass
                
        except urllib.error.URLError as e:
            print(f"❌ URL 에러: {e.reason}")
            
        except Exception as e:
            print(f"❌ 예외 발생: {type(e).__name__}: {e}")
    
    # 인코딩된 키로도 테스트
    print(f"\n{'='*60}")
    print("URL 인코딩된 키로 재시도")
    print(f"{'='*60}")
    
    base_url = "https://apis.data.go.kr/1230000/BidPublicInfoService/getBidPblancListInfoCnstwk"
    
    # 파라미터 설정 (인코딩된 키 사용)
    params = {
        'serviceKey': service_key_encoded,  # 이미 인코딩된 키 사용
        'numOfRows': '10',
        'pageNo': '1',
        'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
        'inqryEndDt': end_date.strftime('%Y%m%d%H%M'),
        'type': 'json'
    }
    
    # URL 생성 (safe 파라미터로 인코딩 제어)
    query_string = urllib.parse.urlencode(params, safe='%')
    full_url = f"{base_url}?{query_string}"
    
    print(f"전체 URL (처음 200자): {full_url[:200]}...")
    
    try:
        request = urllib.request.Request(full_url)
        response = urllib.request.urlopen(request, context=ssl_context, timeout=10)
        
        data = response.read()
        encoding = response.info().get_content_charset('utf-8')
        text = data.decode(encoding)
        
        print(f"✅ 응답 받음! 상태 코드: {response.status}")
        print(f"응답 (처음 500자): {text[:500]}")
        
    except Exception as e:
        print(f"❌ 예외 발생: {type(e).__name__}: {e}")


if __name__ == "__main__":
    test_api()