from time import sleep
import pandas as pd
import undetected_chromedriver as uc  #tarayıcıyı bot algılamasını yakalamasın diye standart webdriver yerine bunu kullanıyoruz
from selenium.webdriver.common.by import By

#tarayıcıyı bot algılamasını yakalamasın diye
driver = uc.Chrome(use_subprocess=True)
driver.delete_all_cookies()

tum_ilanlar = []
TOPLAM_SAYFA = 20

try:
  for sayfa_idx in range(1, TOPLAM_SAYFA + 1):
    offset = (sayfa_idx - 1) * 50
    url = f"https://www.sahibinden.com/kiralik-daire/istanbul-atasehir?pagingOffset={offset}&viewType=Classic&pagingSize=50&address_region=2"

    print(f"{sayfa_idx}. sayfa yükleniyor...")
    driver.get(url)

    # ÖNEMLİ: İlk açılışta veya sayfa değişimlerinde bot koruması çıkarsa
    # terminale bilgi verelim ve manuel geçiş için  süre tanıyalım
    sleep(5)
    #Selenium CSS Selectors
    ilanlar = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")

    if not ilanlar:
      print(
          f"\n[!] {sayfa_idx}. sayfada ilanlar alınamadı."
          " Bot korumasına (Cloudflare/DataDome) takılmış olabilirsiniz."
      )
      print(
          "Lütfen açılan tarayıcı penceresinden varsa robot doğrulamasını"
          " (CAPTCHA) elinizle çözün."
      )
      input(
          "Doğrulamayı yaptıktan sonra devam etmek için ENTER tuşuna"
          " basın..."
      )
      #enter bastıktan sonra tekrar ilanları yakalamayı dene
      #bot koruması için
      ilanlar = driver.find_elements(By.CSS_SELECTOR, "tr.searchResultsItem")

    for ilan in ilanlar:
      try:
        fiyat = ilan.find_element(
            By.CSS_SELECTOR, "td.searchResultsPriceValue"
        ).text.strip()
        detaylar = ilan.find_elements(By.CSS_SELECTOR, "td.searchResultsAttributeValue")

        m_brut = detaylar[0].text.strip() if len(detaylar) > 0 else ""
        oda_sayisi = detaylar[1].text.strip() if len(detaylar) > 1 else ""
        lokasyon = ilan.find_element(
            By.CSS_SELECTOR, "td.searchResultsLocationValue"
        ).text.strip()

        tum_ilanlar.append({
            "Fiyat": fiyat,
            "m² (Brüt)": m_brut,
            "Oda Sayısı": oda_sayisi,
            "Semt / Mahalle": lokasyon,
                    })
      except Exception:
        continue

    #sayfalar arası geçişte bot olduğumuz anlaşılmasın diye
    #sisteme insanî bir ritim vermek için rastgele bekleme
    sleep(6)

finally:
  driver.quit()

df = pd.DataFrame(tum_ilanlar)
df.to_excel("atasehir_kiralik_daireler.xlsx", index=False)
print(f"Toplam {len(tum_ilanlar)} ilan kaydedildi.")