from flask import Flask, render_template, request, session, redirect, url_for,make_response
import pdfkit
import base64
#wkhtmltopdf indirilmesi gerekliaaaa
import os
import sys
import shutil
from pathlib import Path

import math


# --- Helpers for PyInstaller / resource access ---

def resource_path(relative_path: str) -> str:
    """Return absolute path to resource, works for dev and for PyInstaller bundle."""
    base_path = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base_path) / relative_path)


def find_wkhtmltopdf() -> str | None:
    """Try to locate wkhtmltopdf in env, PATH, or bundled bin directory."""
    # 1) Environment variable override
    env_path = os.environ.get("WKHTMLTOPDF_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    # 2) System PATH
    which = shutil.which("wkhtmltopdf")
    if which:
        return which
    # 3) Bundled with the app under bin/
    candidates = [
        resource_path("bin/wkhtmltopdf.exe"),  # Windows
        resource_path("bin/wkhtmltopdf"),      # Linux/macOS
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static"),
)
app.secret_key = "cok_gizli_anahtar"

# ----------------R_A---------------------------#
def N_G_cal(value):
    # Örnek olarak, gelen değere bağlı olarak 0.1 ile çarpılmış değeri döndürür.
    return value * 0.1

def A_D_cal(L, W, H, H_max):
    A_D_1 = (L * W) + (2 * (3 * H)) * (L + W) + (math.pi * (3 * H)**2)
    A_D_2 = math.pi * (3 * H_max)**2
    if (H_max == H):
        return A_D_1
    else:
        if (A_D_1 >= A_D_2):
            return A_D_1
        else:
            return A_D_2

def C_D_cal(selected_option: str) -> float:
    mapping = {
        "Daha yüksek cisimler ile çevrelenen yapı": 0.25,
        "Aynı yükseklikte veya daha alçak cisimler ile çevrelenen yapı": 0.50,
        "Ayrık yapı: yakında başka cisimlerin olmaması": 1.0,
        "Tepe veya tepecik üzerinde ayrık yapı": 2.0
    }
    return mapping.get(selected_option, 0.0)

    




def P_B_cal(selected_option: str) -> float:
    mapping = {
        "Yapı LPS ile Korunmuyor": 1.0,
        "1. Seviye LPS ile Korunuyor": 0.02,
        "2. Seviye LPS ile Korunuyor": 0.05,
        "3. Seviye LPS ile Korunuyor": 0.1,
        "4. Seviye LPS ile Korunuyor": 0.2,
        "Sürekli Metal veya Takviyeli Beton İskelete Sahip Yapı": 0.01,
        "Metal çatıyı tamamen koruyan ve sürekli metal veya takviyeli beton iskelete sahip yapı": 0.001
    }
    return mapping.get(selected_option, 0.0)

def r_t_cal(selected_option: str) -> float:  # yuzeytip
    mapping = {
        "Tarımsal, Betton": 10**(-2),
        "Mermer, Seramik": 10**(-3),
        "Çakıl, Moket, Halı": 10**(-4),
        "Asfalt, Muşamba, Halı": 10**(-5)
    }
    return mapping.get(selected_option, 0.0)

def L_T_cal():
    return 10**(-2)

def r_p_cal(selected_option: str) -> float:  # yangın_tedbir
    mapping = {
        "Tedbir Yok": 1.0,
        "Yangın Söndürücüler, İle Çalıştırılan Yangın Söndürme Sistemi, Elle Çalıştırılan Alarm Sistemleri, Hidrantlar, Yangına Karşı Korunmalı Bölmeler, Kaçış Güzergâhları": 0.5,
        "Otomatik Sabit Yangın Söndürme Sistemleri, Otomatik Alarm Sistemleri (İtfayiciler 10 dakikalık mesafede ise)": 0.2  
    }
    return mapping.get(selected_option, 0.0)

def r_f_cal(selected_option: str) -> float:  # yangın_riski
    mapping = {
        "Patlama ve Yangın Riski Yok": 0,
        "Yangın Riski Düşük": 10**(-3),
        "Yangın Riski Normal": 10**(-2),
        "Yangın Riski Yüksek": 10**(-1),
        "1. Seviye Patlama Riski-Bölge 2,22": 10**(-3),
        "2. Seviye Patlama Riski-Bölge 1,21": 10**(-1),
        "3. Seviye Patlama Riski(Katı Patlayıcı)-Bölge 0,20": 1
    }
    return mapping.get(selected_option, 0.0)  # özel_tehlike

def h_z_cal(selected_option: str) -> float:
    mapping = {
        "Özel Tehlike Yok": 1,
        "Düşük Panik Seviyesi": 2,
        "Orta Panik Seviyesi": 5,
        "Tahliye Zorluğu": 5,
        "Yüksek Panik Seviyesi": 10
    }
    return mapping.get(selected_option, 0.0)

def L_F_cal(selected_option: str) -> float:  # yapı_tipi
    mapping = {
        "Patlama Riski Olan Yapılar": 10**(-1),
        "Hastahane": 10**(-1),
        "Otel, Okul, Kamu Binası":10**(-1),
        "Halka Açık Ağlence Yeri, İbadethane, Müze": 5 * 10**(-2),
        "Sanayi, Ticari": 2 * 10**(-2),
        "Diğerleri": 10**(-2)
    }
    return mapping.get(selected_option, 0.0)

def P_SPD_cal(selected_option: str) -> float:  # SPD
    mapping = {
        "SPD Bulunmuyor": 1,
        "4-3. Seviye SPD": 0.05,
        "2. Seviye SPD": 0.02,
        "1. Seviye SPD": 0.01
    }
    return mapping.get(selected_option, 0.0)

def P_EB_cal(selected_option: str) -> float:

    mapping ={
    "SPD Bulunmuyor":1,
    "4-3. Seviye SPD":0.05,
    "2. Seviye SPD":0.02,
    "1. Seviye SPD":0.01
    }
    return mapping.get(selected_option, 0.0)

def A_M_cal(L, W):
    A_M = 2 * 500 * (L + W) + math.pi * (500)**2
    return A_M
def P_LI_GÜÇ_cal(selected_option: str) -> float:
    mapping = {
        "Yeterli Değil Veya Yok": 1,
        "1 kV": 1.0,
        "1.5 kV": 0.6,
        "2.5 kV": 0.3,
        "4 kV": 0.16,
        "6 kV": 0.1
    }
    return mapping.get(selected_option, 0.0)
def P_LI_TLC_cal(selected_option: str) -> float:
    mapping = {
        "Yeterli Değil Veya Yok": 1,
        "1 kV": 1.0,
        "1.5 kV": 0.5,
        "2.5 kV": 0.2,
        "4 kV": 0.08,
        "6 kV": 0.04
    }
    return mapping.get(selected_option, 0.0)

def KS_4_cal(selected_option: str) -> float:
    mapping = {
        "Yeterli Değil Veya Yok": 0,
        "1 kV": 1.0,
        "1.5 kV": 1/1.5,
        "2.5 kV": 1/2.5,
        "4 kV": 1/4.0,
        "6 kV": 1/6.0
    }
    return mapping.get(selected_option, 0.0)

def KS_3_cal(selected_option: str) -> float:
    mapping = {
        "Zırhlanmamış kablo – döngüleri önlemek için güzergâh tedbiri yok": 1,
        "Zırhlanmamış kablo – döngüleri önlemek için güzergâh tedbiri var (10 m^2 mertebesinde döngü alanı)": 0.2,
        "Zırhlanmamış kablo – döngüleri önlemek için güzergâh tedbiri var (0.5 m^2 mertebesinde döngü alanı)":0.01,
        "Zırhlanmış kablolar ve metal kanal içinde serili kablolar": 0.0001
    }
    return mapping.get(selected_option, 0.0)

def A_L_cal(L_hat):
    # Bilinmiyor ("-") seçildiğinde önceki varsayılan değeri kullan
    if L_hat == "-":
        return 1000*40
    A_L = 40 * L_hat
    return A_L

def C_I_cal(selected_option: str) -> float:
    mapping = {
        "Havai": 1,
        "Gömülü": 0.5
    }
    return mapping.get(selected_option, 0.0)

def C_T_cal(selected_option: str) -> float:
    mapping = {
        "AG Güç Hattı": 1,
        "YG Güç Hattı": 0.2
    }
    return mapping.get(selected_option, 0.0)

def C_E_cal(selected_option: str) -> float:
    mapping = {
        "Kırsal": 1,
        "Banliyö": 0.5,
        "Şehir": 0.1,
        "Yirmi Metreden Uzun Yapılarla Çevrili Şehir": 0.01
    }
    return mapping.get(selected_option, 0.0)

def P_TA_cal(selected_options) -> float:
    mapping = {
        "Korunma Tedbiri Yok": 1.0,
        "Uyarı İşaretleri": 0.1,
        "Elektriksel Yalıtım": 0.01,
        "Etkin Zemin Eş Potansiyel Kuşaklaması": 0.01,
        "Fiziksel Kısıtlamalar ve İndirme İletkeni Olarak Kullanılan Bina İskeleti": 0
    }
    # Eğer birden fazla seçenek gelmişse (liste), değerleri çarparız.
    if isinstance(selected_options, list):
        product = 1
        for option in selected_options:
            product *= mapping.get(option, 0.0)
        return product
    else:
        return mapping.get(selected_options, 0.0)

def P_TU_cal(selected_options) -> float:
    mapping = {
        "Korunma Tedbiri Yok": 1,
        "Kablaj Uyarılarıları": 0.1,
        "Elektriksel Yalıtım": 0.01,
        "Fiziksel Kısıtlamalar": 0
    }
    if isinstance(selected_options, list):
        product = 1
        for option in selected_options:
            product *= mapping.get(option, 0.0)
        return product
    else:
        return mapping.get(selected_options, 0.0)


def A_I_cal(L_hat):
    # Bilinmiyor ("-") seçildiğinde önceki varsayılan değeri kullan
    if L_hat == "-":
        return 4000 * 1000
    A_I = 4000 * L_hat
    return A_I

def C_LI_GÜÇ_cal(selected_option: str) -> float:
    mapping = {
        "Zırhlanmamış Güç Hattı":1,
        "Zırhlanmış Güç Hattı":0.3,
        "Çoklu Topraklanmış Nötr Güç Hattı":0.2
    }
    return mapping.get(selected_option, 0.0)
def C_LI_TLC_cal(selected_option: str) -> float:
    mapping = {
        "Zırhlanmamış Telekominikasyon Hattı":1,
        "Zırhlanmış Telekominikasyon Hattı":0.3
    }
    return mapping.get(selected_option, 0.0)




###########################################


        


# --- Display formatting helpers ---
def fmt_r(x, sig=4):
    """
    Format risk values compactly with limited decimals/significant digits for display in templates.
    Default: 4 significant figures (e.g., 0.01234 -> '0.01234', 1.234567e-5 -> '1.235e-05').
    """
    try:
        return format(float(x), f".{sig}g")
    except Exception:
        return x

# ---------------- Routes ---------------- #

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/region_parameters", methods=["GET", "POST"])
def region_parameters():
    # İlk ziyaret için session'daki değerleri alıyoruz (boş olabilir)
    lightning_density = session.get("lightning_density", "")
    yapisecim = session.get("yapisecim", "")
    özel_tehlike = session.get("özel_tehlike", "")
    yapı_max_h = session.get("yapı_max_h", "")
    yapı_h = session.get("yapı_h", "")
    genislik = session.get("genislik", "")
    uzunluk = session.get("uzunluk", "")
    yıldırımdan_korunma_seviyesi = session.get("yıldırımdan_korunma_seviyesi", "")
    SPD = session.get("SPD", "")
    çevre_faktörü = session.get("çevre_faktörü", "")
    yapı_tipi = session.get("yapı_tipi", "")
    yuzeytip = session.get("yuzeytip", "")

    
    if request.method == "POST":
        lightning_density = float(request.form["lightning_density"])
        yapisecim = request.form["yapisecim"]
        özel_tehlike = request.form["özel_tehlike"]
        yapı_max_h = float(request.form["yapı_max_h"])
        yapı_h = float(request.form["yapı_h"])
        genislik = float(request.form["genislik"])
        uzunluk = float(request.form["uzunluk"])
        yıldırımdan_korunma_seviyesi = request.form["yıldırımdan_korunma_seviyesi"]
        SPD = request.form["SPD"]
        çevre_faktörü = request.form["çevre_faktörü"]
        yapı_tipi = request.form["yapı_tipi"]
        yuzeytip = request.form["yuzeytip"]


        session["lightning_density"] = lightning_density
        session["yapisecim"] = yapisecim
        session["özel_tehlike"] = özel_tehlike
        session["yapı_max_h"] = yapı_max_h
        session["yapı_h"] = yapı_h
        session["genislik"] = genislik
        session["uzunluk"] = uzunluk
        session["yıldırımdan_korunma_seviyesi"] = yıldırımdan_korunma_seviyesi
        session["SPD"] = SPD
        session["çevre_faktörü"] = çevre_faktörü
        session["yapı_tipi"] = yapı_tipi
        session["yuzeytip"] = yuzeytip


        session["N_G"] = N_G_cal(lightning_density)
        session["A_D"] = A_D_cal(uzunluk, genislik, yapı_h, yapı_max_h)
        session["C_D"] = C_D_cal(yapisecim)
        session["P_B"] = P_B_cal(yıldırımdan_korunma_seviyesi)
        session["h_z"] = h_z_cal(özel_tehlike)
        session["L_F"] = L_F_cal(yapı_tipi)  # varsayım: L_F_cal için yapı_tipi kullanılıyor
        session["P_EB"] = P_EB_cal(SPD)
        session["r_t"] = r_t_cal(yuzeytip)
        session["A_M"] = A_M_cal(uzunluk, genislik)
        session["C_E"] = C_E_cal(çevre_faktörü)
        
        
        
        

        return redirect(url_for("power_line"))
    
    return render_template("region_parameters.html",
                           lightning_density=lightning_density,
                           yapisecim=yapisecim,
                           yapı_max_h=yapı_max_h,
                           yapı_h=yapı_h,
                           genislik=genislik,
                           uzunluk=uzunluk,
                           yıldırımdan_korunma_seviyesi=yıldırımdan_korunma_seviyesi,
                           SPD=SPD,
                           çevre_faktörü=çevre_faktörü,
                           özel_tehlike=özel_tehlike,
                           yapı_tipi=yapı_tipi,
                           yuzeytip=yuzeytip)

@app.route("/power_line", methods=["GET", "POST"])
def power_line():
    güç_hattı = session.get("güç_hattı", "")
    hat_uzunluk_güç = session.get("hat_uzunluk_güç", "")
    tesisat_faktörü_güç = session.get("tesisat_faktörü_güç", "")
    güç_hattı_tipi = session.get("güç_hattı_tipi", "")
    dayanım_gerilimi_güç = session.get("dayanım_gerilimi_güç", "")
    dış_hat_tipi_güç = session.get("dış_hat_tipi_güç", "")

    SPD_güç = session.get("SPD_güç", "")
    iç_hat_GÜÇ = session.get("iç_hat_GÜÇ", "")
    giriş_GÜÇ = session.get("giriş_GÜÇ", "")

    if request.method == "POST":
        unknown_power = False
        güç_hattı = request.form["güç_hattı"]
        if güç_hattı == "Yok":
            hat_uzunluk_güç = 0
            tesisat_faktörü_güç = "-"
            güç_hattı_tipi = "-"
            dayanım_gerilimi_güç = "-"
            dış_hat_tipi_güç = "-"
            SPD_güç = "-"
            iç_hat_GÜÇ = "-"
            giriş_GÜÇ = "-"
        else:
            if "hat_uzunluk_bilinmiyor" in request.form:
                unknown_power = True
                hat_uzunluk_güç = "-"
            else:
                hat_uzunluk_güç = float(request.form["hat_uzunluk_güç"])
            tesisat_faktörü_güç = request.form["tesisat_faktörü_güç"]
            güç_hattı_tipi = request.form["güç_hattı_tipi"]
            dayanım_gerilimi_güç = request.form["dayanım_gerilimi_güç"]
            dış_hat_tipi_güç = request.form["dış_hat_tipi_güç"]
            SPD_güç = request.form["SPD_güç"]
            iç_hat_GÜÇ = request.form["iç_hat_GÜÇ"]
            giriş_GÜÇ = request.form["giriş_GÜÇ"]

        # Form değerlerini session'a kaydetme
        session["güç_hattı"] = güç_hattı
        session["hat_uzunluk_güç"] = hat_uzunluk_güç
        session["tesisat_faktörü_güç"] = tesisat_faktörü_güç
        session["güç_hattı_tipi"] = güç_hattı_tipi
        session["dayanım_gerilimi_güç"] = dayanım_gerilimi_güç
        session["dış_hat_tipi_güç"] = dış_hat_tipi_güç
        session["SPD_güç"] = SPD_güç
        session["iç_hat_GÜÇ"] = iç_hat_GÜÇ
        session["giriş_GÜÇ"] = giriş_GÜÇ

        # Sadece "Yok" seçildiğinde sayfa 0 olmalı; "Bilinmiyor" durumunda varsayılanlar kullanılacak
        if güç_hattı == "Yok":
            session["A_L_GÜÇ"] = 0.0
            session["C_I_GÜÇ"] = 0.0
            session["C_T_GÜÇ"] = 0.0
            session["P_SPD_GÜÇ"] = 0.0
            session["A_I_GÜÇ"] = 0.0
            session["P_LI_GÜÇ"] = 0.0
            session["C_LI_GÜÇ"] = 0.0
            session["KS_3_GÜÇ"] = 0.0
            session["KS_4_GÜÇ"] = 0.0
        else:
            session["A_L_GÜÇ"] = A_L_cal(hat_uzunluk_güç)
            session["C_I_GÜÇ"] = C_I_cal(tesisat_faktörü_güç)
            session["C_T_GÜÇ"] = C_T_cal(güç_hattı_tipi)
            session["P_SPD_GÜÇ"] = P_SPD_cal(SPD_güç)
            session["A_I_GÜÇ"] = A_I_cal(hat_uzunluk_güç)
            session["P_LI_GÜÇ"] = P_LI_GÜÇ_cal(dayanım_gerilimi_güç)
            session["C_LI_GÜÇ"] = C_LI_GÜÇ_cal(dış_hat_tipi_güç)
            session["KS_3_GÜÇ"] = KS_3_cal(iç_hat_GÜÇ)
            session["KS_4_GÜÇ"] = KS_4_cal(dayanım_gerilimi_güç)
        return redirect(url_for("TLC"))

    return render_template("power_line.html",
                           güç_hattı=güç_hattı,
                           hat_uzunluk_güç=hat_uzunluk_güç,
                           tesisat_faktörü_güç=tesisat_faktörü_güç,
                           güç_hattı_tipi=güç_hattı_tipi,
                           dayanım_gerilimi_güç=dayanım_gerilimi_güç,
                           dış_hat_tipi_güç=dış_hat_tipi_güç,
                           SPD_güç=SPD_güç,
                           iç_hat_GÜÇ= iç_hat_GÜÇ,
                           giriş_GÜÇ= giriş_GÜÇ)

@app.route("/TLC", methods=["GET", "POST"])
def TLC():
    hat_uzunluk_TLC = session.get("hat_uzunluk_TLC", "")
    tesisat_faktörü_TLC = session.get("tesisat_faktörü_TLC", "")
    dayanım_gerilimi_TLC = session.get("dayanım_gerilimi_TLC", "")
    dış_hat_tipi_TLC = session.get("dış_hat_tipi_TLC", "")
    TLC_hattı = session.get("TLC_hattı", "")
    SPD_TLC = session.get("SPD_TLC", "")
    iç_hat_TLC = session.get("iç_hat_TLC", "")
    giriş_TLC = session.get("giriş_TLC", "")

    if request.method == "POST":
        TLC_hattı = request.form["TLC_hattı"]
        if TLC_hattı == "Yok":
            hat_uzunluk_TLC = 0
            tesisat_faktörü_TLC = "-"
            dayanım_gerilimi_TLC = "-"
            dış_hat_tipi_TLC = "-"
            SPD_TLC = "-"
            iç_hat_TLC = "-"
            giriş_TLC = "-"
        else:
            if "hat_uzunluk_TLC_bilinmiyor" in request.form:
                hat_uzunluk_TLC = "-"
            else:
                hat_uzunluk_TLC = float(request.form["hat_uzunluk_TLC"])
            tesisat_faktörü_TLC = request.form["tesisat_faktörü_TLC"]
            dayanım_gerilimi_TLC = request.form["dayanım_gerilimi_TLC"]
            dış_hat_tipi_TLC = request.form["dış_hat_tipi_TLC"]
            SPD_TLC = request.form["SPD_TLC"]
            iç_hat_TLC = request.form["iç_hat_TLC"]
            giriş_TLC = request.form["giriş_TLC"]

        # Form değerlerini session'a kaydetme
        session["TLC_hattı"] = TLC_hattı
        session["hat_uzunluk_TLC"] = hat_uzunluk_TLC
        session["tesisat_faktörü_TLC"] = tesisat_faktörü_TLC
        session["dayanım_gerilimi_TLC"] = dayanım_gerilimi_TLC
        session["dış_hat_tipi_TLC"] = dış_hat_tipi_TLC
        session["SPD_TLC"] = SPD_TLC
        session["iç_hat_TLC"] = iç_hat_TLC
        session["giriş_TLC"] = giriş_TLC

        # Sadece "Yok" seçildiğinde sayfa 0 olmalı; "Bilinmiyor" durumunda varsayılanlar kullanılacak
        if TLC_hattı == "Yok":
            session["A_L_TLC"] = 0.0
            session["C_I_TLC"] = 0.0
            session["C_T_TLC"] = 0.0
            session["P_SPD_TLC"] = 0.0
            session["A_I_TLC"] = 0.0
            session["P_LI_TLC"] = 0.0
            session["C_LI_TLC"] = 0.0
            session["KS_3_TLC"] = 0.0
            session["KS_4_TLC"] = 0.0
        else:
            session["A_L_TLC"] = A_L_cal(hat_uzunluk_TLC)
            session["C_I_TLC"] = C_I_cal(tesisat_faktörü_TLC)
            session["C_T_TLC"] = 1
            session["P_SPD_TLC"] = P_SPD_cal(SPD_TLC)
            session["A_I_TLC"] = A_I_cal(hat_uzunluk_TLC)
            session["P_LI_TLC"] = P_LI_TLC_cal(dayanım_gerilimi_TLC)
            session["C_LI_TLC"] = C_LI_TLC_cal(dış_hat_tipi_TLC)
            session["KS_3_TLC"] = KS_3_cal(iç_hat_TLC)
            session["KS_4_TLC"] = KS_4_cal(dayanım_gerilimi_TLC)

        return redirect(url_for("bölge_konum"))

    return render_template("TLC.html",
                           hat_uzunluk_TLC=hat_uzunluk_TLC,
                           tesisat_faktörü_TLC=tesisat_faktörü_TLC,
                           dayanım_gerilimi_TLC=dayanım_gerilimi_TLC,
                           dış_hat_tipi_TLC=dış_hat_tipi_TLC,
                           TLC_hattı=TLC_hattı,
                           SPD_TLC=SPD_TLC,
                           iç_hat_TLC= iç_hat_TLC,
                           giriş_TLC= giriş_TLC)


@app.route("/bölge_konum", methods=["GET", "POST"])
def bölge_konum():
    
    yangın_riski = session.get("yangın_riski", "")
    yangın_tedbir = session.get("yangın_tedbir", "")
    # Yeni: "elektirik_önlem_hat" alanı artık çoklu seçim olacağı için getlist kullanıyoruz
    elektirik_önlem_hat = session.get("elektirik_önlem_hat", "")
    elektirik_önlem_yapı = session.get("elektirik_önlem_yapı", "")

    
    if request.method == "POST":

        yangın_riski = request.form["yangın_riski"]
        yangın_tedbir = request.form["yangın_tedbir"]
        # Yeni: Çoklu seçim için getlist kullanıldı
        elektirik_önlem_hat = request.form.getlist("elektirik_önlem_hat")
        elektirik_önlem_yapı = request.form.getlist("elektirik_önlem_yapı")
          # ### YENİ

        


        
        session["elektirik_önlem_yapı"] = elektirik_önlem_yapı
        session["yangın_riski"] = yangın_riski
        session["yangın_tedbir"] = yangın_tedbir
        session["elektirik_önlem_hat"] = elektirik_önlem_hat  # ### YENİ: Liste olarak kaydedildi



        session["P_TA"] = P_TA_cal(elektirik_önlem_yapı)  # ### YENİ: P_TA hesaplanıyor
        session["r_p"] = r_p_cal(yangın_tedbir)
        session["r_f"] = r_f_cal(yangın_riski)
        # Yeni: P_TU_cal artık çoklu seçenekleri destek ediyor
        session["P_TU"] = P_TU_cal(elektirik_önlem_hat)  # ### YENİ
       
        
        return redirect(url_for("rapor"))
    
    return render_template("bölge_konum.html",
                           elektirik_önlem_yapı=elektirik_önlem_yapı,
                           yangın_riski=yangın_riski,
                           yangın_tedbir=yangın_tedbir,
                           elektirik_önlem_hat=elektirik_önlem_hat)


@app.route("/rapor", methods=["GET", "POST"])
def rapor():
    # Önceden kaydedilmiş session verileri varsa onları alıyoruz
    uzman_isim = session.get("uzman_isim", "")
    musteri = session.get("musteri", "")
    proje_no = session.get("proje_no", "")
    obje = session.get("obje", "")
    tarih = session.get("tarih", "")
    uzman_aciklama = session.get("uzman_aciklama", "")

    if request.method == "POST":
        # Form gönderildiğinde verileri session'a kaydediyoruz
        uzman_isim = request.form["uzman_isim"]
        musteri = request.form["musteri"]
        proje_no = request.form["proje_no"]
        obje = request.form["obje"]
        tarih = request.form["tarih"]
        uzman_aciklama = request.form["uzman_aciklama"]

        session["uzman_isim"] = uzman_isim
        session["musteri"] = musteri
        session["proje_no"] = proje_no
        session["obje"] = obje
        session["tarih"] = tarih
        session["uzman_aciklama"] = uzman_aciklama

        return redirect(url_for("computed_values"))  # Bilgiler kaydedildikten sonra hesaplama sayfasına yönlendiriyoruz

    return render_template("rapor.html", 
                           uzman_isim=uzman_isim, 
                           musteri=musteri, 
                           proje_no=proje_no, 
                           obje=obje, 
                           tarih=tarih, 
                           uzman_aciklama=uzman_aciklama)



# --- Yeni Route: Computed Values ---
@app.route("/computed_values")
def computed_values():
    # Gerekli session parametrelerinin varlığını kontrol edelim:
    required_params = [
        "N_G", "A_D", "C_D", "P_TA", "P_B", "r_t","r_t","A_L_TLC","C_I_TLC","C_T_TLC","P_SPD_TLC","A_I_GÜÇ","C_I_GÜÇ","P_LI_GÜÇ","P_LI_TLC","giriş_GÜÇ","giriş_TLC","iç_hat_GÜÇ","iç_hat_TLC","dayanım_gerilimi_TLC","dayanım_gerilimi_güç","uzman_isim",
        "r_p", "h_z", "L_F", "P_EB", "yapı_tipi","A_M","KS_4_GÜÇ","KS_3_GÜÇ","KS_4_TLC","KS_3_TLC","A_L_GÜÇ","C_I_GÜÇ","C_E","C_T_GÜÇ","P_TU","P_SPD_GÜÇ","C_LI_GÜÇ","C_LI_TLC","A_I_TLC","tesisat_faktörü_güç","tesisat_faktörü_TLC"
    ]
    missing = [param for param in required_params if session.get(param) is None]
    if missing:
        return f"Gerekli parametre(ler) eksik: {', '.join(missing)}", 400

    # Session değerlerini alıyoruz (varsayılan olarak sayısal değerler saklanmış olmalı):
    N_G       = session.get("N_G")         # Örneğin, float
    A_D       = session.get("A_D")
    C_D       = session.get("C_D")
    P_TA      = session.get("P_TA")
    P_B       = session.get("P_B")
    r_t       = session.get("r_t")
    r_p       = session.get("r_p")
    h_z       = session.get("h_z")
    L_F       = session.get("L_F")
    P_EB     = session.get("P_EB")
    uzman_isim = session.get("uzman_isim")



    yapi_tipi = session.get("yapı_tipi")
    A_M       = session.get("A_M")
    KS_4_GÜÇ      = session.get("KS_4_GÜÇ")
    KS_3_GÜÇ      = session.get("KS_3_GÜÇ")
    KS_4_TLC      = session.get("KS_4_TLC")
    KS_3_TLC      = session.get("KS_3_TLC")
    A_L_GÜÇ   = session.get("A_L_GÜÇ")
    C_I_GÜÇ = session.get("C_I_GÜÇ")
    C_E = session.get("C_E")
    C_T_GÜÇ = session.get("C_T_GÜÇ")
    P_TU = session.get("P_TU")
    P_SPD_GÜÇ = session.get("P_SPD_GÜÇ")
 

    r_t = session.get("r_t")
    A_L_TLC = session.get("A_L_TLC")
    C_I_TLC = session.get("C_I_TLC")
    C_T_TLC = session.get("C_T_TLC")
    P_SPD_TLC = session.get("P_SPD_TLC")

    A_I_GÜÇ = session.get("A_I_GÜÇ")
    C_I_GÜÇ = session.get("C_I_GÜÇ")
    P_LI_GÜÇ = session.get("P_LI_GÜÇ")
    giriş_GÜÇ = session.get("giriş_GÜÇ")
    P_LI_TLC = session.get("P_LI_TLC")
    giriş_TLC = session.get("giriş_TLC")
    A_I_TLC = session.get("A_I_TLC")
    iç_hat_GÜÇ = session.get("iç_hat_GÜÇ")
    dayanım_gerilimi_güç = session.get("dayanım_gerilimi_güç")
    iç_hat_TLC =session.get("iç_hat_TLC")
    dayanım_gerilimi_TLC = session.get("dayanım_gerilimi_TLC")
    tesisat_faktörü_güç = session.get("tesisat_faktörü_güç")
    tesisat_faktörü_TLC = session.get("tesisat_faktörü_TLC")

    if (giriş_GÜÇ == "Zırh, donanımda olduğu gibi aynı kuşaklama barasına bağlanmış"):
        C_LI_GÜÇ = 0
    else:
        if(tesisat_faktörü_güç  == "Havai" and giriş_GÜÇ == "Zırh, donanımda olduğu gibi aynı kuşaklama barasına bağlanmamış"):
            C_LI_GÜÇ = 0.1
        else:
            C_LI_GÜÇ = session.get("C_LI_GÜÇ")


    if (giriş_TLC == "Zırh, donanımda olduğu gibi aynı kuşaklama barasına bağlanmış"):
        C_LI_TLC = 0
    else:
        if(tesisat_faktörü_TLC == "Havai" and giriş_TLC == "Zırh, donanımda olduğu gibi aynı kuşaklama barasına bağlanmamış"):
            C_LI_TLC = 0.1
        else:
            C_LI_TLC = session.get("C_LI_TLC")


   




    
    # r_f: Eğer yapı tipi "Patlama Riski Olan Yapılar" ise 1, aksi halde session'dan gelen değeri kullanıyoruz.
    if yapi_tipi == "Patlama Riski Olan Yapılar":
        r_f = 1
    else:
        r_f = session.get("r_f")
        if r_f is None:
            return "r_f değeri eksik", 400

    # --- R_A Hesaplaması ---
   
    N_D = N_G * A_D * C_D * 1e-6
    P_A = P_TA * P_B
    L_T = 1e-2
    L_A = r_t * L_T
    R_A = N_D * P_A * L_A
    

    # --- R_B Hesaplaması ---
    L_B = r_p * r_f * h_z * L_F
    R_B = N_D * P_B * L_B
    

    # --- R_C Hesaplaması ---
    C_LD_GÜÇ = 1
    C_LD_TLC = 1
    P_C_GÜÇ = P_SPD_GÜÇ * C_LD_GÜÇ
    P_C_TLC  = P_SPD_TLC * C_LD_TLC
    P_C = 1 - (1 - P_C_GÜÇ) * (1 - P_C_TLC)
    if yapi_tipi == "Hastahane":
        L_O = 1e-3
    elif yapi_tipi == "Patlama Riski Olan Yapılar":
        L_O = 1e-1
    else:
        L_O = 0
    L_C = L_O
    R_C = N_D * P_C * L_C





    # --- R_M HESAPLANMASI ---
    N_M = N_G*A_M*1e-6

    if (iç_hat_GÜÇ == "Zırhlanmış kablolar ve metal kanal içinde serili kablolar"):
        KS_1_GÜÇ = 1e-4
        KS_2_GÜÇ = 1e-4
    else:
        KS_1_GÜÇ = 1
        KS_2_GÜÇ = 1

    if (dayanım_gerilimi_güç == "Yeterli Değil Veya Yok"):
        KS_1_GÜÇ = 1
        KS_2_GÜÇ = 1
        KS_3_GÜÇ = 1
        KS_4_GÜÇ = 1
    P_MS_P = (KS_1_GÜÇ*KS_2_GÜÇ*KS_3_GÜÇ*KS_4_GÜÇ)**2
    P_M_P = P_SPD_GÜÇ*P_MS_P

    if (iç_hat_TLC == "Zırhlanmış kablolar ve metal kanal içinde serili kablolar"):
        KS_1_TLC = 1e-4
        KS_2_TLC = 1e-4
    else:
        KS_1_TLC = 1
        KS_2_TLC = 1


    if (dayanım_gerilimi_TLC == "Yeterli Değil Veya Yok"):
        KS_1_TLC = 1
        KS_2_TLC = 1
        KS_3_TLC = 1
        KS_4_TLC = 1
 













    P_MS_T = (KS_1_TLC*KS_2_TLC*KS_3_TLC*KS_4_TLC)**2
    P_M_T = P_SPD_TLC*P_MS_T

    P_M = 1 - (1 - P_M_P) * (1 - P_M_T)
    L_M= L_C
    R_M = N_M*P_M*L_M




    #----R_U_P HESAPLANAMSI: ---S

    N_L_P = N_G*A_L_GÜÇ*C_I_GÜÇ*C_E*C_T_GÜÇ*1e-6

    P_LD =1

    P_U_P = P_TU*P_EB*P_LD*C_LD_GÜÇ
    L_U = r_t*L_T*1*1
    R_U_P = N_L_P*P_U_P*L_U

     #----R_U_T HESAPLANAMSI: ---

    N_L_T = N_G*A_L_TLC*C_I_TLC*C_T_TLC*C_E*1e-6
    P_U_T = P_TU*P_EB*P_LD*C_LD_TLC
    L_U_T = r_t*L_T*1*1

    R_U_T = N_L_T*P_U_T*L_U_T

    #----R_U HESAPLANAMSI: ---
    R_U = R_U_T+R_U_P

#----R_V_P HESAPLANAMSI: ---

    P_V_P = P_EB*P_LD*C_LD_GÜÇ
    L_V_P = r_p*r_f*h_z*L_F
    R_V_P = N_L_P*P_V_P*L_V_P

#----R_V_T HESAPLANAMSI: ---

    P_V_T = P_EB*P_LD*C_LD_TLC
    L_V_T = r_p*r_f*h_z*L_F
    R_V_T = N_L_T*P_V_T*L_V_T

    #----R_V HESAPLANAMSI: ---
    R_V = R_V_T +R_V_P

#----R_W_P HESAPLANAMSI: ---

    P_W_P = P_SPD_GÜÇ*P_LD*C_LD_GÜÇ
    L_W_P = L_O*1*1
    R_W_P = N_L_P*P_W_P*L_W_P

#----R_W_T HESAPLANAMSI: ---

    P_W_T = P_SPD_TLC*P_LD*C_LD_TLC
    L_W_T = L_O*1*1
    R_W_T = N_L_T*P_W_T*L_W_T

#----R_W_T HESAPLANAMSI: ---

    R_W = R_W_T + R_W_P

#----R_Z_P HESAPLANAMSI: ---

    N_I_P = N_G*A_I_GÜÇ*C_I_GÜÇ*C_E*C_T_GÜÇ*1e-6
    P_Z_P = P_SPD_GÜÇ*P_LI_GÜÇ*C_LI_GÜÇ
    L_Z_P =L_O*1*1
    R_Z_P = N_I_P*P_Z_P*L_Z_P

#----R_Z_T HESAPLANAMSI: ---

    N_I_T = N_G*A_I_TLC*C_I_TLC*C_E*C_T_TLC*1e-6
    P_Z_T = P_SPD_TLC*P_LI_TLC*C_LI_TLC
    L_Z_T = L_O*1*1
    R_Z_T = P_Z_T*N_I_T*L_Z_T



    R_Z = R_Z_P+R_Z_T

    # --- TOPLAM RİSK ---
    R_TOPLAM = R_A + R_B + R_C + R_M + R_U + R_V + R_W + R_Z
    session["R_TOPLAM"] = R_TOPLAM



    session["R_A"] = R_A
    session["R_B"] = R_B
    session["R_C"] = R_C
    session["R_M"] = R_M
    session["R_U"] = R_U
    session["R_V"] = R_V
    session["R_W"] = R_W
    session["R_Z"] = R_Z

    

    # Hesaplama sonuçlarını template'e gönderiyoruz:
    return render_template(
        "computed_values.html",
        # Hesapladığınız risk bileşenleri (formatlanmış olarak)
        R_A=fmt_r(R_A),
        R_B=fmt_r(R_B),
        R_C=fmt_r(R_C),
        R_M=fmt_r(R_M),
        R_U_P=fmt_r(R_U_P),
        R_U_T=fmt_r(R_U_T),
        R_U=fmt_r(R_U),
        R_V_P=fmt_r(R_V_P),
        R_V_T=fmt_r(R_V_T),
        R_V=fmt_r(R_V),
        R_W_P=fmt_r(R_W_P),
        R_W_T=fmt_r(R_W_T),
        R_W=fmt_r(R_W),
        R_Z_P=fmt_r(R_Z_P),
        R_Z_T=fmt_r(R_Z_T),
        R_Z=fmt_r(R_Z),
        R_TOPLAM=fmt_r(R_TOPLAM),
        R_toplam=fmt_r(R_TOPLAM),
        # Eklenen diğer değişkenler
        N_G=N_G,
        A_D=A_D,
        C_D=C_D,
        P_TA=P_TA,
        P_B=P_B,
        r_t=r_t,
        r_p=r_p,
        h_z=h_z,
        L_F=L_F,
        P_SPD_GÜÇ=P_SPD_GÜÇ,
        P_SPD_TLC=P_SPD_TLC,
        C_LD_GÜÇ=C_LD_GÜÇ,
        C_LD_TLC_cal=C_LD_TLC,
        yapi_tipi=yapi_tipi,
        A_M=A_M,
        KS_4_GÜÇ=KS_4_GÜÇ,
        KS_3_GÜÇ=KS_3_GÜÇ,        
        KS_4_TLC=KS_4_TLC,
        KS_3_TLC=KS_3_TLC,
        A_L_GÜÇ=A_L_GÜÇ,
        C_I_GÜÇ=C_I_GÜÇ,
        C_E=C_E,
        C_T_GÜÇ=C_T_GÜÇ,
        P_TU=P_TU,
        P_EB=P_EB,
        A_L_TLC=A_L_TLC,
        C_I_TLC=C_I_TLC,
        C_T_TLC=C_T_TLC,
        A_I_GÜÇ=A_I_GÜÇ,
        P_LI_GÜÇ=P_LI_GÜÇ,
        P_LI_TLC=P_LI_TLC,
        C_LI_GÜÇ=C_LI_GÜÇ,
        C_LI_TLC=C_LI_TLC,
        A_I_TLC=A_I_TLC,
        N_D=N_D,
        N_M=N_M,
        N_L_P=N_L_P,
        N_L_T=N_L_T,
        N_I_P=N_I_P,
        N_I_T=N_I_T,
        L_A=L_A,
        r_f=r_f,
        L_B=L_B,
        L_US=L_U,
        P_C=P_C,
        L_O=L_O,
        P_M=P_M,
        P_M_P=P_M_P,
        P_M_T=P_M_T,
        KS_1_GÜÇ=KS_1_GÜÇ,
        KS_2_GÜÇ=KS_2_GÜÇ,
        P_MS_P=P_MS_P,
        P_MS_T=P_MS_T,
        uzman_isim=uzman_isim
    )




@app.route("/download_pdf")



def download_pdf():
    N_G = session.get("N_G", "")
    uzman_isim = session.get("uzman_isim", "")
    musteri = session.get("musteri", "")
    proje_no = session.get("proje_no", "")
    obje = session.get("obje", "")
    tarih = session.get("tarih", "")
    uzman_aciklama = session.get("uzman_aciklama", "")
    R_A = session.get("R_A", "") / 1e-5
    R_B = session.get("R_B", "") / 1e-5
    R_C = session.get("R_C", "") / 1e-5
    R_M = session.get("R_M", "") / 1e-5

    
    R_U = session.get("R_U", "") / 1e-5
    R_V = session.get("R_V", "") / 1e-5
    R_W = session.get("R_W", "") / 1e-5
    R_Z = session.get("R_Z", "") / 1e-5
    R_TOPLAM = R_A + R_B + R_C + R_M + R_U + R_V + R_W + R_Z
    R_TOPLAM = round(R_TOPLAM, 2)
    
    if R_TOPLAM >= 1:
        sonuç = "R1 > RT olduğu görülmektedir. Sonuç olarak KORUMA GEREKLİDİR."
    else:
        sonuç = "R1 < RT olduğu görülmektedir. Sonuç olarak KORUMA GEREKLİ DEĞİLDİR."

    # Logo dosyasını base64 formatına çeviriyoruz (PyInstaller uyumlu).
    logo_path = resource_path("static/logo.png")
    with open(logo_path, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    rendered = render_template(
        "pdf_template.html",
        N_G=N_G,
        uzman_isim=uzman_isim,
        musteri=musteri,
        proje_no=proje_no,
        obje=obje,
        tarih=tarih,
        uzman_aciklama=uzman_aciklama,
        R_A=R_A,
        R_B=R_B,
        R_C=R_C,
        R_M=R_M,
        R_U=R_U,
        R_V=R_V,
        R_W=R_W,
        R_Z=R_Z,
        R_TOPLAM=R_TOPLAM,
        sonuç=sonuç,
        logo_base64=logo_base64  # Template'e base64 string gönderiliyor.
    )
    
    # wkhtmltopdf yolunu otomatik bul (env/PATH/bundled) ve pdfkit'i konfigüre et
    wkhtml_path = find_wkhtmltopdf()
    try:
        if wkhtml_path:
            config = pdfkit.configuration(wkhtmltopdf=wkhtml_path)
            pdf = pdfkit.from_string(rendered, False, configuration=config)
        else:
            # Son çare: sistemde default konfigürasyonla dene (bazı ortamlar için yeterli olabilir)
            pdf = pdfkit.from_string(rendered, False)
    except Exception as e:
        # Kullanıcı dostu hata
        return f"PDF üretimi sırasında hata oluştu: {e}. Lütfen wkhtmltopdf kurulu olduğundan emin olun veya uygulama klasöründeki bin/ altına ekleyin.", 500

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={musteri}-{obje} Risk Analiz Raporu.pdf"
    return response





if __name__ == "__main__":
    # EXE'de iki kez çalışmayı önlemek için reloader kapalı
    app.run(debug=False, use_reloader=False)





