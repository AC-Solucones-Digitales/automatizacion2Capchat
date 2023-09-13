from selenium.webdriver.common.by import By
from selenium import webdriver
from twocaptcha import TwoCaptcha

# Base de datos
import mysql.connector

mydb = mysql.connector.connect(
  host="osem.es",
  user="pym",
  password="password",
  database="colombia"
)

c=mydb.cursor()
c.execute("SELECT * FROM documentos3 WHERE id > 600 AND id < 900")
result_set = c.fetchall()
count = 0
for row in result_set:
    try:
        print(row[0])
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        d = webdriver.Firefox(options=options)
        d.get("https://wsp.registraduria.gov.co/censo/consultar")
        placa = d.find_element(By.ID, 'nuip')
        placa.send_keys(row[1])
        # Solve the Captcha
        solver = TwoCaptcha("3ad74949feb3c5dad4345026c58d1033")
        response = solver.recaptcha(sitekey='6LcthjAgAAAAAFIQLxy52074zanHv47cIvmIHglH', url='https://wsp.registraduria.gov.co/censo/consultar')
        code = response['code']

        # Set the solved Captcha
        recaptcha_response_element = d.find_element(By.ID, 'g-recaptcha-response')
        d.execute_script(f'arguments[0].value = "{code}";', recaptcha_response_element)
        
        boton=d.find_element(By.NAME, "enviar");
        d.execute_script("arguments[0].click();", boton)
        d.implicitly_wait(1)
        niup=d.find_elements(By.XPATH, '/html/body/div[1]/section[2]/div/div/div[5]/form/div[2]/div[2]/div/table/tbody/tr/td')
        mycursor = mydb.cursor()
        if(len(niup) >= 6):
            sql = "INSERT INTO recopilados (niup, departamento, municipio, puesto, direccion, mesa, nombre, telefono) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (niup[0].text, niup[1].text, niup[2].text, niup[3].text, niup[4].text, niup[5].text, row[2], row[3])
            mycursor.execute(sql, val)
            mydb.commit()
            sql2 = "DELETE FROM documentos3 WHERE documento = %s"
            mycursor.execute(sql2, (row[1],))
            mydb.commit()
            count += 1
            print(count)
        else:
            sql2 = "DELETE FROM documentos3 WHERE documento = %s"
            mycursor.execute(sql2, (row[1],))
            mydb.commit()
        d.close()
            
    except:
        print("el proceso fallo")
        d.close()
