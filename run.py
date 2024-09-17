import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import time

print('inicio')

# Função para carregar a tabela de destinatários
def carregar_destinatarios(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
    print('df carregado')
    return df

# Função para carregar o template HTML com codificação UTF-8
def carregar_template_html(caminho_html):
    with open(caminho_html, 'r', encoding='utf-8') as file:
        html_content = file.read()
    print('template carregado')
    return html_content

# Função para personalizar o HTML para cada destinatário
def personalizar_email(html_content, nome_destinatario):
    print('template personalizado')
    return html_content.replace('{{NOME}}', nome_destinatario)

# Função para enviar e-mails
def enviar_email(destinatario, assunto, conteudo_html, remetente, senha_remetente):
    msg = MIMEMultipart('alternative')
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto

    # Adiciona o cabeçalho de Content-Type com codificação UTF-8
    conteudo_html_utf8 = MIMEText(conteudo_html, 'html', 'utf-8')
    msg.attach(conteudo_html_utf8)

    # Conectando ao servidor SMTP
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Usar TLS para segurança
            server.login(remetente, senha_remetente)
            server.sendmail(remetente, destinatario, msg.as_string())
            print(f"E-mail enviado para {destinatario}")
    except Exception as e:
        print(f"Erro ao enviar e-mail para {destinatario}: {e}")

# Função para enviar 100 e-mails por hora
def enviar_emails_controlado(arquivo_csv, caminho_html, remetente, senha_remetente, assunto):
    # Carregar template HTML e destinatários
    html_content = carregar_template_html(caminho_html)
    df_destinatarios = carregar_destinatarios(arquivo_csv)

    emails_enviados = 0
    inicio_intervalo = time.time()  # Marca o tempo inicial

    # Itera sobre os destinatários
    for index, row in df_destinatarios.iterrows():
        email_destinatario = row['Email']
        nome_destinatario = row['Nome']
        email_personalizado = personalizar_email(html_content, nome_destinatario)

        # Envia o e-mail
        enviar_email(email_destinatario, assunto, email_personalizado, remetente, senha_remetente)
        emails_enviados += 1

        # Verifica se já enviou 100 e-mails em uma hora
        if emails_enviados >= 100:
            tempo_passado = time.time() - inicio_intervalo
            if tempo_passado < 3600:  # 3600 segundos = 1 hora
                tempo_espera = 3600 - tempo_passado
                print(f"Aguardando {tempo_espera / 60:.2f} minutos para enviar mais e-mails...")
                time.sleep(tempo_espera)  # Aguarda o tempo restante da hora

            # Reinicia o contador e o tempo
            emails_enviados = 0
            inicio_intervalo = time.time()

        # Pausa de 36 segundos entre cada e-mail para garantir menos de 100/h
        time.sleep(36)

if __name__ == "__main__":
    remetente = ""
    senha_remetente = ""
    assunto = ""
    
    caminho_html = ""
    arquivo_csv = ""
    
    enviar_emails_controlado(arquivo_csv, caminho_html, remetente, senha_remetente, assunto)
