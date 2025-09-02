// 나라장터 입찰공고 검색 시스템 JavaScript

class BidSearchApp {
    constructor() {
        this.selectedItems = new Set();
        this.allData = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadAgencies();
        this.setDefaultDates();
        this.updateCurrentTime();
        
        // 시간 업데이트 (1분마다)
        setInterval(() => this.updateCurrentTime(), 60000);
    }

    setupEventListeners() {
        // 검색 폼
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });

        // 전체 선택 체크박스
        document.getElementById('headerCheckbox').addEventListener('change', (e) => {
            this.toggleSelectAll(e.target.checked);
        });

        // 버튼 이벤트
        document.getElementById('selectAllBtn').addEventListener('click', () => {
            this.selectAll();
        });

        document.getElementById('deleteSelectedBtn').addEventListener('click', () => {
            this.deleteSelected();
        });

        document.getElementById('exportExcelBtn').addEventListener('click', () => {
            this.exportToExcel();
        });
    }

    updateCurrentTime() {
        const now = new Date();
        const timeString = now.toLocaleString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
        document.getElementById('currentTime').textContent = timeString;
    }

    setDefaultDates() {
        const today = new Date();
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        document.getElementById('startDate').value = this.formatDate(weekAgo);
        document.getElementById('endDate').value = this.formatDate(today);
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    async loadAgencies() {
        try {
            const response = await axios.get('/api/agencies');
            if (response.data.success) {
                const select = document.getElementById('agencyFilter');
                select.innerHTML = '<option value="all">전체</option>';
                
                response.data.agencies.forEach(agency => {
                    const option = document.createElement('option');
                    option.value = agency;
                    option.textContent = agency;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('기관 목록 로드 실패:', error);
        }
    }

    async performSearch() {
        const formData = {
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value,
            bid_type: document.getElementById('bidType').value,
            agency_filter: document.getElementById('agencyFilter').value
        };

        this.showLoading(true);
        this.hideResults();

        try {
            const response = await axios.post('/api/search', formData);
            
            if (response.data.success) {
                this.allData = response.data.data;
                this.displayResults(this.allData);
                this.showSuccessMessage(`${response.data.count}개의 입찰공고를 찾았습니다.`);
            } else {
                this.showErrorMessage(response.data.error || '검색에 실패했습니다.');
                this.showEmptyState();
            }
        } catch (error) {
            console.error('검색 실패:', error);
            this.showErrorMessage('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
            this.showEmptyState();
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(data) {
        if (!data || data.length === 0) {
            this.showEmptyState();
            return;
        }

        const tbody = document.getElementById('resultsTableBody');
        tbody.innerHTML = '';
        
        data.forEach((item, index) => {
            const row = this.createTableRow(item, index);
            tbody.appendChild(row);
        });

        this.updateResultCount(data.length);
        this.showResults();
        this.selectedItems.clear();
        this.updateSelectAllButton();
    }

    createTableRow(item, index) {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors duration-200';
        row.dataset.id = item.id;

        // 날짜 포맷팅
        const bidDate = this.formatDisplayDate(item.bidNtceDt);
        const closeDate = this.formatDisplayDate(item.bidClseDt);
        
        // 가격 포맷팅
        const price = this.formatPrice(item.presmptPrce);
        
        // 입찰 구분 뱃지 클래스
        const badgeClass = this.getBadgeClass(item.bidType);

        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <input type="checkbox" class="row-checkbox rounded border-gray-300 text-blue-600 focus:ring-blue-500" 
                       data-id="${item.id}">
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${badgeClass}">
                    ${item.bidType}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${bidDate}
            </td>
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 max-w-md truncate" title="${item.bidNtceNm}">
                    ${item.bidNtceNm}
                </div>
                <div class="text-sm text-gray-500">공고번호: ${item.bidNtceNo}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${item.dminsttNm}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${closeDate}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${price}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                ${item.bidNtceUrl ? 
                    `<a href="${item.bidNtceUrl}" target="_blank" 
                       class="text-blue-600 hover:text-blue-900 flex items-center">
                        <i class="fas fa-external-link-alt mr-1"></i>
                        상세보기
                    </a>` : 
                    '<span class="text-gray-400">링크없음</span>'
                }
            </td>
        `;

        // 체크박스 이벤트 리스너
        const checkbox = row.querySelector('.row-checkbox');
        checkbox.addEventListener('change', (e) => {
            this.handleRowSelection(e.target.dataset.id, e.target.checked);
            row.classList.toggle('selected', e.target.checked);
        });

        return row;
    }

    getBadgeClass(bidType) {
        const classes = {
            '용역': 'badge-servc bg-blue-100 text-blue-800',
            '건설공사': 'badge-cnstwk bg-green-100 text-green-800',
            '물품': 'badge-thng bg-yellow-100 text-yellow-800'
        };
        return classes[bidType] || 'bg-gray-100 text-gray-800';
    }

    formatDisplayDate(dateString) {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('ko-KR', {
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            }).replace(/\./g, '/');
        } catch {
            return dateString.substring(0, 16);
        }
    }

    formatPrice(priceString) {
        if (!priceString || priceString === 'N/A') return '-';
        try {
            const price = parseInt(priceString);
            if (price >= 100000000) {
                return `${(price / 100000000).toFixed(1)}억원`;
            } else if (price >= 10000000) {
                return `${Math.floor(price / 10000000)}천만원`;
            } else {
                return `${price.toLocaleString()}원`;
            }
        } catch {
            return priceString;
        }
    }

    handleRowSelection(id, selected) {
        if (selected) {
            this.selectedItems.add(id);
        } else {
            this.selectedItems.delete(id);
        }
        this.updateSelectAllButton();
    }

    toggleSelectAll(selectAll) {
        const checkboxes = document.querySelectorAll('.row-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAll;
            const row = checkbox.closest('tr');
            row.classList.toggle('selected', selectAll);
            
            if (selectAll) {
                this.selectedItems.add(checkbox.dataset.id);
            } else {
                this.selectedItems.delete(checkbox.dataset.id);
            }
        });
        this.updateSelectAllButton();
    }

    selectAll() {
        document.getElementById('headerCheckbox').checked = true;
        this.toggleSelectAll(true);
    }

    updateSelectAllButton() {
        const headerCheckbox = document.getElementById('headerCheckbox');
        const totalRows = document.querySelectorAll('.row-checkbox').length;
        const selectedCount = this.selectedItems.size;
        
        if (selectedCount === 0) {
            headerCheckbox.checked = false;
            headerCheckbox.indeterminate = false;
        } else if (selectedCount === totalRows) {
            headerCheckbox.checked = true;
            headerCheckbox.indeterminate = false;
        } else {
            headerCheckbox.checked = false;
            headerCheckbox.indeterminate = true;
        }
    }

    async deleteSelected() {
        if (this.selectedItems.size === 0) {
            this.showWarningMessage('삭제할 항목을 선택해주세요.');
            return;
        }

        if (!confirm(`선택한 ${this.selectedItems.size}개 항목을 삭제하시겠습니까?`)) {
            return;
        }

        try {
            const response = await axios.post('/api/delete', {
                selected_ids: Array.from(this.selectedItems)
            });

            if (response.data.success) {
                // 선택된 행들을 DOM에서 제거
                this.selectedItems.forEach(id => {
                    const row = document.querySelector(`tr[data-id="${id}"]`);
                    if (row) {
                        row.remove();
                    }
                });

                this.selectedItems.clear();
                this.updateSelectAllButton();
                this.updateResultCount(response.data.remaining_count);
                this.showSuccessMessage(response.data.message);
            } else {
                this.showErrorMessage(response.data.error || '삭제에 실패했습니다.');
            }
        } catch (error) {
            console.error('삭제 실패:', error);
            this.showErrorMessage('서버 오류가 발생했습니다.');
        }
    }

    async exportToExcel() {
        const selectedIds = this.selectedItems.size > 0 ? 
            Array.from(this.selectedItems) : 
            this.allData.map(item => item.id);

        if (selectedIds.length === 0) {
            this.showWarningMessage('내보낼 데이터가 없습니다.');
            return;
        }

        this.showLoading(true, '엑셀 파일을 생성하는 중...');

        try {
            const response = await axios.post('/api/export/excel', {
                selected_ids: selectedIds
            }, {
                responseType: 'blob'
            });

            // 파일 다운로드
            const blob = new Blob([response.data], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            });
            
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            
            const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_');
            link.download = `나라장터_입찰공고_${timestamp}.xlsx`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            this.showSuccessMessage(`${selectedIds.length}개 항목이 엑셀 파일로 저장되었습니다.`);
        } catch (error) {
            console.error('엑셀 내보내기 실패:', error);
            this.showErrorMessage('엑셀 파일 생성에 실패했습니다.');
        } finally {
            this.showLoading(false);
        }
    }

    updateResultCount(count) {
        document.getElementById('resultCount').textContent = `${count}건`;
    }

    showResults() {
        document.getElementById('resultsSection').classList.remove('hidden');
        document.getElementById('emptyState').classList.add('hidden');
    }

    hideResults() {
        document.getElementById('resultsSection').classList.add('hidden');
        document.getElementById('emptyState').classList.add('hidden');
    }

    showEmptyState() {
        document.getElementById('resultsSection').classList.add('hidden');
        document.getElementById('emptyState').classList.remove('hidden');
    }

    showLoading(show, message = '검색 중...') {
        const spinner = document.getElementById('loadingSpinner');
        const text = spinner.querySelector('span');
        
        if (show) {
            text.textContent = message;
            spinner.classList.remove('hidden');
        } else {
            spinner.classList.add('hidden');
        }
    }

    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }

    showWarningMessage(message) {
        this.showMessage(message, 'warning');
    }

    showMessage(message, type = 'info') {
        // 기존 메시지 제거
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-sm shadow-lg`;
        alertDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
                <span>${message}</span>
                <button class="ml-auto text-current opacity-50 hover:opacity-100" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(alertDiv);

        // 3초 후 자동 제거
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
}

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    new BidSearchApp();
});