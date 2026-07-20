import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pyshorteners

url_short=pyshorteners.Shortener()

today = datetime.now().strftime("%y.%m.%d")

print(f"⚡{today} 리포트 수집 시작...\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

reports_data = []

for page in range(1, 3):
    url = f"https://finance.naver.com/research/company_list.naver?&page={page}"
    response = requests.get(url, headers=headers)
    response.encoding = 'euc-kr'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', class_='type_1')
    if not table:
        continue
        
    rows = table.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue
            
        title_tag = cols[1].find('a')
        if not title_tag or 'company_read' not in title_tag.get('href', ''):
            continue
            
        stock_name = cols[0].text.strip()
        title = title_tag.text.strip()
        broker = cols[2].text.strip()
        date = cols[4].text.strip()  # 작성일 텍스트
        

        is_today = (today in date)        
        if is_today:
            href = title_tag['href']
            detail_link = "https://finance.naver.com" + href if href.startswith('/research/') else "https://finance.naver.com/research/" + href
            try:
                short_link = url_short.tinyurl.short(detail_link)
            except:
                short_link = detail_link
            reports_data.append({
                '종목명': stock_name,
                '리포트제목': title,
                '증권사': broker,
                '작성일': date,
                'URL': short_link,
            })

df = pd.DataFrame(reports_data)

print("="*40)
if not df.empty:
    print(f"✅ [성공] 총 {len(df)}건의 리포트를 확인하세요!\n")
    print(df[['종목명', '증권사', 'URL']])
else:
    print("⚠️ 날짜 형식을 맞춰도 오늘 자 리포트가 안 나온다면,")
    print("   오늘 장이 안 열렸거나(주말/공휴일) 아직 게시판에 오늘 자 새 리포트가 등록되지 않은 시각입니다.")
print("="*40)