from gtts import gTTS
from subprocess import call

def cria_audio(texto, nome_arquivo):
    tts = gTTS(texto, lang='pt-br')
    path = 'audios/' + nome_arquivo + '.mp3'
    with open(path, 'wb') as file:
        tts.write_to_fp(file)
    call(['mpg321', path])

cria_audio('Olá, pode falar que eu faço', 'feedback')