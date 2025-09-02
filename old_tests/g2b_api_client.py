#!/usr/bin/env python3
"""
나라장터 입찰공고정보 API 클라이언트
조달청 G2B (Government to Business) 입찰공고 조회
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import urllib3

# SSL 경고 무시 (개발 환경용)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class G2BClient:
    """나라장터 입찰공고 API 클라이언트"""
    
    def __init__(self, service_key: str):
        """
        초기화
        
        Args:
            service_key: 공공데이터포털에서 발급받은 서비스 키
        """
        self.service_key = service_key
        self.base_url = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService"
        self.session = requests.Session()
        self.session.verify = False  # SSL 검증 비활성화
        
    def get_bid_list_servc(self, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          page_no: int = 1,
                          num_of_rows: int = 10,
                          inqry_div: str = "1") -> Dict:
        """
        용역 입찰공고 목록 조회
        
        Args:
            start_date: 조회 시작일 (기본: 7일 전)
            end_date: 조회 종료일 (기본: 오늘)
            page_no: 페이지 번호
            num_of_rows: 한 페이지 결과 수
            inqry_div: 조회구분 (1: 입찰공고, 2: 사전규격)
            
        Returns:
            API 응답 데이터
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
            
        endpoint = f"{self.base_url}/getBidPblancListInfoServc"
        
        params = {
            'serviceKey': self.service_key,
            'pageNo': str(page_no),
            'numOfRows': str(num_of_rows),
            'inqryDiv': inqry_div,
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M')
        }
        
        return self._make_request(endpoint, params)
    
    def get_bid_list_cnstwk(self, 
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            page_no: int = 1,
                            num_of_rows: int = 10,
                            inqry_div: str = "1") -> Dict:
        """
        건설공사 입찰공고 목록 조회
        
        Args:
            start_date: 조회 시작일 (기본: 7일 전)
            end_date: 조회 종료일 (기본: 오늘)
            page_no: 페이지 번호
            num_of_rows: 한 페이지 결과 수
            inqry_div: 조회구분
            
        Returns:
            API 응답 데이터
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
            
        endpoint = f"{self.base_url}/getBidPblancListInfoCnstwk"
        
        params = {
            'serviceKey': self.service_key,
            'pageNo': str(page_no),
            'numOfRows': str(num_of_rows),
            'inqryDiv': inqry_div,
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M')
        }
        
        return self._make_request(endpoint, params)
    
    def get_bid_list_thng(self, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          page_no: int = 1,
                          num_of_rows: int = 10,
                          inqry_div: str = "1") -> Dict:
        """
        물품 입찰공고 목록 조회
        
        Args:
            start_date: 조회 시작일 (기본: 7일 전)
            end_date: 조회 종료일 (기본: 오늘)
            page_no: 페이지 번호
            num_of_rows: 한 페이지 결과 수
            inqry_div: 조회구분
            
        Returns:
            API 응답 데이터
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
            
        endpoint = f"{self.base_url}/getBidPblancListInfoThng"
        
        params = {
            'serviceKey': self.service_key,
            'pageNo': str(page_no),
            'numOfRows': str(num_of_rows),
            'inqry_div': inqry_div,
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M')
        }
        
        return self._make_request(endpoint, params)
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        API 요청 실행
        
        Args:
            endpoint: API 엔드포인트 URL
            params: 요청 파라미터
            
        Returns:
            API 응답 데이터
        """
        try:
            response = self.session.get(
                endpoint, 
                params=params,
                timeout=30,
                headers={
                    'Accept': 'application/json, application/xml, text/xml, */*',
                    'User-Agent': 'G2B-API-Client/1.0'
                }
            )
            
            response.raise_for_status()
            
            # 응답 형식 확인
            content_type = response.headers.get('Content-Type', '')
            
            if 'json' in content_type:
                return response.json()
            elif 'xml' in content_type:
                # XML 응답 처리 (필요시 구현)
                return {'xml_response': response.text}
            else:
                # 텍스트 응답
                return {'text_response': response.text}
                
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return {'error': str(e)}
        except Exception as e:
            print(f"예외 발생: {e}")
            return {'error': str(e)}
    
    def print_bid_summary(self, data: Dict) -> None:
        """
        입찰 공고 요약 정보 출력
        
        Args:
            data: API 응답 데이터
        """
        if 'error' in data:
            print(f"❌ 에러: {data['error']}")
            return
            
        if 'response' in data:
            header = data['response'].get('header', {})
            result_code = header.get('resultCode', '')
            result_msg = header.get('resultMsg', '')
            
            print(f"결과 코드: {result_code}")
            print(f"결과 메시지: {result_msg}")
            
            if result_code == '00':
                body = data['response'].get('body', {})
                total_count = body.get('totalCount', 0)
                items = body.get('items', [])
                
                print(f"\n총 {total_count}개 입찰공고")
                print("-" * 80)
                
                if isinstance(items, list):
                    for idx, item in enumerate(items[:5], 1):  # 상위 5개만 출력
                        print(f"\n[{idx}] {item.get('bidNtceNm', 'N/A')}")
                        print(f"    공고번호: {item.get('bidNtceNo', 'N/A')}")
                        print(f"    발주기관: {item.get('dminsttNm', 'N/A')}")
                        print(f"    공고일시: {item.get('bidNtceDt', 'N/A')}")
                        print(f"    입찰마감: {item.get('bidClseDt', 'N/A')}")
                        print(f"    예정가격: {item.get('presmptPrce', 'N/A')}")
                elif isinstance(items, dict):
                    # items가 단일 객체인 경우
                    print(f"\n[1] {items.get('bidNtceNm', 'N/A')}")
                    print(f"    공고번호: {items.get('bidNtceNo', 'N/A')}")
                    print(f"    발주기관: {items.get('dminsttNm', 'N/A')}")
                    print(f"    공고일시: {items.get('bidNtceDt', 'N/A')}")
                    print(f"    입찰마감: {items.get('bidClseDt', 'N/A')}")
                    print(f"    예정가격: {items.get('presmptPrce', 'N/A')}")
            else:
                print(f"❌ API 오류: {result_msg}")
        else:
            print("❌ 예상치 못한 응답 형식")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])


def main():
    """메인 실행 함수"""
    # 작동하는 서비스 키 (URL 디코딩된 상태)
    SERVICE_KEY = "xXw4gHFIYeAF02lry3V2aAO+cBMUlGCCuEE4k5OMX4qAycWqmL4EfrzLl+akDZM85sDGNhI4kcks3ioy+qY/pA=="
    
    print("="*80)
    print("나라장터 입찰공고 정보 조회")
    print("="*80)
    
    # 클라이언트 생성
    client = G2BClient(SERVICE_KEY)
    
    # 1. 용역 입찰공고 조회
    print("\n[용역 입찰공고]")
    print("-"*80)
    servc_data = client.get_bid_list_servc(num_of_rows=5)
    client.print_bid_summary(servc_data)
    
    # 2. 건설공사 입찰공고 조회
    print("\n\n[건설공사 입찰공고]")
    print("-"*80)
    cnstwk_data = client.get_bid_list_cnstwk(num_of_rows=5)
    client.print_bid_summary(cnstwk_data)
    
    # 3. 물품 입찰공고 조회
    print("\n\n[물품 입찰공고]")
    print("-"*80)
    thng_data = client.get_bid_list_thng(num_of_rows=5)
    client.print_bid_summary(thng_data)


if __name__ == "__main__":
    main()