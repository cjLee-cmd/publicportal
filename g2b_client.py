#!/usr/bin/env python3
"""
나라장터 입찰공고정보 API 클라이언트
Consolidated and cleaned version using curl subprocess approach
"""

import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import urllib.parse
import xml.etree.ElementTree as ET
from config import SERVICE_KEY, BASE_URL, CONNECT_TIMEOUT, MAX_TIMEOUT


class G2BClient:
    """나라장터 API 통합 클라이언트"""
    
    def __init__(self, service_key: str = SERVICE_KEY):
        self.service_key = service_key
        self.service_key_encoded = urllib.parse.quote(service_key, safe='')
        self.base_url = BASE_URL
        
    def get_bid_list(self,
                     bid_type: str = "servc",
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     page_no: int = 1,
                     num_of_rows: int = 10,
                     inqry_div: str = "1") -> Dict:
        """
        입찰공고 목록 조회
        
        Args:
            bid_type: "servc"(용역), "cnstwk"(건설), "thng"(물품)
            start_date: 조회 시작일
            end_date: 조회 종료일
            page_no: 페이지 번호
            num_of_rows: 한 페이지 결과 수
            inqry_div: 조회구분 (1: 입찰공고)
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
            
        # Endpoint mapping
        endpoint_map = {
            'servc': 'getBidPblancListInfoServc',
            'cnstwk': 'getBidPblancListInfoCnstwk',
            'thng': 'getBidPblancListInfoThng'
        }
        
        endpoint = f"{self.base_url}/{endpoint_map.get(bid_type, 'getBidPblancListInfoServc')}"
        
        params = {
            'serviceKey': self.service_key_encoded,
            'pageNo': str(page_no),
            'numOfRows': str(num_of_rows),
            'inqryDiv': inqry_div,
            'inqryBgnDt': start_date.strftime('%Y%m%d%H%M'),
            'inqryEndDt': end_date.strftime('%Y%m%d%H%M')
        }
        
        return self._make_curl_request(endpoint, params)
    
    def get_today_bids(self, bid_type: str = "all") -> List[Dict]:
        """
        오늘 공고된 입찰 조회
        
        Args:
            bid_type: "servc", "cnstwk", "thng", "all"(전체)
        """
        today = datetime.now()
        today_start = today.strftime('%Y%m%d') + '0000'
        today_end = today.strftime('%Y%m%d') + '2359'
        
        all_bids = []
        types = [bid_type] if bid_type != "all" else ["servc", "cnstwk", "thng"]
        
        for type_name in types:
            print(f"\n[{self._get_type_name(type_name)} 입찰공고 조회 중...]")
            
            result = self.get_bid_list(
                bid_type=type_name,
                start_date=datetime.strptime(today_start, '%Y%m%d%H%M'),
                end_date=datetime.strptime(today_end, '%Y%m%d%H%M'),
                num_of_rows=100
            )
            
            if result and 'response' in result:
                header = result['response'].get('header', {})
                if header.get('resultCode') == '00':
                    body = result['response'].get('body', {})
                    items = body.get('items', [])
                    
                    for item in items:
                        item['bidType'] = self._get_type_name(type_name)
                    
                    all_bids.extend(items)
                    print(f"  ✅ {len(items)}개 조회 완료")
        
        return all_bids
    
    def _get_type_name(self, type_code: str) -> str:
        """타입 코드를 한글명으로 변환"""
        type_names = {
            'servc': '용역',
            'cnstwk': '건설공사',
            'thng': '물품'
        }
        return type_names.get(type_code, type_code)
    
    def _make_curl_request(self, endpoint: str, params: Dict) -> Dict:
        """curl을 사용한 API 요청"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{endpoint}?{query_string}"
        
        curl_command = [
            'curl', '-X', 'GET', full_url,
            '-H', 'accept: */*',
            '--silent',
            '--connect-timeout', str(CONNECT_TIMEOUT),
            '--max-time', str(MAX_TIMEOUT)
        ]
        
        try:
            result = subprocess.run(
                curl_command,
                capture_output=True,
                text=True,
                timeout=MAX_TIMEOUT
            )
            
            if result.returncode != 0:
                return {'error': f'curl failed: {result.stderr}'}
            
            # Try JSON first, then XML
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return self._parse_xml_response(result.stdout)
                
        except Exception as e:
            return {'error': str(e)}
    
    def _parse_xml_response(self, xml_string: str) -> Dict:
        """XML 응답 파싱"""
        try:
            root = ET.fromstring(xml_string)
            
            header = root.find('header')
            header_data = {}
            if header is not None:
                header_data = {
                    'resultCode': header.findtext('resultCode', ''),
                    'resultMsg': header.findtext('resultMsg', '')
                }
            
            body = root.find('body')
            body_data = {}
            if body is not None:
                total_count = body.findtext('totalCount', '0')
                body_data['totalCount'] = total_count
                
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
        except Exception as e:
            return {'error': f'XML parsing failed: {str(e)}'}
    
    def print_bid_summary(self, data: Dict) -> None:
        """입찰 공고 요약 정보 출력"""
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
                
                print(f"\n✅ 총 {total_count}개 입찰공고")
                print("-" * 80)
                
                for idx, item in enumerate(items[:5], 1):
                    self._print_bid_item(idx, item)
            else:
                print(f"❌ API 오류: {result_msg}")
    
    def _print_bid_item(self, idx: int, bid: Dict) -> None:
        """개별 입찰 항목 출력"""
        bid_time = bid.get('bidNtceDt', '')
        if len(bid_time) >= 19:
            time_str = bid_time[11:16]
        else:
            time_str = ''
        
        print(f"\n{idx:2d}. [{time_str}] {bid.get('bidNtceNm', 'N/A')}")
        print(f"    📍 {bid.get('dminsttNm', 'N/A')}")
        print(f"    📋 공고번호: {bid.get('bidNtceNo', 'N/A')}")
        
        close_dt = bid.get('bidClseDt', '')
        if close_dt:
            try:
                close_date = datetime.strptime(close_dt[:10], '%Y-%m-%d')
                days_left = (close_date - datetime.now()).days
                print(f"    ⏰ 마감: {close_dt[:16]} (D-{days_left})")
            except:
                print(f"    ⏰ 마감: {close_dt}")
        
        price = bid.get('presmptPrce', '')
        if price and price != 'N/A':
            try:
                price_num = int(price)
                if price_num >= 100000000:
                    price_str = f"{price_num/100000000:.1f}억원"
                elif price_num >= 10000000:
                    price_str = f"{price_num/10000000:.0f}천만원"
                else:
                    price_str = f"{price_num:,}원"
                print(f"    💰 예정가격: {price_str}")
            except:
                pass


def main():
    """메인 실행"""
    client = G2BClient()
    
    print("="*80)
    print("나라장터 입찰공고 정보 조회")
    print("="*80)
    
    # 최근 입찰공고 조회
    print("\n[최근 용역 입찰공고]")
    servc_data = client.get_bid_list("servc", num_of_rows=5)
    client.print_bid_summary(servc_data)


if __name__ == "__main__":
    main()