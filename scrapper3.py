from selenium_recaptcha_solver import RecaptchaSolver
from selenium.webdriver.common.by import By
from selenium import webdriver
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning) 
import time

# Base de datos
import mysql.connector

mydb = mysql.connector.connect(
  host="osem.es",
  user="pym",
  password="password",
  database="colombia"
)


c=mydb.cursor()
c.execute("SELECT * FROM documentos LIMIT 100 OFFSET 400")
result_set = c.fetchall()
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
count = 0
for row in result_set:
    try:
        options = webdriver.FirefoxOptions()
        options.headless = True
        d = webdriver.Firefox(options=options)
        
        solver = RecaptchaSolver(driver=d)
        d.get("https://wsp.registraduria.gov.co/censo/consultar")
        placa = d.find_element(By.ID, 'nuip')
        placa.send_keys(row[1])
        recaptcha_iframe = d.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        boton=d.find_element(By.NAME, "enviar");
        d.execute_script("arguments[0].click();", boton)
        d.implicitly_wait(2)
        niup=d.find_elements(By.XPATH, '/html/body/div[1]/section[2]/div/div/div[5]/form/div[2]/div[2]/div/table/tbody/tr/td')
        mycursor = mydb.cursor()
        if(len(niup) == 6):
            sql = "INSERT INTO recopilados (niup, departamento, municipio, puesto, direccion, mesa) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (niup[0].text, niup[1].text, niup[2].text, niup[3].text, niup[4].text, niup[5].text)
            mycursor.execute(sql, val)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
            # cursor2 = mydb.cursor()
            sql2 = "DELETE FROM documentos WHERE documento = %s"
            # val2 = (niup[0].text)
            mycursor.execute(sql2, (niup[0].text,))
            mydb.commit()
            count += 1
            print(count)
        time.sleep(40)
    except:
        print("el proceso fallo")
        time.sleep(120)
    d.close()
