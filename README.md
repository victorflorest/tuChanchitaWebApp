# Trabajo Final Algoritmos Y Estructuras de Programación (Versión Aplicación Web)

Versiones (26/05/2025): 
+ Python 3.9.5
+ annotated-types==0.7.0
+ anyio==4.9.0
+ arabic-reshaper==3.0.0
+ asgiref==3.8.1
+ asn1crypto==1.5.1
+ certifi==2025.4.26
+ cffi==1.17.1
+ chardet==5.2.0
+ charset-normalizer==3.4.2
+ click==8.1.8
+ colorama==0.4.6
+ cryptography==45.0.3
+ cssselect2==0.8.0
+ defusedxml==0.7.1
+ distro==1.9.0
+ Django==5.2.1
+ h11==0.16.0
+ html5lib==1.1
+ httpcore==1.0.9
+ httpx==0.28.1
+ idna==3.10
+ jiter==0.10.0
+ lxml==5.4.0
+ openai==1.82.0
+ oscrypto==1.3.0
+ pillow==11.2.1
+ pycparser==2.22
+ pydantic==2.11.5
+ pydantic_core==2.33.2
+ pyHanko==0.28.0
+ pyhanko-certvalidator==0.27.0
+ pypdf==5.5.0
+ python-bidi==0.6.6
+ PyYAML==6.0.2
+ qrcode==8.2
+ reportlab==4.4.1
+ requests==2.32.3
+ six==1.17.0
+ sniffio==1.3.1
+ sqlparse==0.5.3
+ svglib==1.5.1
+ tinycss2==1.4.0
+ tqdm==4.67.1
+ typing-inspection==0.4.1
+ typing_extensions==4.13.2
+ tzdata==2025.2
+ tzlocal==5.3.1
+ uritools==5.0.0
+ urllib3==2.4.0
+ webencodings==0.5.1
+ xhtml2pdf==0.2.17

## Paso 1:
+ Instalar Python 3.13.3
+ https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe
+ Activar la opción de añadir al path en la instalación y para todos los usuarios

## Paso 2:

+ Clonar repositorio
+ git clone -b Branch_Manuel --single-branch https://github.com/victorflorest/tuChanchita-App.git

## Paso 3:

+ Abrimos la carpeta en VSCode y nos dirigimos a la terminal e ingresamos los siguientes comandos:

+ py -3.13 -m venv venv

+ .\venv\Scripts\activate

+ en caso esto no funcione ejecutamos como administrados el powershell y ejecutamos el siguiente comando:

+ Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

+ y luego presionamos "S" para confirmar el comando

+ volvemos a ejecutar ".\venv\Scripts\activate" en la terminal del visual studio code y nos debería aparecer entre parentesis y de color verde (venv) al comienzo de la linea de comandos

## Paso 4:

+ Instalaremos las librerías

+ pip install -r requirements.txt

## Paso 5 (Funcionalidad del chatbot)

+ Navegamos a la carpeta ./tuchanchita

+ Abrimos settings.py

+ Ingresamos la llave Twelve API Key y la llave OpenAI API Key en las últimas líneas donde corresponde

## Paso 6:

+ Ejecutamos el programa

+ python manage.py runserver

## Paso 7:

+ Abrimos nuestro navegador web de preferencia y entramos a la siguiente URL: http://127.0.0.1:8000/


## En caso cierras y vuelvas a abrir y no puedas ejecutar con "python manage.py runserver" solo escribe este comando .\venv\Scripts\activate y ya podrás o presiona F1 escribes Select Interpreter y selecciona el que contenga venv y así podrás ejecutar el programa sin necesidad de escribir .\venv\Scripts\activate cada que salgas y entres del programa

## Instrucciones por IDE
# VSCode
+ `Ctrl + Shift + P`
+ Abrir settings.json
+ Cambiar el servidor de python a Pylance
+ `"python.languageServer": "Pylance"`
+ Recomendado usar el plugin Code Runner