#!/usr/bin/env python3
"""
오늘 공고된 나라장터 입찰 정보 조회
"""

import subprocess
import json
from datetime import datetime
from typing import Dict, List
import urllib.parse
import xml.etree.ElementTree as ET


class TodayBidsClient:
    """오늘의 입찰공고 조회 클라이언트"""
    
    def __init__(self, service_key: str):
        self.service_key = service_key
        self.service_key_encoded = urllib.parse.quote(service_key, safe='')
        self.base_url = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService"
        
    def get_today_bids(self, bid_type: str = "all") -> List[Dict]:
        """
        오늘 공고된 입찰 조회
        
        Args:
            bid_type: "servc"(용역), "cnstwk"(건설), "thng"(물품), "all"(전체)
        """
        # 오늘 날짜 설정
        today = datetime.now()
        today_start = today.strftime('%Y%m%d') + '0000'
        today_end = today.strftime('%Y%m%d') + '2359'
        
        all_bids = []
        
        # 조회할 타입 결정
        if bid_type == "all":
            types = ["servc", "cnstwk", "thng"]
        else:
            types = [bid_type]
        
        for type_name in types:
            print(f"\n[{self._get_type_name(type_name)} 입찰공고 조회 중...]")
            
            endpoint = f"{self.base_url}/getBidPblancListInfo{type_name.capitalize()}"
            if type_name == "cnstwk":
                endpoint = f"{self.base_url}/getBidPblancListInfoCnstwk"
            elif type_name == "thng":
                endpoint = f"{self.base_url}/getBidPblancListInfoThng"
            else:
                endpoint = f"{self.base_url}/getBidPblancListInfoServc"
            
            params = {
                'serviceKey': self.service_key_encoded,
                'pageNo': '1',
                'numOfRows': '100',  # 한 번에 100개 조회
                'inqryDiv': '1',
                'inqryBgnDt': today_start,
                'inqryEndDt': today_end
            }
            
            result = self._make_curl_request(endpoint, params)
            
            if result and 'response' in result:
                header = result['response'].get('header', {})
                if header.get('resultCode') == '00':
                    body = result['response'].get('body', {})
                    items = body.get('items', [])
                    
                    # 타입 정보 추가
                    for item in items:
                        item['bidType'] = self._get_type_name(type_name)
                    
                    all_bids.extend(items)
                    print(f"  ✅ {len(items)}개 조회 완료")
                else:
                    print(f"  ❌ 조회 실패: {header.get('resultMsg')}")
        
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
            '--connect-timeout', '30',
            '--max-time', '60'
        ]
        
        try:
            result = subprocess.run(
                curl_command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {'error': f'curl failed: {result.stderr}'}
            
            # JSON 파싱 시도
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                # XML 파싱
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
    
    def print_today_summary(self, bids: List[Dict]) -> None:
        """오늘의 입찰 요약 출력"""
        print("\n" + "="*80)
        print(f"📅 {datetime.now().strftime('%Y년 %m월 %d일')} 공고된 입찰")
        print("="*80)
        
        if not bids:
            print("\n오늘 공고된 입찰이 없습니다.")
            return
        
        print(f"\n총 {len(bids)}개 입찰공고\n")
        
        # 타입별 분류
        by_type = {}
        for bid in bids:
            bid_type = bid.get('bidType', '기타')
            if bid_type not in by_type:
                by_type[bid_type] = []
            by_type[bid_type].append(bid)
        
        # 타입별 출력
        for bid_type, type_bids in by_type.items():
            print(f"\n【{bid_type}】 {len(type_bids)}개")
            print("-" * 80)
            
            # 시간순 정렬 (최신 순)
            type_bids.sort(key=lambda x: x.get('bidNtceDt', ''), reverse=True)
            
            # 상위 10개만 출력
            for idx, bid in enumerate(type_bids[:10], 1):
                self._print_bid_item(idx, bid)
                
            if len(type_bids) > 10:
                print(f"\n   ... 외 {len(type_bids) - 10}개 더 있음")
    
    def _print_bid_item(self, idx: int, bid: Dict) -> None:
        """개별 입찰 항목 출력"""
        # 공고 시간 포맷팅
        bid_time = bid.get('bidNtceDt', '')
        if len(bid_time) >= 19:
            time_str = bid_time[11:16]  # HH:MM 형식
        else:
            time_str = ''
        
        print(f"\n{idx:2d}. [{time_str}] {bid.get('bidNtceNm', 'N/A')}")
        print(f"    📍 {bid.get('dminsttNm', 'N/A')}")
        print(f"    📋 공고번호: {bid.get('bidNtceNo', 'N/A')}")
        
        # 마감일 계산
        close_dt = bid.get('bidClseDt', '')
        if close_dt:
            try:
                close_date = datetime.strptime(close_dt[:10], '%Y-%m-%d')
                days_left = (close_date - datetime.now()).days
                print(f"    ⏰ 마감: {close_dt[:16]} (D-{days_left})")
            except:
                print(f"    ⏰ 마감: {close_dt}")
        
        # 예정가격
        price = bid.get('presmptPrce', '')
        if price and price != 'N/A':
            try:
                price_num = int(price)
                if price_num >= 100000000:  # 1억 이상
                    price_str = f"{price_num/100000000:.1f}억원"
                elif price_num >= 10000000:  # 천만원 이상
                    price_str = f"{price_num/10000000:.0f}천만원"
                else:
                    price_str = f"{price_num:,}원"
                print(f"    💰 예정가격: {price_str}")
            except:
                print(f"    💰 예정가격: {price}")


def main():
    """메인 실행"""
    SERVICE_KEY = "xXw4gHFIYeAF02lry3V2aAO+cBMUlGCCuEE4k5OMX4qAycWqmL4EfrzLl+akDZM85sDGNhI4kcks3ioy+qY/pA=="
    
    client = TodayBidsClient(SERVICE_KEY)
    
    # 오늘 공고된 모든 입찰 조회
    print("오늘 공고된 입찰을 조회합니다...")
    today_bids = client.get_today_bids("all")
    
    # 결과 출력
    client.print_today_summary(today_bids)


if __name__ == "__main__":
    main()