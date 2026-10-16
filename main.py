import openpyxl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
from openpyxl import load_workbook
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager  # Yeni eklendi
from selenium.webdriver.chrome.service import Service  # Yeni eklendi


# Chrome ayarları
chromOptions = Options()
chromOptions.add_argument("--headless")
chromOptions.add_argument("--no-sandbox")
chromOptions.add_argument("start-maximized")


# Driver oluşturma
service = Service(r"\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chromOptions)
driver.delete_all_cookies()

# URL'yi aç
driver.get("https://www.sahibinden.com/kiralik-daire/istanbul-atasehir?viewType=Classic&pagingSize=50&address_region=2")
driver.implicitly_wait(10)

tum_ilanlar = []
sayfa = 20

try:
  for sayfa in range(1, sayfa + 1):
    # Sahibinden'de sayfalama yapısı genellikle ?pagingOffset=50 şeklindedir
    # 1. sayfa için offset 0, 2. sayfa için 50, 3. sayfa için 100...
    offset = (sayfa - 1) * 50
    url = f"https://www.sahibinden.com/kiralik-daire/istanbul-atasehir?pagingOffset={offset}&viewType=Classic&pagingSize=50&address_region=2"

    print(f"{sayfa}. sayfa yükleniyor...")
    driver.get(url)

    # Sayfanın yüklenmesi için güvenli bir bekleme süresi
    sleep(4)

    # İlan listesindeki satırları seçme (Sahibinden sınıf isimleri güncellenebilir,
    # tarayıcıda F12 ile inceleyerek class adını teyit edin)
    ilanlar = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")

    if not ilanlar:
      print(
          f"{sayfa}. sayfada ilan bulunamadı veya bot korumasına takılmış"
          " olabilirsiniz."
      )
      break

    for ilan in ilanlar:
      try:
        # Örnek seçiciler (Sitenin güncel HTML yapısına göre class'lar değişebilir)
        # Fiyat
        fiyat = ilan.find_element(
            By.CSS_SELECTOR, "td.searchResultsPriceValue"
        ).text.strip()

        # m² (Brüt), Oda Sayısı, Bina Yaşı vb. özellikler genellikle hücreler (td) içindedir
        # Sütun sırasına göre verileri çekebilirsiniz:
        detaylar = ilan.find_elements(By.CSS_SELECTOR, "td.searchResultsAttribute")

        m_brut = detaylar[0].text.strip() if len(detaylar) > 0 else ""
        oda_sayisi = detaylar[1].text.strip() if len(detaylar) > 1 else ""
        bina_yasi = detaylar[2].text.strip() if len(detaylar) > 2 else ""
        bulundugu_kat = detaylar[3].text.strip() if len(detaylar) > 3 else ""

        # Semt / Mahalle ve İlan Tarihi
        lokasyon = ilan.find_element(
            By.CSS_SELECTOR, "td.searchResultsLocationValue"
        ).text.strip()
        tarih = ilan.find_element(
            By.CSS_SELECTOR, "td.searchResultsDateValue"
        ).text.strip()

        tum_ilanlar.append({
            "Fiyat": fiyat,
            "m² (Brüt)": m_brut,
            "Oda Sayısı": oda_sayisi,
            "Bina Yaşı": bina_yasi,
            "Bulunduğu Kat": bulundugu_kat,
            "Semt / Mahalle": lokasyon,
            "İlan Tarihi": tarih,
        })
      except Exception as e:
        # Tek bir ilandaki veri çekme hatası tüm döngüyü patlatmasın
        continue

    # Her sayfa arasında IP ban riskine karşı 3-6 saniye mola verin
    sleep(5)

finally:
  driver.quit()

# Verileri Pandas ile Excel'e aktarma
df = pd.DataFrame(tum_ilanlar)
df.to_excel("atasehir_kiralik_daireler.xlsx", index=False)
print(
    f"İşlem tamam! Toplam {len(tum_ilanlar)} adet ilan Excel dosyasına"
    " kaydedildi."
)