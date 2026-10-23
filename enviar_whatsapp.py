from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

ARQUIVO_LISTA = "numeros.txt"
TEMPO_MAX = 60  

# --------- VELOCIDADE DE DIGITAÇÃO (AJUSTE AQUI) ----------
ATRASO_MIN_CHAR = 0.04   # 0.02 = rápido
ATRASO_MAX_CHAR = 0.12   # 0.06 = mais humano/lento
ATRASO_ENTRE_LINHAS = 0.50  # pausa pequena após cada linha
# ----------------------------------------------------------

MENSAGEM = """ESCREVA A MENSAGEM AQUI!"""

def digitar_lento_no_whatsapp(caixa_msg, texto: str):
    """
    Digita o texto em uma única mensagem:
    - Quebra de linha: SHIFT+ENTER (não envia)
    - Envio final: ENTER (apenas uma vez)
    """
    linhas = texto.split("\n")

    for i, linha in enumerate(linhas):
        # Digita caractere a caractere (mais estável do que enviar texto inteiro)
        for ch in linha:
            caixa_msg.send_keys(ch)
            time.sleep(random.uniform(ATRASO_MIN_CHAR, ATRASO_MAX_CHAR))

        # Se não for a última linha, quebra linha SEM enviar
        if i < len(linhas) - 1:
            caixa_msg.send_keys(Keys.SHIFT, Keys.ENTER)
            time.sleep(ATRASO_ENTRE_LINHAS)

    # Envia uma única vez no final
    caixa_msg.send_keys(Keys.ENTER)

# ======================================================
# INICIALIZA DRIVER
# ======================================================

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, TEMPO_MAX)

driver.get("https://web.whatsapp.com")
input("Escaneie o QR Code e pressione ENTER para iniciar...")

def enviar(numero):
    try:
        url = f"https://web.whatsapp.com/send?phone={numero}&text&app_absent=0"

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)

        # Garante que entrou no chat
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "footer")))

        # Campo correto de mensagem (rodapé do chat)
        caixa_msg = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//footer//div[@contenteditable='true' and (@role='textbox' or @data-tab='10')]")
            )
        )

        caixa_msg.click()
        time.sleep(0.8)  # foco mais estável

        # DIGITA COMO UMA ÚNICA MENSAGEM (SHIFT+ENTER nas quebras)
        digitar_lento_no_whatsapp(caixa_msg, MENSAGEM)

        # Espera curta pós-envio     
        
        time.sleep(2.5)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return True

    except Exception as e:
        print(f"Erro ao enviar para {numero}: {e}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return False

# ======================================================
# PROCESSA A LISTA
# ======================================================

with open(ARQUIVO_LISTA, "r", encoding="utf-8") as f:
    numeros = [l.strip() for l in f if l.strip()]

print(f"Iniciando envio para {len(numeros)} contatos...\n")

for numero in numeros[:]:
    ok = enviar(numero)

    if ok:
        numeros.remove(numero)
        with open(ARQUIVO_LISTA, "w", encoding="utf-8") as f:
            for n in numeros:
                f.write(n + "\n")

        # Pausa segura entre contatos (ajuste se quiser)
        time.sleep(random.randint(25, 45))
    else:
        # Se falhar, pausa menor e segue (mantém na lista)
        time.sleep(random.randint(10, 15))

print("\nEnvio finalizado.")
driver.quit()
