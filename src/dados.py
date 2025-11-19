import requests
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Configurações - Lucas
REPO = "shutterstock/rickshaw"  
TOKEN = "" # Token removido por segurança - insira seu token aqui se precisar fazer nova coleta

# Diretório para salvar os dados coletados (path absoluto relativo a este arquivo)
# Usa o diretório pai do pacote `src` para localizar `dados_coletados`, tornando o carregamento
# independente do diretório de trabalho atual quando o script é executado.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'dados_coletados'))
OS_ISSUES_FILE = os.path.join(DATA_DIR, 'issues.json')
OS_PULLS_FILE = os.path.join(DATA_DIR, 'pulls.json')
OS_INTERACOES_FILE = os.path.join(DATA_DIR, 'interacoes.json')
OS_METADADOS_FILE = os.path.join(DATA_DIR, 'metadados.json')

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Função para criar diretório de dados se não existir
def criar_diretorio_dados():
    """Cria o diretório para armazenar os dados coletados."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Diretório '{DATA_DIR}' criado.")

# Função para salvar dados em arquivo JSON
def salvar_json(dados: any, arquivo: str, indent: int = 2):
    """Salva dados em um arquivo JSON."""
    criar_diretorio_dados()
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=indent, ensure_ascii=False)
    print(f"Dados salvos em: {arquivo}")

# Função para carregar dados de um arquivo JSON
def carregar_json(arquivo: str) -> Optional[any]:
    """Carrega dados de um arquivo JSON."""
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Função para lidar com paginação da API do GitHub - Lucas
def get_paginated(url: str) -> List[Dict]:
    """
    Pega os resultados da API do GitHub com paginação.
    
    Args:
        url: URL da API do GitHub
        
    Returns:
        Lista de resultados paginados
    """
    resultados = []
    while url:
        try:
            r = requests.get(url, headers=HEADERS)
            if r.status_code != 200:
                print(f"Erro {r.status_code} em {url}")
                if r.status_code == 403:
                    print("Possível limite de taxa da API atingido. Aguardando...")
                    time.sleep(60)
                    continue
                break
            dados = r.json()
            if isinstance(dados, list):
                resultados.extend(dados)
            else:
                resultados.append(dados)
            
            if "next" in r.links:
                url = r.links["next"]["url"]
            else:
                url = None
            time.sleep(0.5)  # Respeita rate limit da API
        except Exception as e:
            print(f"Erro ao processar {url}: {e}")
            break
    return resultados

# Pega as issues do repositório - Lucas    
def coletar_issues() -> List[Dict]:
    """
    Coleta todas as issues do repositório (abertas e fechadas).
    
    Returns:
        Lista de issues
    """
    print("Coletando issues...")
    url = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100"
    issues = get_paginated(url)
    print(f"Total de issues coletadas: {len(issues)}")
    return issues

# Pega os pull requests do repositório - Lucas
def coletar_pulls() -> List[Dict]:
    """
    Coleta todos os pull requests do repositório (abertos e fechados).
    
    Returns:
        Lista de pull requests
    """
    print("Coletando pull requests...")
    url = f"https://api.github.com/repos/{REPO}/pulls?state=all&per_page=100"
    pulls = get_paginated(url)
    print(f"Total de pull requests coletados: {len(pulls)}")
    return pulls

# Pega os comentários de uma issue específica - Lucas
def coletar_comentarios_issue(issue_number: int) -> List[Dict]:
    """
    Coleta todos os comentários de uma issue específica.
    
    Args:
        issue_number: Número da issue
        
    Returns:
        Lista de comentários da issue
    """
    url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments?per_page=100"
    return get_paginated(url)

# Pega as reviews de um pull request específico - Lucas
def coletar_reviews(pr_number: int) -> List[Dict]:
    """
    Coleta todas as reviews de um pull request específico.
    
    Args:
        pr_number: Número do pull request
        
    Returns:
        Lista de reviews do pull request
    """
    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/reviews?per_page=100"
    return get_paginated(url)

# Pega os comentários de um pull request específico - Lucas
def coletar_comentarios_pr(pr_number: int) -> List[Dict]:
    """
    Coleta todos os comentários de um pull request específico.
    
    Args:
        pr_number: Número do pull request
        
    Returns:
        Lista de comentários do pull request
    """
    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/comments?per_page=100"
    return get_paginated(url)

# Extrai informações relevantes de uma issue para análise de grafos
def processar_issue(issue: Dict) -> Dict:
    """
    Processa uma issue e extrai informações relevantes para construção do grafo.
    
    Args:
        issue: Dados da issue da API do GitHub
        
    Returns:
        Dicionário com informações processadas da issue
    """
    dados_processados = {
        "numero": issue.get("number"),
        "titulo": issue.get("title"),
        "autor": issue.get("user", {}).get("login") if issue.get("user") else None,
        "estado": issue.get("state"),
        "fechado_por": issue.get("closed_by", {}).get("login") if issue.get("closed_by") else None,
        "data_criacao": issue.get("created_at"),
        "data_fechamento": issue.get("closed_at"),
        "eh_pull_request": issue.get("pull_request") is not None,
        "url": issue.get("url"),
        "html_url": issue.get("html_url")
    }
    return dados_processados

# Extrai informações relevantes de um pull request para análise de grafos
def processar_pull_request(pull: Dict) -> Dict:
    """
    Processa um pull request e extrai informações relevantes para construção do grafo.
    
    Args:
        pull: Dados do pull request da API do GitHub
        
    Returns:
        Dicionário com informações processadas do pull request
    """
    dados_processados = {
        "numero": pull.get("number"),
        "titulo": pull.get("title"),
        "autor": pull.get("user", {}).get("login") if pull.get("user") else None,
        "estado": pull.get("state"),
        "merged": pull.get("merged"),
        "merged_by": pull.get("merged_by", {}).get("login") if pull.get("merged_by") else None,
        "mergeable": pull.get("mergeable"),
        "data_criacao": pull.get("created_at"),
        "data_fechamento": pull.get("closed_at"),
        "data_merge": pull.get("merged_at"),
        "url": pull.get("url"),
        "html_url": pull.get("html_url")
    }
    return dados_processados

# Coleta e processa todas as interações do repositório
def coletar_todas_interacoes(issues: List[Dict], pulls: List[Dict]) -> Dict:
    """
    Coleta todas as interações (comentários, reviews, fechamentos, merges) do repositório.
    
    Args:
        issues: Lista de issues coletadas
        pulls: Lista de pull requests coletados
        
    Returns:
        Dicionário com todas as interações organizadas por tipo
    """
    print("\nColetando interações detalhadas...")
    interacoes = {
        "comentarios_issues": [],
        "comentarios_pulls": [],
        "reviews_pulls": [],
        "fechamentos_issues": [],
        "merges_pulls": []
    }
    
    # Processa issues (apenas issues, não pull requests)
    # A API do GitHub retorna pull requests quando buscamos issues
    # Pull requests têm o campo "pull_request" não nulo
    issues_reais = [issue for issue in issues if not issue.get("pull_request")]
    print(f"Processando {len(issues_reais)} issues...")
    
    for i, issue in enumerate(issues_reais, 1):
        if i % 10 == 0:
            print(f"  Processando issue {i}/{len(issues_reais)}...")
        
        issue_num = issue.get("number")
        autor_issue = issue.get("user", {}).get("login") if issue.get("user") else None
        
        # Coleta comentários da issue
        # Abertura de issue comentada por outro usuário: peso 3
        comentarios = coletar_comentarios_issue(issue_num)
        for comentario in comentarios:
            autor_comentario = comentario.get("user", {}).get("login") if comentario.get("user") else None
            if autor_comentario and autor_comentario != autor_issue:
                interacoes["comentarios_issues"].append({
                    "issue_numero": issue_num,
                    "autor_issue": autor_issue,
                    "autor_comentario": autor_comentario,
                    "data_comentario": comentario.get("created_at"),
                    "tipo": "comentario_issue",
                    "peso": 3  # Abertura de issue comentada por outro usuário
                })
        
        # Verifica fechamento de issue por outro usuário
        fechado_por = issue.get("closed_by", {}).get("login") if issue.get("closed_by") else None
        if fechado_por and fechado_por != autor_issue:
            interacoes["fechamentos_issues"].append({
                "issue_numero": issue_num,
                "autor_issue": autor_issue,
                "fechado_por": fechado_por,
                "data_fechamento": issue.get("closed_at"),
                "tipo": "fechamento_issue",
                "peso": 3
            })
    
    # Processa pull requests
    print(f"Processando {len(pulls)} pull requests...")
    for i, pull in enumerate(pulls, 1):
        if i % 10 == 0:
            print(f"  Processando PR {i}/{len(pulls)}...")
        
        pr_num = pull.get("number")
        autor_pr = pull.get("user", {}).get("login") if pull.get("user") else None
        
        # Coleta comentários gerais na conversa do PR (usando endpoint de issues, pois PRs são issues)
        comentarios_conversa = coletar_comentarios_issue(pr_num)
        for comentario in comentarios_conversa:
            autor_comentario = comentario.get("user", {}).get("login") if comentario.get("user") else None
            if autor_comentario and autor_comentario != autor_pr:
                interacoes["comentarios_pulls"].append({
                    "pr_numero": pr_num,
                    "autor_pr": autor_pr,
                    "autor_comentario": autor_comentario,
                    "data_comentario": comentario.get("created_at"),
                    "tipo": "comentario_pr_conversa",
                    "peso": 2
                })
        
        # Coleta comentários em linhas de código do pull request (review comments)
        comentarios_review = coletar_comentarios_pr(pr_num)
        for comentario in comentarios_review:
            autor_comentario = comentario.get("user", {}).get("login") if comentario.get("user") else None
            if autor_comentario and autor_comentario != autor_pr:
                interacoes["comentarios_pulls"].append({
                    "pr_numero": pr_num,
                    "autor_pr": autor_pr,
                    "autor_comentario": autor_comentario,
                    "data_comentario": comentario.get("created_at"),
                    "tipo": "comentario_pr_review",
                    "peso": 2
                })
        
        # Coleta reviews do pull request
        reviews = coletar_reviews(pr_num)
        for review in reviews:
            revisor = review.get("user", {}).get("login") if review.get("user") else None
            estado_review = review.get("state")  # APPROVED, CHANGES_REQUESTED, COMMENTED
            if revisor and revisor != autor_pr and estado_review in ["APPROVED", "CHANGES_REQUESTED"]:
                interacoes["reviews_pulls"].append({
                    "pr_numero": pr_num,
                    "autor_pr": autor_pr,
                    "revisor": revisor,
                    "estado_review": estado_review,
                    "data_review": review.get("submitted_at"),
                    "tipo": "review_pr",
                    "peso": 4
                })
        
        # Verifica merge do pull request
        merged_by = pull.get("merged_by", {}).get("login") if pull.get("merged_by") else None
        if pull.get("merged") and merged_by and merged_by != autor_pr:
            interacoes["merges_pulls"].append({
                "pr_numero": pr_num,
                "autor_pr": autor_pr,
                "merged_by": merged_by,
                "data_merge": pull.get("merged_at"),
                "tipo": "merge_pr",
                "peso": 5
            })
    
    return interacoes

# Função principal para executar a coleta completa de dados
def executar_coleta_completa():
    """
    Executa a coleta completa de dados do repositório e salva em arquivos JSON.
    """
    print("=" * 60)
    print("INICIANDO COLETA DE DADOS DO REPOSITÓRIO")
    print(f"Repositório: {REPO}")
    print("=" * 60)
    
    # Verifica se o token foi configurado
    if not TOKEN:
        print("ERRO: Token do GitHub não configurado!")
        print("Por favor, configure a variável TOKEN no código.")
        return
    
    try:
        # Coleta issues e pull requests
        issues = coletar_issues()
        pulls = coletar_pulls()
        
        # Processa issues e pulls para extrair informações relevantes
        issues_processadas = [processar_issue(issue) for issue in issues]
        pulls_processados = [processar_pull_request(pull) for pull in pulls]
        
        # Coleta todas as interações
        interacoes = coletar_todas_interacoes(issues, pulls)
        
        # Salva dados em arquivos JSON
        print("\nSalvando dados coletados...")
        salvar_json(issues_processadas, OS_ISSUES_FILE)
        salvar_json(pulls_processados, OS_PULLS_FILE)
        salvar_json(interacoes, OS_INTERACOES_FILE)
        
        # Salva metadados da coleta
        metadados = {
            "repositorio": REPO,
            "data_coleta": datetime.now().isoformat(),
            "total_issues": len(issues_processadas),
            "total_pulls": len(pulls_processados),
            "total_comentarios_issues": len(interacoes["comentarios_issues"]),
            "total_comentarios_pulls": len(interacoes["comentarios_pulls"]),
            "total_reviews": len(interacoes["reviews_pulls"]),
            "total_fechamentos": len(interacoes["fechamentos_issues"]),
            "total_merges": len(interacoes["merges_pulls"])
        }
        salvar_json(metadados, OS_METADADOS_FILE)
        
        print("\n" + "=" * 60)
        print("COLETA CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"Issues coletadas: {metadados['total_issues']}")
        print(f"Pull Requests coletados: {metadados['total_pulls']}")
        print(f"Comentários em issues: {metadados['total_comentarios_issues']}")
        print(f"Comentários em PRs: {metadados['total_comentarios_pulls']}")
        print(f"Reviews: {metadados['total_reviews']}")
        print(f"Fechamentos de issues: {metadados['total_fechamentos']}")
        print(f"Merges: {metadados['total_merges']}")
        print(f"\nDados salvos em: {DATA_DIR}/")
        
    except Exception as e:
        print(f"\nERRO durante a coleta: {e}")
        import traceback
        traceback.print_exc()

# Função para carregar dados coletados
def carregar_dados_coletados() -> Dict:
    """
    Carrega todos os dados coletados dos arquivos JSON.
    
    Returns:
        Dicionário com issues, pulls, interações e metadados
    """
    dados = {
        "issues": carregar_json(OS_ISSUES_FILE),
        "pulls": carregar_json(OS_PULLS_FILE),
        "interacoes": carregar_json(OS_INTERACOES_FILE),
        "metadados": carregar_json(OS_METADADOS_FILE)
    }
    
    if dados["metadados"]:
        print("Dados carregados com sucesso!")
        print(f"Data da coleta: {dados['metadados'].get('data_coleta')}")
    else:
        print("Nenhum dado encontrado. Execute a coleta primeiro.")
    
    return dados

if __name__ == "__main__":
    # Executa a coleta completa quando o script é executado diretamente
    executar_coleta_completa()

