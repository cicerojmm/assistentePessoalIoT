import speech_recognition as sr
from requests import get
from bs4 import BeautifulSoup
from gtts import gTTS
from paho.mqtt import publish
import os

##### CONFIGURAÇÕES #####
with open('arquivoConfiguraGoogleSpeech.json') as credenciais_google:
    credenciais_google = credenciais_google.read()
executaAcao = False

serverMQTT = 'iot.eclipse.org'
portaMQTT = 1883
topicoLuz = 'iluminacao/status'

hotword = 'verônica'
hotwordNoticias = 'notícias'
hotwordTemperatura = 'temperatura'
hotwordLigarLuz = 'ligar a luz'
hotwordDesligarLuz = 'desativar a luz'

def monitorarAudio():
    microfone = sr.Recognizer()
    with sr.Microphone() as source:
        print("Aguardando o Comando: ")
        audio = microfone.listen(source)
    try:
        trigger = microfone.recognize_google_cloud(audio, credentials_json=credenciais_google, language='pt-BR')
        trigger = trigger.lower()
        if hotword in trigger and not getStatusTrigger():
            print('Comando reconhecido!')
            respoder('feedback')
            setStatusTrigger(True)
        elif getStatusTrigger():
            setStatusTrigger(False)
            return trigger
    except sr.UnknownValueError:
        print("Google not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Cloud Speech service; {0}".format(e))

    return None

def setStatusTrigger(status):
    global executaAcao
    executaAcao = status

def getStatusTrigger():
    return executaAcao

def analisarAcao(comando):
    if hotwordNoticias in comando:
        retornarUltimasNoticias()
    elif hotwordTemperatura in comando:
        retornarPrevisaoTempo()
    elif hotwordLigarLuz in comando:
        publicarNoTopico(topicoLuz, 1)
        retornarIluminacao(1)
    elif hotwordDesligarLuz in comando:
        publicarNoTopico(topicoLuz, 0)
        retornarIluminacao(0)
    else:
        criarAudio(comando.strip(hotword), 'comando')
        respoder('comando')
        respoder('notfound')

def retornarUltimasNoticias():
    site = get('https://news.google.com/news/rss?ned=pt_br&gl=BR&hl=pt')
    noticias = BeautifulSoup(site.text, 'html.parser')
    for item in noticias.findAll('item')[:2]:
        noticia = item.title.text
        criarAudio(noticia, 'noticia')
        respoder('noticia')
    respoder('thau')

def retornarPrevisaoTempo():
    site = get('http://api.openweathermap.org/data/2.5/weather?id=3462377&q=goiania,br&APPID=1d20fd1ca254ea2797f60e64520675a8&units=metric&lang=pt')
    clima = site.json()
    temperatura = clima['main']['temp']
    #minima = clima['main']['temp_min']
    #maxima = clima['main']['temp_max']
    descricao = clima['weather'][0]['description']
    mensagem = f'No momento a temperatura é de {temperatura} graus com {descricao}'
    criarAudio(mensagem, 'clima')
    respoder('clima')
    respoder('thau')

def retornarIluminacao(status):
    if status == 1:
        mensagem = 'A luz foi ligada'
    else:
        mensagem = 'A luz foi desligada'
    criarAudio(mensagem, 'iluminacao')
    respoder('iluminacao')
    respoder('thau')

def publicarNoTopico(topico, payload):
    publish.single(topico, payload=payload, qos=1, retain=True, hostname=serverMQTT,
           port=portaMQTT, client_id="veronica")

def criarAudio(texto, nome_arquivo):
    tts = gTTS(texto, lang='pt-br')
    path = 'audios/' + nome_arquivo + '.mp3'
    with open(path, 'wb') as file:
        tts.write_to_fp(file)

def respoder(nome_arquivo):
    path = 'audios/' + nome_arquivo + '.mp3'
    os.system('mpg321 ' + path)

def __main__():
    while True:
        comando = monitorarAudio()
        if comando is not None:
            analisarAcao(comando)

__main__()
