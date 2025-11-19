from AdjacencyMatrixGraph import AdjacencyMatrixGraph
from dados import carregar_dados_coletados

class PullRequestReviewGraphMatrixAd:
    """
    Classe específica para modelar o Grafo 3: revisões/aprovações/merges de pull requests.
    Versão usando Matriz de Adjacência.
    
    Cada usuário é representado como um nó.
    As interações de revisão/aprovação/merge são representadas como arestas direcionadas.
    
    Convenção adotada:
    - Uma aresta é criada de quem FAZ A REVISÃO/MERGE para quem CRIOU o PR,
      desde que sejam usuários distintos.
      Ex.: se user_X revisa/aprova/faz merge de um PR criado por user_Y (user_X != user_Y),
           adicionamos uma aresta user_X → user_Y.
    O grafo é simples e direcionado.
    """
    
    def __init__(self):
        """
        Construtor do grafo de revisões/merges de pull requests.
        Carrega os dados coletados e constrói o grafo usando matriz de adjacência.
        """
        self.dados = carregar_dados_coletados()
        self.usuarios = {}          # Mapear usuário -> índice do vértice
        self.usuarios_reverso = {}  # Mapear índice -> usuário
        self.grafo = None
        
        self._construir_grafo()
    
    def _extrair_usuarios(self):
        """
        Extrai todos os usuários únicos relevantes para o grafo 3.
        
        Aqui consideramos:
        - autor de pull requests
        - revisores de pull requests
        - usuários que fazem merge de pull requests
        """
        usuarios_set = []
        
        # Extrai usuários dos pull requests
        if self.dados.get("pulls"):
            for pull in self.dados["pulls"]:
                autor = pull.get("autor")
                merged_by = pull.get("merged_by")
                
                if autor and autor not in usuarios_set:
                    usuarios_set.append(autor)
                if merged_by and merged_by not in usuarios_set:
                    usuarios_set.append(merged_by)
        
        # Extrai usuários das revisões de pull requests
        if self.dados.get("interacoes") and self.dados["interacoes"].get("reviews_pulls"):
            for review in self.dados["interacoes"]["reviews_pulls"]:
                autor_pr = review.get("autor_pr")
                revisor = review.get("revisor")
                
                if autor_pr and autor_pr not in usuarios_set:
                    usuarios_set.append(autor_pr)
                if revisor and revisor not in usuarios_set:
                    usuarios_set.append(revisor)
        
        # Cria mapeamento usuário -> índice
        for i, usuario in enumerate(usuarios_set):
            self.usuarios[usuario] = i
            self.usuarios_reverso[i] = usuario
        
        print(f"Total de usuários únicos encontrados (Grafo 3 - Matriz): {len(usuarios_set)}")
        return len(usuarios_set)
    
    def _construir_grafo(self):
        """
        Constrói o grafo de revisões/merges de pull requests baseado nos dados coletados.
        """
        print("Construindo grafo de revisões/merges de pull requests (Grafo 3 - Matriz)...")
        
        # Extrai usuários únicos
        num_usuarios = self._extrair_usuarios()
        
        if num_usuarios == 0:
            print("Nenhum usuário encontrado nos dados para o Grafo 3!")
            return
        
        # Cria o grafo com matriz de adjacência
        self.grafo = AdjacencyMatrixGraph(num_usuarios)
        print(f"🔢 Usando Matriz de Adjacência com {num_usuarios} usuários")
        
        # Adiciona arestas baseadas nas revisões e merges
        self._adicionar_arestas_reviews()
        self._adicionar_arestas_merges()
        
        print(f"✅ Grafo 3 (Matriz) construído com {self.grafo.getVertexCount()} vértices e {self.grafo.getEdgeCount()} arestas")
    
    def _adicionar_arestas_reviews(self):
        """
        Adiciona arestas baseadas nas revisões de pull requests.
        
        Regra:
        - Se um PR foi criado por 'autor_pr' e revisado por 'revisor'
          e autor_pr != revisor, então adicionamos uma aresta:
            revisor → autor_pr
        """
        if not self.dados.get("interacoes") or not self.dados["interacoes"].get("reviews_pulls"):
            print("Nenhuma revisão de PR encontrada para o Grafo 3!")
            return
        
        arestas_adicionadas = 0
        
        for review in self.dados["interacoes"]["reviews_pulls"]:
            # Campos esperados em cada revisão:
            autor_pr = review.get("autor_pr")
            revisor = review.get("revisor")
            estado_review = review.get("estado_review")
            
            # Ignora se faltar algum campo ou se for o mesmo usuário
            if not autor_pr or not revisor:
                continue
            if autor_pr == revisor:
                # O grafo 3 considera apenas revisões por outro usuário
                continue
            
            # Considera todas as revisões (APPROVED, CHANGES_REQUESTED, COMMENTED)
            if autor_pr in self.usuarios and revisor in self.usuarios:
                origem = self.usuarios[revisor]    # quem revisa
                destino = self.usuarios[autor_pr]  # quem criou o PR
                
                self.grafo.addEdge(origem, destino)
                arestas_adicionadas += 1
        
        print(f"Total de arestas adicionadas (revisões de PRs): {arestas_adicionadas}")
    
    def _adicionar_arestas_merges(self):
        """
        Adiciona arestas baseadas nos merges de pull requests.
        
        Regra:
        - Se um PR foi criado por 'autor' e teve merge feito por 'merged_by'
          e autor != merged_by, então adicionamos uma aresta:
            merged_by → autor
        """
        if not self.dados.get("pulls"):
            print("Nenhum pull request encontrado para o Grafo 3!")
            return
        
        arestas_adicionadas = 0
        
        for pull in self.dados["pulls"]:
            # Campos esperados em cada pull request:
            autor = pull.get("autor")
            merged_by = pull.get("merged_by")
            
            # Ignora se faltar algum campo, se for o mesmo usuário, ou se não foi feito merge
            if not autor or not merged_by:
                continue
            if autor == merged_by:
                # O grafo 3 considera apenas merges por outro usuário
                continue
            
            if autor in self.usuarios and merged_by in self.usuarios:
                origem = self.usuarios[merged_by]  # quem fez o merge
                destino = self.usuarios[autor]     # quem criou o PR
                
                self.grafo.addEdge(origem, destino)
                arestas_adicionadas += 1
        
        print(f"Total de arestas adicionadas (merges de PRs): {arestas_adicionadas}")
    
    def get_usuario_por_indice(self, indice: int) -> str:
        """
        Retorna o nome do usuário pelo índice do vértice.
        
        Args:
            indice: Índice do vértice
            
        Returns:
            Nome do usuário
        """
        return self.usuarios_reverso.get(indice, f"Usuario_{indice}")
    
    def get_indice_por_usuario(self, usuario: str) -> int:
        """
        Retorna o índice do vértice pelo nome do usuário.
        
        Args:
            usuario: Nome do usuário
            
        Returns:
            Índice do vértice (-1 se não encontrado)
        """
        return self.usuarios.get(usuario, -1)
    
    def get_grafo(self):
        """
        Retorna a instância do grafo.
        
        Returns:
            Instância de AdjacencyMatrixGraph
        """
        return self.grafo
    
    def imprimir_estatisticas(self):
        """
        Imprime estatísticas do grafo de revisões/merges de pull requests.
        """
        if not self.grafo:
            print("Grafo 3 (Matriz) não foi construído!")
            return
        
        print("=" * 60)
        print("ESTATÍSTICAS DO GRAFO 3 - REVISÕES/MERGES DE PRS (MATRIZ)")
        print("=" * 60)
        print(f"Número de usuários (vértices): {self.grafo.getVertexCount()}")
        print(f"Número de interações (arestas): {self.grafo.getEdgeCount()}")
        print(f"Grafo é conexo: {self.grafo.isConnected()}")
        print(f"Grafo é vazio: {self.grafo.isEmptyGraph()}")
        print(f"Grafo é completo: {self.grafo.isCompleteGraph()}")
        
        # Estatísticas de grau
        if self.grafo.getVertexCount() > 0:
            graus_entrada = []
            graus_saida = []
            
            for i in range(self.grafo.getVertexCount()):
                grau_entrada = self.grafo.getVertexInDegree(i)
                grau_saida = self.grafo.getVertexOutDegree(i)
                graus_entrada.append(grau_entrada)
                graus_saida.append(grau_saida)
            
            max_grau_entrada = max(graus_entrada)
            min_grau_entrada = min(graus_entrada)
            soma_grau_entrada = sum(graus_entrada)
            media_grau_entrada = soma_grau_entrada / len(graus_entrada)
            
            max_grau_saida = max(graus_saida)
            min_grau_saida = min(graus_saida)
            soma_grau_saida = sum(graus_saida)
            media_grau_saida = soma_grau_saida / len(graus_saida)
            
            print(f"\nGrau de entrada - Mín: {min_grau_entrada}, Máx: {max_grau_entrada}, Média: {media_grau_entrada:.2f}")
            print(f"Grau de saída  - Mín: {min_grau_saida}, Máx: {max_grau_saida}, Média: {media_grau_saida:.2f}")
            
            # Top usuários que mais REVISAM/FAZEM MERGE (grau de saída)
            print(f"\nTop 5 usuários que mais revisam/fazem merge (grau de saída):")
            usuarios_atividade = []
            for i in range(self.grafo.getVertexCount()):
                usuario = self.get_usuario_por_indice(i)
                atividade = self.grafo.getVertexOutDegree(i)
                usuarios_atividade.append((atividade, usuario))
            
            # Ordenação manual decrescente
            for i in range(len(usuarios_atividade)):
                for j in range(i + 1, len(usuarios_atividade)):
                    if usuarios_atividade[i][0] < usuarios_atividade[j][0]:
                        usuarios_atividade[i], usuarios_atividade[j] = usuarios_atividade[j], usuarios_atividade[i]
            
            for i in range(min(5, len(usuarios_atividade))):
                atividade, usuario = usuarios_atividade[i]
                if atividade > 0:
                    print(f"  {i+1}. {usuario}: {atividade} revisões/merges")
        
        print("=" * 60)
    
    def imprimir_amostra_arestas(self, limite: int = 10):
        """
        Imprime uma amostra das arestas do grafo.
        
        Args:
            limite: Número máximo de arestas a exibir
        """
        if not self.grafo:
            print("Grafo 3 (Matriz) não foi construído!")
            return
        
        print(f"\nAmostra das primeiras {limite} arestas (revisões/merges):")
        print("-" * 40)
        
        count = 0
        for i in range(self.grafo.getVertexCount()):
            if count >= limite:
                break
            
            # Para matriz, precisamos verificar cada possível sucessor
            sucessores = [j for j in range(self.grafo.getVertexCount()) if j != i and self.grafo.hasEdge(i, j)]
            for j in sucessores:
                if count >= limite:
                    break
                
                usuario_origem = self.get_usuario_por_indice(i)  # quem revisa/faz merge
                usuario_destino = self.get_usuario_por_indice(j) # quem criou o PR
                
                print(f"{usuario_origem} → {usuario_destino}")
                count += 1
        
        if count == 0:
            print("Nenhuma aresta encontrada.")
    
    def exportToGEPHI(self, path: str) -> None:
        """
        Exporta o grafo de revisões/merges para formato GEXF com rótulos de usuários.
        
        Args:
            path: Caminho do arquivo a ser criado
        """
        if not self.grafo:
            print("Grafo 3 (Matriz) não foi construído!")
            return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # Cabeçalho GEXF
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
                f.write('  <meta lastmodifieddate="2024-01-01">\n')
                f.write('    <creator>TrabalhoGrafos - PullRequestReviewGraphMatrixAd</creator>\n')
                f.write('    <description>Grafo de revisões/merges de PRs GitHub (Matriz) para visualização no GEPHI</description>\n')
                f.write('  </meta>\n')
                
                # Tipo de grafo (direcionado)
                f.write('  <graph mode="static" defaultedgetype="directed">\n')
                
                # Atributos dos nós
                f.write('    <attributes class="node">\n')
                f.write('      <attribute id="0" title="grau_entrada" type="integer"/>\n')
                f.write('      <attribute id="1" title="grau_saida" type="integer"/>\n')
                f.write('    </attributes>\n')
                
                # Nós (usuários)
                f.write('    <nodes>\n')
                for i in range(self.grafo.getVertexCount()):
                    usuario = self.get_usuario_por_indice(i)
                    grau_entrada = self.grafo.getVertexInDegree(i)
                    grau_saida = self.grafo.getVertexOutDegree(i)
                    
                    # Escapa caracteres especiais XML
                    usuario_escaped = (
                        usuario.replace('&', '&amp;')
                               .replace('<', '&lt;')
                               .replace('>', '&gt;')
                               .replace('"', '&quot;')
                    )
                    
                    f.write(f'      <node id="{i}" label="{usuario_escaped}">\n')
                    f.write('        <attvalues>\n')
                    f.write(f'          <attvalue for="0" value="{grau_entrada}"/>\n')
                    f.write(f'          <attvalue for="1" value="{grau_saida}"/>\n')
                    f.write('        </attvalues>\n')
                    f.write('      </node>\n')
                f.write('    </nodes>\n')
                
                # Arestas (revisões/merges)
                f.write('    <edges>\n')
                edge_id = 0
                for u in range(self.grafo.getVertexCount()):
                    sucessores = self.grafo.getSuccessors(u)
                    for v in sucessores:
                        f.write(f'      <edge id="{edge_id}" source="{u}" target="{v}" />\n')
                        edge_id += 1
                f.write('    </edges>\n')
                
                f.write('  </graph>\n')
                f.write('</gexf>\n')
            
            print(f"Grafo 3 (Matriz) exportado com sucesso para: {path}")
            print(f"Total de usuários: {self.grafo.getVertexCount()}")
            print(f"Total de interações (revisões/merges): {self.grafo.getEdgeCount()}")
            print("Para visualizar:")
            print("1. Abra o GEPHI")
            print("2. File > Open > Selecione o arquivo")
            print("3. Layout > Force Atlas 2 (recomendado)")
            print("4. Aparência > Nós > Tamanho > grau_saida (para destacar quem mais revisa/faz merge)")
            
        except Exception as e:
            print(f"Erro ao exportar grafo 3 (Matriz): {e}")
            raise


def main():
    """
    Função principal para testar o grafo de revisões/merges (Grafo 3 - Matriz).
    """
    print("Criando grafo de revisões/merges de pull requests (Grafo 3 - Matriz)...")
    
    try:
        # Cria o grafo de revisões/merges usando matriz
        pr_review_graph = PullRequestReviewGraphMatrixAd()
        
        # Imprime estatísticas
        pr_review_graph.imprimir_estatisticas()
        
        # Imprime amostra das arestas
        pr_review_graph.imprimir_amostra_arestas(15)
        
        # Exporta para GEPHI
        print("\n" + "=" * 50)
        print("Exportando grafo 3 (Matriz) para visualização no GEPHI...")
        pr_review_graph.exportToGEPHI("grafo_reviews_merges_prs_matrix.gexf")
        
    except Exception as e:
        print(f"Erro ao criar grafo de revisões/merges (Grafo 3 - Matriz): {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
