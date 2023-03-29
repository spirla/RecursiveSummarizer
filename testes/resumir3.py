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

def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def gpt3_completion(prompt, engine='text-davinci-003', temp=0.18, top_p=1.0, tokens=750, freq_pen=0, pres_pen=0.0, stop=['<<END>>']):
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

if __name__ == '__main__':
    openai.api_key = open_file('openaiapikey.txt')
    input_file = 'input1.txt'
    instructions_file = 'instruções.txt'
    alltext = open_file(input_file)
    sentence_list = nltk.sent_tokenize(alltext)

    CHUNK_SIZE = 16
    CHUNK_LENGTH_LIMIT = 2400
    result = []
    chunk_num = 0

    chunk = []
    chunk_length = 0

    for sentence in sentence_list:
        if chunk_length + len(sentence) > CHUNK_LENGTH_LIMIT and chunk_length > 0:
            result.append(" ".join(chunk))
            chunk = []
            chunk_length = 0
        
        chunk.append(sentence)
        chunk_length += len(sentence)
        
        if len(chunk) >= CHUNK_SIZE or chunk_length > 2600:
            result.append(" ".join(chunk))
            chunk = []
            chunk_length = 0
            
    if chunk:
        result.append(" ".join(chunk))
        
    for chunk in result:
        chunk_num += 1
        prompt = open_file(instructions_file).replace('<<SUMARIO>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt3_completion(prompt)
        print(f'\n\n\nChunk {chunk_num} of {len(result)} - {summary}')
        
    output_file = f'output1_{time.time()}.txt'
    save_file('\n\n'.join(summary), output_file)
    print(f'\n\nResults saved to file: {output_file}')