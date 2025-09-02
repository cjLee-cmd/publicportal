#!/usr/bin/env python3
"""
나라장터 입찰공고 조회 메인 애플리케이션
"""

import sys
from datetime import datetime
from g2b_client import G2BClient


def show_menu():
    """메뉴 표시"""
    print("\n" + "="*60)
    print("나라장터 입찰공고 조회 시스템")
    print("="*60)
    print("1. 오늘 공고된 입찰 조회")
    print("2. 최근 용역 입찰공고 조회")
    print("3. 최근 건설공사 입찰공고 조회")
    print("4. 최근 물품 입찰공고 조회")
    print("0. 종료")
    print("-"*60)


def main():
    """메인 실행"""
    client = G2BClient()
    
    while True:
        show_menu()
        choice = input("선택하세요: ").strip()
        
        if choice == "0":
            print("프로그램을 종료합니다.")
            break
            
        elif choice == "1":
            print("\n오늘 공고된 입찰을 조회합니다...")
            bids = client.get_today_bids("all")
            
            if bids:
                print(f"\n📅 {datetime.now().strftime('%Y년 %m월 %d일')} 공고된 입찰")
                print(f"총 {len(bids)}개 입찰공고\n")
                
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
                    print("-" * 60)
                    
                    for idx, bid in enumerate(type_bids[:5], 1):
                        client._print_bid_item(idx, bid)
                    
                    if len(type_bids) > 5:
                        print(f"\n   ... 외 {len(type_bids) - 5}개 더 있음")
            else:
                print("오늘 공고된 입찰이 없습니다.")
                
        elif choice == "2":
            print("\n[용역 입찰공고 조회]")
            data = client.get_bid_list("servc", num_of_rows=10)
            client.print_bid_summary(data)
            
        elif choice == "3":
            print("\n[건설공사 입찰공고 조회]")
            data = client.get_bid_list("cnstwk", num_of_rows=10)
            client.print_bid_summary(data)
            
        elif choice == "4":
            print("\n[물품 입찰공고 조회]")
            data = client.get_bid_list("thng", num_of_rows=10)
            client.print_bid_summary(data)
            
        else:
            print("잘못된 선택입니다. 다시 선택해주세요.")
        
        input("\n계속하려면 Enter를 누르세요...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        sys.exit(0)