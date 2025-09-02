#!/usr/bin/env python3
"""
나라장터 입찰공고 조회 웹 애플리케이션
Flask 백엔드 API 서버
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from g2b_client import G2BClient

app = Flask(__name__)
CORS(app)

# 글로벌 변수
g2b_client = G2BClient()
current_bids = []

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_bids():
    """입찰공고 검색 API"""
    try:
        data = request.get_json()
        
        # 파라미터 추출
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        bid_type = data.get('bid_type', 'all')
        agency_filter = data.get('agency_filter', '')
        
        # 날짜 파싱
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_dt = datetime.now() - timedelta(days=7)
            
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59)
        else:
            end_dt = datetime.now()
        
        # 입찰공고 조회
        global current_bids
        current_bids = []
        
        # 조회할 타입 결정
        if bid_type == 'all':
            types = ['servc', 'cnstwk', 'thng']
        else:
            types = [bid_type]
        
        for type_name in types:
            result = g2b_client.get_bid_list(
                bid_type=type_name,
                start_date=start_dt,
                end_date=end_dt,
                num_of_rows=100
            )
            
            if result and 'response' in result:
                header = result['response'].get('header', {})
                if header.get('resultCode') == '00':
                    body = result['response'].get('body', {})
                    items = body.get('items', [])
                    
                    # 데이터 가공
                    for item in items:
                        bid_data = {
                            'id': f"{type_name}_{item.get('bidNtceNo', '')}",
                            'bidType': g2b_client._get_type_name(type_name),
                            'bidNtceNo': item.get('bidNtceNo', ''),
                            'bidNtceNm': item.get('bidNtceNm', ''),
                            'dminsttNm': item.get('dminsttNm', ''),
                            'bidNtceDt': item.get('bidNtceDt', ''),
                            'bidClseDt': item.get('bidClseDt', ''),
                            'presmptPrce': item.get('presmptPrce', ''),
                            'bidNtceUrl': item.get('bidNtceUrl', ''),
                            'ntceInsttNm': item.get('ntceInsttNm', ''),
                        }
                        
                        # 기관 필터링
                        if agency_filter and agency_filter != 'all':
                            if agency_filter not in bid_data['dminsttNm']:
                                continue
                        
                        current_bids.append(bid_data)
        
        # 날짜순 정렬 (최신순)
        current_bids.sort(key=lambda x: x.get('bidNtceDt', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'data': current_bids,
            'count': len(current_bids)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agencies')
def get_agencies():
    """기관 목록 조회 API"""
    try:
        # 최근 데이터에서 기관 목록 추출
        agencies = set()
        
        # 샘플 데이터로 최근 입찰공고에서 기관 목록을 추출
        for type_name in ['servc', 'cnstwk', 'thng']:
            result = g2b_client.get_bid_list(
                bid_type=type_name,
                num_of_rows=50
            )
            
            if result and 'response' in result:
                header = result['response'].get('header', {})
                if header.get('resultCode') == '00':
                    body = result['response'].get('body', {})
                    items = body.get('items', [])
                    
                    for item in items:
                        agency = item.get('dminsttNm', '').strip()
                        if agency:
                            agencies.add(agency)
        
        agency_list = sorted(list(agencies))
        
        return jsonify({
            'success': True,
            'agencies': agency_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export/excel', methods=['POST'])
def export_excel():
    """Excel 내보내기 API"""
    try:
        data = request.get_json()
        selected_ids = data.get('selected_ids', [])
        
        # 선택된 항목 필터링
        if selected_ids:
            export_data = [bid for bid in current_bids if bid['id'] in selected_ids]
        else:
            export_data = current_bids
        
        if not export_data:
            return jsonify({
                'success': False,
                'error': '내보낼 데이터가 없습니다.'
            }), 400
        
        # DataFrame 생성
        df_data = []
        for bid in export_data:
            # 가격 포맷팅
            price = bid.get('presmptPrce', '')
            if price and price != 'N/A':
                try:
                    price_num = int(price)
                    if price_num >= 100000000:
                        price_formatted = f"{price_num/100000000:.1f}억원"
                    elif price_num >= 10000000:
                        price_formatted = f"{price_num/10000000:.0f}천만원"
                    else:
                        price_formatted = f"{price_num:,}원"
                except:
                    price_formatted = price
            else:
                price_formatted = ''
            
            df_data.append({
                '구분': bid.get('bidType', ''),
                '공고번호': bid.get('bidNtceNo', ''),
                '공고명': bid.get('bidNtceNm', ''),
                '발주기관': bid.get('dminsttNm', ''),
                '공고일시': bid.get('bidNtceDt', ''),
                '마감일시': bid.get('bidClseDt', ''),
                '예정가격': price_formatted,
                '공고기관': bid.get('ntceInsttNm', ''),
            })
        
        df = pd.DataFrame(df_data)
        
        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='입찰공고', index=False)
        
        output.seek(0)
        
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'나라장터_입찰공고_{timestamp}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/delete', methods=['POST'])
def delete_bids():
    """선택된 항목 삭제 API"""
    try:
        data = request.get_json()
        selected_ids = data.get('selected_ids', [])
        
        global current_bids
        # 선택된 항목들을 current_bids에서 제거
        current_bids = [bid for bid in current_bids if bid['id'] not in selected_ids]
        
        return jsonify({
            'success': True,
            'message': f'{len(selected_ids)}개 항목이 삭제되었습니다.',
            'remaining_count': len(current_bids)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)