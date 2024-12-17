from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def get_video_id(url):
    """
    YouTube video URL'sinden video ID'sini çıkarır.
    """
    from urllib.parse import urlparse, parse_qs

    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        query = parse_qs(parsed_url.query)
        return query.get('v', [None])[0]
    elif parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    else:
        return None

def scroll_to_load_comments(driver, scroll_pause_time=2, max_scrolls=10):
    """
    Sayfayı aşağı kaydırarak yorumların yüklenmesini sağlar.
    """
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    scrolls = 0
    while scrolls < max_scrolls:
        # Sayfayı en alta kaydır
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        # Yorumların yüklenmesi için bekle
        time.sleep(scroll_pause_time)
        # Yeni yüklenen sayfa yüksekliğini al
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            # Daha fazla yükleme yok
            break
        last_height = new_height
        scrolls += 1

def extract_comments(driver, max_comments=100):
    """
    Yüklenen yorumlardan metinleri çıkarır.
    """
    comments = []
    # Yorum öğelerini seçin
    comment_elements = driver.find_elements(By.XPATH, '//*[@id="content-text"]')
    for elem in comment_elements:
        if len(comments) >= max_comments:
            break
        comment = elem.text
        if comment:
            comments.append(comment)
    return comments

def main():
    # Kullanıcıdan YouTube video URL'sini al
    video_url = input("YouTube video URL'sini girin: ").strip()
    video_id = get_video_id(video_url)
    if not video_id:
        print("Geçersiz YouTube URL'si.")
        return

    # Tam video URL'sini oluştur
    full_url = f"https://www.youtube.com/watch?v={video_id}"

    # Selenium WebDriver seçeneklerini ayarla
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Tarayıcıyı görünmez modda çalıştırır
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    # WebDriver'ı başlat
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Video sayfasını aç
        driver.get(full_url)
        time.sleep(5)  # Sayfanın tam olarak yüklenmesi için bekle

        # Yorumlar bölümüne gitmek için sayfayı aşağı kaydır
        driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(2)

        # Yorumların yüklenmesi için sayfayı aşağı kaydır
        scroll_to_load_comments(driver, scroll_pause_time=2, max_scrolls=20)

        # Yorumları çıkar
        comments = extract_comments(driver, max_comments=200)

        if comments:
            print(f"\nToplam {len(comments)} yorum bulundu:\n")
            for idx, comment in enumerate(comments, 1):
                print(f"{idx}. {comment}\n")
        else:
            print("Yorum bulunamadı veya hata oluştu.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
