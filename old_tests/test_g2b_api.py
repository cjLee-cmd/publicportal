#!/usr/bin/env python3
"""
나라장터 입찰공고정보서비스 API 테스트 및 디버깅 스크립트
조달청 G2B (Government to Business) 입찰공고 API 연동
"""

import requests
import urllib.parse
from datetime import datetime, timedelta
import json
import xml.etree.ElementTree as ET

class G2BAPIClient:
    """나라장터 입찰공고 API 클라이언트"""
    
    def __init__(self, service_key):
        self.service_key = service_key
        # 여러 가능한 base URL 테스트
        self.base_urls = [
            "https://apis.data.go.kr/1230000/BidPublicInfoService",  # 공식 문서 기반
            "https://apis.data.go.kr/1230000/ad/BidPublicInfoService",  # 사용자 제공
            "https://apis.data.go.kr/1230000/BidPublicInfoService01",  # 가능한 버전
        ]
        self.current_base_url = None
        
    def decode_service_key(self):
        """서비스 키 디코딩 확인"""
        print(f"원본 서비스 키 (URL 인코딩): {self.service_key}")
        decoded_key = urllib.parse.unquote(self.service_key)
        print(f"디코딩된 서비스 키: {decoded_key}")
        return decoded_key
    
    def test_endpoints(self):
        """다양한 엔드포인트 테스트"""
        endpoints = [
            "getBidPblancListInfoCnstwk",  # 건설공사 입찰공고
            "getBidPblancListInfoServc",   # 용역 입찰공고
            "getBidPblancListInfoThng",    # 물품 입찰공고
            "getBidPblancListInfoServcPPSSrch",  # 용역 입찰공고(통합검색)
        ]
        
        # 테스트용 파라미터 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'serviceKey': self.service_key,  # URL 인코딩된 키 사용
            'numOfRows': '10',
            'pageNo': '1',
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),  # 조회시작일시 YYYYMMDDhhmm
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M'),    # 조회종료일시 YYYYMMDDhhmm
            'type': 'json'  # 응답 형식
        }
        
        # 디코딩된 키로도 테스트
        decoded_key = urllib.parse.unquote(self.service_key)
        params_decoded = params.copy()
        params_decoded['serviceKey'] = decoded_key
        
        results = []
        
        for base_url in self.base_urls:
            print(f"\n{'='*60}")
            print(f"Base URL 테스트: {base_url}")
            print(f"{'='*60}")
            
            for endpoint in endpoints:
                url = f"{base_url}/{endpoint}"
                print(f"\n테스트 중: {endpoint}")
                print(f"전체 URL: {url}")
                
                # URL 인코딩된 키로 테스트
                print("\n1. URL 인코딩된 서비스 키로 테스트:")
                result = self._make_request(url, params)
                results.append({
                    'base_url': base_url,
                    'endpoint': endpoint,
                    'key_type': 'encoded',
                    'success': result['success'],
                    'response': result
                })
                
                # 디코딩된 키로 테스트
                print("\n2. 디코딩된 서비스 키로 테스트:")
                result = self._make_request(url, params_decoded)
                results.append({
                    'base_url': base_url,
                    'endpoint': endpoint,
                    'key_type': 'decoded',
                    'success': result['success'],
                    'response': result
                })
                
                # 성공한 경우 즉시 반환
                if result['success']:
                    self.current_base_url = base_url
                    print(f"\n✅ 성공! 작동하는 조합 발견:")
                    print(f"   Base URL: {base_url}")
                    print(f"   Endpoint: {endpoint}")
                    print(f"   Key Type: {'decoded' if params_decoded == params else 'encoded'}")
                    return result
        
        return results
    
    def _make_request(self, url, params):
        """실제 API 요청 수행"""
        try:
            # SSL 인증서 검증 비활성화 (개발 환경용)
            import warnings
            from urllib3.exceptions import InsecureRequestWarning
            warnings.filterwarnings('ignore', category=InsecureRequestWarning)
            
            response = requests.get(url, params=params, timeout=10, verify=False)
            print(f"   상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                # 응답 타입 확인
                content_type = response.headers.get('Content-Type', '')
                print(f"   Content-Type: {content_type}")
                
                # JSON 응답 처리
                if 'json' in content_type:
                    data = response.json()
                    if 'response' in data:
                        header = data['response'].get('header', {})
                        result_code = header.get('resultCode', '')
                        result_msg = header.get('resultMsg', '')
                        print(f"   결과 코드: {result_code}")
                        print(f"   결과 메시지: {result_msg}")
                        
                        if result_code == '00':
                            body = data['response'].get('body', {})
                            total_count = body.get('totalCount', 0)
                            print(f"   ✅ 성공! 총 {total_count}개 결과")
                            return {
                                'success': True,
                                'data': data,
                                'total_count': total_count
                            }
                    else:
                        print(f"   ❌ 에러 응답: {data}")
                        
                # XML 응답 처리
                elif 'xml' in content_type:
                    try:
                        root = ET.fromstring(response.text)
                        # OpenAPI 에러 체크
                        error_code = root.find('.//returnAuthMsg')
                        if error_code is not None:
                            print(f"   ❌ 인증 에러: {error_code.text}")
                        else:
                            print(f"   XML 응답 (처음 500자):\n{response.text[:500]}")
                    except:
                        print(f"   응답 내용 (처음 500자):\n{response.text[:500]}")
                else:
                    print(f"   응답 내용 (처음 500자):\n{response.text[:500]}")
                    
            else:
                print(f"   ❌ HTTP 에러 {response.status_code}")
                print(f"   응답: {response.text[:500]}")
                
            return {
                'success': False,
                'status_code': response.status_code,
                'response_text': response.text[:1000]
            }
            
        except requests.exceptions.Timeout:
            print(f"   ❌ 요청 시간 초과")
            return {'success': False, 'error': 'Timeout'}
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 요청 실패: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"   ❌ 예외 발생: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_bid_list(self, endpoint_type='cnstwk'):
        """입찰 공고 목록 조회"""
        if not self.current_base_url:
            print("먼저 test_endpoints()를 실행하여 작동하는 엔드포인트를 찾아주세요.")
            return None
            
        endpoint_map = {
            'cnstwk': 'getBidPblancListInfoCnstwk',  # 건설공사
            'servc': 'getBidPblancListInfoServc',     # 용역
            'thng': 'getBidPblancListInfoThng',       # 물품
        }
        
        endpoint = endpoint_map.get(endpoint_type, 'getBidPblancListInfoCnstwk')
        url = f"{self.current_base_url}/{endpoint}"
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'serviceKey': urllib.parse.unquote(self.service_key),  # 디코딩된 키 사용
            'numOfRows': '100',
            'pageNo': '1',
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M'),
            'type': 'json'
        }
        
        result = self._make_request(url, params)
        if result['success']:
            return result['data']
        return None


