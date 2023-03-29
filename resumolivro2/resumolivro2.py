import openai
from time import time, sleep
import re
import nltk
import os
import sys

nltk.download('punkt')

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
def remove_multiple_spaces(text):
    return re.sub('\s+', ' ', text).strip()    

openai.api_key = open_file('openaiapikey.txt')

def replace_ptbr_chars(text):
    ptbr_chars = 'áàãâéêíóôõúüçÁÀÃÂÉÊÍÓÔÕÚÜÇ'
    ascii_chars = 'aaaaeeiooouucAAAAEEIOOOUUC'
    trans_table = str.maketrans(ptbr_chars, ascii_chars)
    return text.translate(trans_table)

def preprocess(text):
    text = text.lower()
    text = replace_ptbr_chars(text)
    text = remove_multiple_spaces(text)

    return text

def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def gpt4_completion(prompt, engine='gpt-3.5-turbo', temp=0.3, top_p=1.0, tokens=1500, freq_pen=0.15, pres_pen=0.15, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    prompt = preprocess(prompt)
    while True:
        try:
            print("Resumindo...")
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                    {"role": "system", "content": "Você é um consultor jurídico que resume textos de forma técnica e precisa, sem excluir seu conteúdo ou alterar o sentido do texto."},
                    {"role": "assistant", "content": "Olá. Vou resumir a passagem de texto fornecida de forma extensiva e completa, mantendo todas as informações que constam do original, incluindo menções a artigos de lei, decisões judiciais e súmulas de jurisprudência."},
                    {"role": "user", "content": "Faça um resumo do texto sem usar frases introdutórias comuns como 'o texto aborda' ou 'o texto trata'"},
                    {"role": "assistant", "content": "Entendi."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['message']['content'].strip()
            text = re.sub('\s+', ' ', text)
            if not os.path.exists('gpt4_logs'):
                os.makedirs('gpt4_logs')
            filename = '%s_gpt4.txt' % time()
            with open('gpt4_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            in_len = len(prompt)
            out_len = len(text)
            approx_tokens = (in_len + out_len) / 3 # Média de tokens por caractere
            print(f"Foram requisitados aproximadamente {approx_tokens:.2f} tokens.")
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT4 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

if __name__ == '__main__':
    alltext = open_file('Improbidade Administrativa - 2022 - Daniel Amorim e Rafael Carvalho.txt')
    sentence_list = nltk.sent_tokenize(alltext)
    chunks = []
    output = []
    count = 0

    CHUNK_SIZE = 60
    CHUNK_LEN = 0
    chunk = []

    print("Dividindo o texto em chunks...")
    for sentence in sentence_list:
        if CHUNK_LEN + len(sentence) > 7000 and CHUNK_LEN > 0:
            chunks.append(" ".join(chunk))
            chunk = []
            CHUNK_LEN = 0

        chunk.append(sentence)
        CHUNK_LEN += len(sentence)

        if len(chunk) >= CHUNK_SIZE or CHUNK_LEN > 7500:
            chunks.append(" ".join(chunk))
            chunk = []
            CHUNK_LEN = 0

    if chunk:
        chunks.append(" ".join(chunk))

    print(f"Total de chunks criados: {len(chunks)}")

    print("Iniciando o processo de resumir cada chunk do texto...")
    for chunk in chunks:
        count += 1
        prompt = open_file('prompt.txt').replace('<<SUMMARY>>', chunk)
        summary = gpt4_completion(prompt)
        print('\n\n\nChunk', count, 'of', len(chunks), ' - Resumo:')
        print(summary)
        output.append(summary)
        progress = (count / len(chunks)) * 100
        sys.stdout.write("\rProgresso: %.2f%%" % progress)
        sys.stdout.flush()

    save_file('\n\n'.join(output), 'output_%d.txt' % int(time()))