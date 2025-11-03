import requests
import time

# token de acesso pessoal do GitHub com permissões adequadas - Lucas 

REPO = "shutterstock/rickshaw"  
TOKEN = "" # querido professor, você não vê o token de acesso pois é um dado sensivel, por isso toda vez que baixamos o código temos que inserir manualmente

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Função para lidar com paginação da API do GitHub(pega os resultados da API) - Lucas

def get_paginated(url):
    resultados = []
    while url:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print(f"Erro {r.status_code} em {url}")
            break
        resultados.extend(r.json())
        if "next" in r.links:
            url = r.links["next"]["url"]
        else:
            url = None
        time.sleep(0.5)  
    return resultados

# Pega as issues do repositório - Lucas    

def coletar_issues():
    url = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100"
    return get_paginated(url)

# Pega os pull requests do repositório - Lucas

def coletar_pulls():
    url = f"https://api.github.com/repos/{REPO}/pulls?state=all&per_page=100"
    return get_paginated(url)

# Pega os comentários de uma issue específica - Lucas

def coletar_comentarios_issue(issue_url):
    return get_paginated(issue_url)

# Pega as reviews de um pull request específico - Lucas

def coletar_reviews(pr_number):
    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/reviews?per_page=100"
    return get_paginated(url)

# Pega os comentários de um pull request específico - Lucas

def coletar_comentarios_pr(pr_number):
    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/comments?per_page=100"
    return get_paginated(url)

