#!/usr/bin/env python3
"""
나라장터 API - curl을 사용한 우회 방법
SSL 문제를 피하기 위해 시스템 curl 명령 사용
"""

import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import urllib.parse
import xml.etree.ElementTree as ET


class G2BCurlClient:
    """curl을 사용한 나라장터 API 클라이언트"""
    
    def __init__(self, service_key: str):
        """
        초기화
        
        Args:
            service_key: 공공데이터포털 서비스 키 (디코딩된 상태)
        """
        self.service_key = service_key
        # URL 인코딩된 서비스 키
        self.service_key_encoded = urllib.parse.quote(service_key, safe='')
        self.base_url = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService"
        
    def get_bid_list_servc(self,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          page_no: int = 1,
                          num_of_rows: int = 10,
                          inqry_div: str = "1") -> Dict:
        """
        용역 입찰공고 목록 조회
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
            
        endpoint = f"{self.base_url}/getBidPblancListInfoServc"
        
        params = {
            'serviceKey': self.service_key_encoded,
            'pageNo': str(page_no),
            'numOfRows': str(num_of_rows),
            'inqryDiv': inqry_div,
            # 필수 날짜 파라미터 추가
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M')
        }
        
        return self._make_curl_request(endpoint, params)
    
    def get_bid_list_cnstwk(self,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            page_no: int = 1,
                            num_of_rows: int = 10,
                            inqry_div: str = "1") -> Dict:
        """
        건설공사 입찰공고 목록 조회
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
            
        endpoint = f"{self.base_url}/getBidPblancListInfoCnstwk"
        
        params = {
            'serviceKey': self.service_key_encoded,
            'pageNo': str(page_no),
            'numOfRows': str(num_of_rows),
            'inqryDiv': inqry_div,
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M')
        }
        
        return self._make_curl_request(endpoint, params)
    
    def get_bid_list_thng(self,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         page_no: int = 1,
                         num_of_rows: int = 10,
                         inqry_div: str = "1") -> Dict:
        """
        물품 입찰공고 목록 조회
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
            
        endpoint = f"{self.base_url}/getBidPblancListInfoThng"
        
        params = {
            'serviceKey': self.service_key_encoded,
            'pageNo': str(page_no),
            'numOfRows': str(num_of_rows),
            'inqryDiv': inqry_div,
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M')
        }
        
        return self._make_curl_request(endpoint, params)
    
    def _make_curl_request(self, endpoint: str, params: Dict) -> Dict:
        """
        curl 명령을 사용하여 API 요청
        """
        # URL 파라미터 생성
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{endpoint}?{query_string}"
        
        # curl 명령 구성
        curl_command = [
            'curl',
            '-X', 'GET',
            full_url,
            '-H', 'accept: */*',
            '--silent',  # 진행 상황 출력 안함
            '--connect-timeout', '30',
            '--max-time', '60'
        ]
        
        try:
            print(f"요청 중: {endpoint.split('/')[-1]}")
            
            # curl 실행
            result = subprocess.run(
                curl_command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"curl 실행 실패: {result.stderr}")
                return {'error': f'curl failed: {result.stderr}'}
            
            # JSON 파싱 시도
            try:
                response_data = json.loads(result.stdout)
                return response_data
            except json.JSONDecodeError:
                # XML 응답인 경우 파싱
                try:
                    return self._parse_xml_response(result.stdout)
                except Exception as e:
                    print(f"XML 파싱 실패: {e}")
                    return {'xml_response': result.stdout[:1000]}
                
        except subprocess.TimeoutExpired:
            print("요청 시간 초과")
            return {'error': 'Request timeout'}
        except Exception as e:
            print(f"오류 발생: {e}")
            return {'error': str(e)}
    
    def _parse_xml_response(self, xml_string: str) -> Dict:
        """
        XML 응답을 JSON 형식으로 변환
        """
        root = ET.fromstring(xml_string)
        
        # 헤더 정보 파싱
        header = root.find('header')
        header_data = {}
        if header is not None:
            header_data = {
                'resultCode': header.findtext('resultCode', ''),
                'resultMsg': header.findtext('resultMsg', '')
            }
        
        # 바디 정보 파싱
        body = root.find('body')
        body_data = {}
        if body is not None:
            # 총 개수
            total_count = body.findtext('totalCount', '0')
            body_data['totalCount'] = total_count
            
            # 아이템 목록
            items = body.find('items')
            items_list = []
            if items is not None:
                for item in items.findall('item'):
                    item_dict = {}
                    for child in item:
                        item_dict[child.tag] = child.text
                    items_list.append(item_dict)
            
            body_data['items'] = items_list
        
        return {
            'response': {
                'header': header_data,
                'body': body_data
            }
        }
    
    def print_bid_summary(self, data: Dict) -> None:
        """
        입찰 공고 요약 정보 출력
        """
        if 'error' in data:
            print(f"❌ 에러: {data['error']}")
            return
            
        if 'xml_response' in data:
            print("📄 XML 응답 (처음 500자):")
            print(data['xml_response'][:500])
            return
            
        if 'response' in data:
            header = data['response'].get('header', {})
            result_code = header.get('resultCode', '')
            result_msg = header.get('resultMsg', '')
            
            print(f"결과 코드: {result_code}")
            print(f"결과 메시지: {result_msg}")
            
            if result_code == '00' or result_code == '0':
                body = data['response'].get('body', {})
                total_count = body.get('totalCount', 0)
                items = body.get('items', [])
                
                print(f"\n✅ 총 {total_count}개 입찰공고 조회 성공")
                print("-" * 80)
                
                # items 처리
                if items:
                    if isinstance(items, dict) and 'item' in items:
                        items = items['item']
                    
                    if isinstance(items, list):
                        for idx, item in enumerate(items[:5], 1):
                            self._print_bid_item(idx, item)
                    elif isinstance(items, dict):
                        self._print_bid_item(1, items)
                else:
                    print("조회된 입찰공고가 없습니다.")
            else:
                print(f"❌ API 오류: {result_msg}")
        else:
            print("❌ 예상치 못한 응답 형식")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
    
    def _print_bid_item(self, idx: int, item: Dict) -> None:
        """개별 입찰 항목 출력"""
        print(f"\n[{idx}] {item.get('bidNtceNm', item.get('BidNtceNm', 'N/A'))}")
        print(f"    공고번호: {item.get('bidNtceNo', item.get('BidNtceNo', 'N/A'))}")
        print(f"    발주기관: {item.get('dminsttNm', item.get('DminsttNm', 'N/A'))}")
        print(f"    공고일시: {item.get('bidNtceDt', item.get('BidNtceDt', 'N/A'))}")
        print(f"    입찰마감: {item.get('bidClseDt', item.get('BidClseDt', 'N/A'))}")
        
        # 예정가격 (숫자 포맷팅)
        price = item.get('presmptPrce', item.get('PresmptPrce', 'N/A'))
        if price != 'N/A' and price:
            try:
                price_num = int(price)
                price = f"{price_num:,}원"
            except:
                pass
        print(f"    예정가격: {price}")


def main():
    """메인 실행 함수"""
    # 작동하는 서비스 키 (디코딩된 상태)
    SERVICE_KEY = "xXw4gHFIYeAF02lry3V2aAO+cBMUlGCCuEE4k5OMX4qAycWqmL4EfrzLl+akDZM85sDGNhI4kcks3ioy+qY/pA=="
    
    print("="*80)
    print("나라장터 입찰공고 정보 조회 (curl 사용)")
    print("="*80)
    
    # 클라이언트 생성
    client = G2BCurlClient(SERVICE_KEY)
    
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