def main():
    """메인 실행 함수"""
    # 제공된 서비스 키 (URL 인코딩 상태)
    SERVICE_KEY = "C%2FDmY1C%2F445dB75aJfaKmTWKMKQNQ%2BQiH5D8mlitz%2B1eEqpARlRBYC5qvL11TnVJ86V%2BsJsnJyhLkKPB%2FUAp%2BA%3D%3D"
    
    print("="*70)
    print("나라장터 입찰공고정보서비스 API 테스트")
    print("="*70)
    
    # API 클라이언트 생성
    client = G2BAPIClient(SERVICE_KEY)
    
    # 서비스 키 확인
    print("\n[1단계] 서비스 키 확인")
    print("-"*60)
    client.decode_service_key()
    
    # 엔드포인트 테스트
    print("\n[2단계] 모든 가능한 엔드포인트 조합 테스트")
    print("-"*60)
    result = client.test_endpoints()
    
    # 결과가 성공적이면 실제 데이터 조회
    if isinstance(result, dict) and result.get('success'):
        print("\n[3단계] 실제 입찰 공고 데이터 조회")
        print("-"*60)
        
        for bid_type in ['cnstwk', 'servc', 'thng']:
            print(f"\n{bid_type} 입찰 공고 조회 중...")
            data = client.get_bid_list(bid_type)
            if data:
                body = data['response']['body']
                items = body.get('items', [])
                if items:
                    print(f"조회 성공! {len(items)}개 공고 발견")
                    # 첫 번째 공고 정보 출력
                    if len(items) > 0:
                        first_item = items[0] if isinstance(items, list) else items
                        print(f"첫 번째 공고 예시:")
                        for key, value in list(first_item.items())[:5]:
                            print(f"  - {key}: {value}")
    else:
        print("\n❌ 모든 엔드포인트 테스트 실패")
        print("\n가능한 해결 방법:")
        print("1. data.go.kr에서 서비스 활용 신청 상태 확인")
        print("2. 서비스 키가 해당 API에 대해 활성화되어 있는지 확인")
        print("3. API 서비스가 현재 정상 운영 중인지 확인")
        print("4. 서비스 키 재발급 고려")


if __name__ == "__main__":
    main()