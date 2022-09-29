
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import smtplib
import email.message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, redirect, url_for, session, request

def send_email(email,conteudo):
    
    #configuração do e-mail
    host = "smtp.gmail.com"
    port = 587
    user = "" #https://myaccount.google.com/lesssecureapps?pli=1&rapt=AEjHL4Mx-yy3K-m6HgOuARVbgyljkIRpIclC_jfR4ziz7H5vanIrdX2TM5XAuwtmYYK9fqQg92RovYOJ12Xitsrqugn2UyHnFQ
    password = ""
    
    print("Hosting...")
    server = smtplib.SMTP(host, port)
    
    #login com servidor
    print("login...")
    server.ehlo()
    server.starttls()
    server.login(user, password)
    
    #Corpo de texto do e-mail
    message = conteudo
    print("Criando o e-mail")
    email_msg = MIMEMultipart()
    email_msg["From"] = user
    email_msg["To"] = email
    email_msg["subject"] = "Alerta de Bom Preço no Produto!"
    print("Adicionando o corpo de texto")
    email_msg.attach(MIMEText(message, "plain"))
    
    #Enviar a Mensagem
    print("Enviando mensagem...")
    server.sendmail(email_msg["From"], email_msg["To"], email_msg.as_string())
    server.quit()

#Função Scrapper que vai exigir o URL do produto e o minimo de preco para correr
def scraper(email,url, min_price):

    driver = webdriver.Chrome()

    driver.get(url)

    time.sleep(5)

    div_main = driver.find_element_by_xpath("//*[@id='ppd']") # Extrair a pagina html


    html_content = div_main.get_attribute("outerHTML")

    soup = BeautifulSoup(html_content, "html.parser")

    print(soup.prettify()) #Apresenta o HTML da pagina

    list_name = soup.select("span[id^=productTitle]") #Encontrar no HTML o nome do produto
    list_price_product = soup.find_all("span", class_="a-offscreen") #Encontrar no HTML o Preço do produto

    print("Descrição: ", list_name[0].get_text(), " Preço: ",list_price_product[0].get_text())

    driver.close()

    descricao = list_name[0].get_text()
    preco = list_price_product[0].get_text()

    preco_no_email = preco

    preco = preco.replace("€", "")

    preco = preco.replace(",", ".")

    descricao = descricao.rstrip()

    preco = float(preco)

    #Preco Maximo
    if preco < float(min_price):
        send_email(email,f"{descricao}, o preço encontra-se a {preco}")
        return '11' #Retorna 2 de tamanho
    else:
        return '404' #Retorna 3 de tamanho

app = Flask(__name__) #Inicia a app localhost:5000


@app.route('/',methods=["GET","POST"])
def main():
   if request.method == 'GET':
       return render_template("index.html")
   else:
    if request.method == 'POST': #Clicou em START
        email = request.form['email']
        url_do_produto = request.form['produto_url']
        min_preco = request.form['min_preco']


        if len(email) > 0 and len(url_do_produto) > 0 and len(min_preco) > 0: #SE TIVER ESCRITO NOS 3 TEXTBOX
            while True: #loop para seguir o preço do produto que so quebra quando o e-mail e enviado
                search = scraper(email,url_do_produto, min_preco)
                if len(search) == 2:
                    return "<script>alert('E-Mail Enviado!')</script>"

        else:
            return "<script>alert('Erro')</script>"

@app.route('/credits')
def credits():
 return render_template("credits.html")


if __name__ == '__main__':
    app.run()