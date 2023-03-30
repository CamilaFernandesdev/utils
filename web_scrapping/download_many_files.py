import requests

defdownload_many_files(url, path):
    # Faz a requisição no servidor
    response = requests.get(url)
    if response.status_code == response.codes.OK:
        with open(path, 'wb') as new_file:
            new_file.write(response.content)
        print('Downloaded file: ' + path)
        
    else:
        response.raise_for_status()
        
        
if __name__ == '__main__':
    BASE_URL = 'http://math.mit.edu/classes/18.745/Notes/Lecture_{}_Notes.pdf'
    OUTPUT_DIR = 'PATH'
    
    # São 26 aquivos para download no curso do MIT
    for i in range(1, 26):
        output_filename = os.path.join(OUTPUT_DIR, 'aula_mit_math_{}.pdf'.format(i))
       download_many_files(BASE_URL.format(i), output_filename)
