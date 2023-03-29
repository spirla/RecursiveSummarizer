import openai
import os
import textwrap
import regex as re
import nltk
nltk.download('punkt')
import time

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

openai.api_key = open_file('openaiapikey.txt')

def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def gpt3_completion(prompt, engine='text-davinci-003', temp=0.11, top_p=1.0, tokens=750, freq_pen=0, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            time.sleep(1)

if __name__ == '__main__':
    alltext = open_file('input2.txt')
    sentence_list = nltk.sent_tokenize(alltext)
    print  (len(sentence_list))
    result = []
    count = 0
    
    chunk_size = 16
    chunk_len = 0
    chunk = []
    
    for sentence in sentence_list:
        if chunk_len + len(sentence) > 2400 and chunk_len > 0:
            # Complete the current chunk and start a new one
            result.append(" ".join(chunk))
            chunk = []
            chunk_len = 0
        
        chunk.append(sentence)
        chunk_len += len(sentence)
        
        if len(chunk) >= chunk_size or chunk_len > 2600:
            # Complete the current chunk and start a new one
            result.append(" ".join(chunk))
            chunk = []
            chunk_len = 0
            
    if chunk:
        result.append(" ".join(chunk))
        
    for chunk in result:
        count = count + 1
        prompt = open_file('resumojuris.txt').replace('<<SUMARIO>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt3_completion(prompt)
        print('\n\n\n', count, 'of', len(result), ' - ', summary)
        
    save_file('\n\n'.join(result), 'output1_%s.txt' % time.time())