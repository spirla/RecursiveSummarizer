import openai
import time
import re
import pandas as pd

with open('openaiapikey.txt', 'r') as file:
    openai.api_key = file.read().replace('\n', '')

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def gpt3_completion(prompt, engine='text-davinci-003', temp=0.7, max_tokens=100, freq_pen=0.0, pres_pen=0.0, stop=['\n']):
    try:
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=temp,
            max_tokens=max_tokens,
            frequency_penalty=freq_pen,
            presence_penalty=pres_pen,
            stop=stop)
        text = response['choices'][0]['text'].strip()
        text = re.sub('\s+', ' ', text)
        return text
    except Exception as oops:
        print('Error communicating with OpenAI:', oops)
        return "GPT3 error: %s"

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if __name__ == 'main':
    alltext = pd.read_excel('perguntas.xlsx')
    output = []
    prompt = open_file('prompt.txt')

    chunk_size = 1 # tamanho máximo de cada chunk
    chunks_list = list(chunks(alltext.iterrows(), chunk_size)) # cria a lista de chunks

    for chunk in chunks_list:
        for index, row in chunk:
            prompt_summ = prompt.replace('<<SUMMARY>>', row['pergunta'])
            print 
            summary = gpt3_completion(prompt_summ)
            print('Question:', row['pergunta'])
            print('Answer:', summary)
            output.append(summary)

    save_file('\n\n'.join(output), 'output_%d.txt' % int(time.time()))