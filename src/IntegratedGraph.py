from AdjacencyListGraph import AdjacencyListGraph
from AdjacencyMatrixGraph import AdjacencyMatrixGraph
from dados import carregar_dados_coletados

class IntegratedGraph:
    """
    Classe para modelar o Grafo Integrado: combinação ponderada de todas as interações.
    
    Cada usuário é representado como um nó.
    As arestas representam uma combinação ponderada de todas as interações.
    
    Pesos das interações:
    • Comentário em issue ou pull request: peso 2
    • Abertura de issue comentada por outro usuário: peso 3  
    • Revisão/aprovação de pull request: peso 4
    • Merge de pull request: peso 5
    
    Se um usuário fez múltiplas interações com outro, os pesos são somados.
    O grafo é simples e direcionado com pesos nas arestas.
    """
    
    def __init__(self, usar_matriz=False):
        """
        Construtor do grafo integrado.
        Carrega os dados coletados e constrói o grafo.
        
        Args:
            usar_matriz: Se True, usa AdjacencyMatrixGraph; se False, usa AdjacencyListGraph
        """
        self.usar_matriz = usar_matriz
        self.dados = carregar_dados_coletados()
        self.usuarios = {}          # Mapear usuário -> índice do vértice
        self.usuarios_reverso = {}  # Mapear índice -> usuário
        self.pesos_arestas = {}     # Mapear (origem, destino) -> peso total
        self.grafo = None
        
        self._construir_grafo()
    
    def _extrair_usuarios(self):
        """
        Extrai todos os usuários únicos de todos os tipos de dados.
        """
        usuarios_set = []
        
        # Extrai usuários das issues
        if self.dados.get("issues"):
            for issue in self.dados["issues"]:
                autor = issue.get("autor")
                fechado_por = issue.get("fechado_por")
                
                if autor and autor not in usuarios_set:
                    usuarios_set.append(autor)
                if fechado_por and fechado_por not in usuarios_set:
                    usuarios_set.append(fechado_por)
        
        # Extrai usuários dos pull requests
        if self.dados.get("pulls"):
            for pull in self.dados["pulls"]:
                autor = pull.get("autor")
                merged_by = pull.get("merged_by")
                
                if autor and autor not in usuarios_set:
                    usuarios_set.append(autor)
                if merged_by and merged_by not in usuarios_set:
                    usuarios_set.append(merged_by)
        
        # Extrai usuários das interações
        if self.dados.get("interacoes"):
            # Comentários em issues
            for comentario in self.dados["interacoes"].get("comentarios_issues", []):
                autor_issue = comentario.get("autor_issue")
                autor_comentario = comentario.get("autor_comentario")
                
                if autor_issue and autor_issue not in usuarios_set:
                    usuarios_set.append(autor_issue)
                if autor_comentario and autor_comentario not in usuarios_set:
                    usuarios_set.append(autor_comentario)
            
            # Comentários em pull requests
            for comentario in self.dados["interacoes"].get("comentarios_pulls", []):
                autor_pr = comentario.get("autor_pr")
                autor_comentario = comentario.get("autor_comentario")
                
                if autor_pr and autor_pr not in usuarios_set:
                    usuarios_set.append(autor_pr)
                if autor_comentario and autor_comentario not in usuarios_set:
                    usuarios_set.append(autor_comentario)
            
            # Revisões de pull requests
            for review in self.dados["interacoes"].get("reviews_pulls", []):
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
        
        print(f"Total de usuários únicos encontrados (Grafo Integrado): {len(usuarios_set)}")
        return len(usuarios_set)
    
    def _construir_grafo(self):
        """
        Constrói o grafo integrado baseado em todos os dados coletados.
        """
        print("Construindo grafo integrado com pesos...")
        
        # Extrai usuários únicos
        num_usuarios = self._extrair_usuarios()
        
        if num_usuarios == 0:
            print("Nenhum usuário encontrado nos dados para o Grafo Integrado!")
            return
        
        # Inicializa matriz de pesos
        self.pesos_arestas = {}
        
        # Adiciona interações com seus respectivos pesos
        self._adicionar_comentarios_issues()      # peso 3 (abertura comentada)
        self._adicionar_comentarios_pulls()       # peso 2 (comentário)
        self._adicionar_reviews_pulls()           # peso 4 (revisão)
        self._adicionar_merges_pulls()            # peso 5 (merge)
        
        # Cria o grafo com o número de usuários
        if self.usar_matriz:
            self.grafo = AdjacencyMatrixGraph(num_usuarios)
            print(f"🔢 Usando Matriz de Adjacência com {num_usuarios} usuários")
        else:
            self.grafo = AdjacencyListGraph(num_usuarios)
            print(f"📋 Usando Lista de Adjacência com {num_usuarios} usuários")
        
        # Adiciona todas as arestas com base nos pesos calculados
        self._adicionar_arestas_ponderadas()
        
        print(f"✅ Grafo Integrado construído com {self.grafo.getVertexCount()} vértices e {self.grafo.getEdgeCount()} arestas")
    
    def _adicionar_peso(self, origem_usuario, destino_usuario, peso):
        """
        Adiciona peso à aresta entre dois usuários.
        
        Args:
            origem_usuario: Nome do usuário origem
            destino_usuario: Nome do usuário destino  
            peso: Peso a ser adicionado
        """
        if origem_usuario == destino_usuario:
            return  # Não adiciona self-loops
        
        if origem_usuario in self.usuarios and destino_usuario in self.usuarios:
            origem_idx = self.usuarios[origem_usuario]
            destino_idx = self.usuarios[destino_usuario]
            
            chave = (origem_idx, destino_idx)
            if chave in self.pesos_arestas:
                self.pesos_arestas[chave] += peso
            else:
                self.pesos_arestas[chave] = peso
    
    def _adicionar_comentarios_issues(self):
        """
        Adiciona pesos baseados em comentários em issues.
        Peso 3: Abertura de issue comentada por outro usuário.
        """
        if not self.dados.get("interacoes") or not self.dados["interacoes"].get("comentarios_issues"):
            print("Nenhum comentário em issues encontrado!")
            return
        
        interacoes_adicionadas = 0
        
        for comentario in self.dados["interacoes"]["comentarios_issues"]:
            autor_issue = comentario.get("autor_issue")
            autor_comentario = comentario.get("autor_comentario")
            
            if autor_issue and autor_comentario and autor_issue != autor_comentario:
                # Comentarista → Autor da issue (peso 3)
                self._adicionar_peso(autor_comentario, autor_issue, 3)
                interacoes_adicionadas += 1
        
        print(f"Interações de comentários em issues processadas: {interacoes_adicionadas} (peso 3 cada)")
    
    def _adicionar_comentarios_pulls(self):
        """
        Adiciona pesos baseados em comentários em pull requests.
        Peso 2: Comentário em pull request.
        """
        if not self.dados.get("interacoes") or not self.dados["interacoes"].get("comentarios_pulls"):
            print("Nenhum comentário em PRs encontrado!")
            return
        
        interacoes_adicionadas = 0
        
        for comentario in self.dados["interacoes"]["comentarios_pulls"]:
            autor_pr = comentario.get("autor_pr")
            autor_comentario = comentario.get("autor_comentario")
            
            if autor_pr and autor_comentario and autor_pr != autor_comentario:
                # Comentarista → Autor do PR (peso 2)
                self._adicionar_peso(autor_comentario, autor_pr, 2)
                interacoes_adicionadas += 1
        
        print(f"Interações de comentários em PRs processadas: {interacoes_adicionadas} (peso 2 cada)")
    
    def _adicionar_reviews_pulls(self):
        """
        Adiciona pesos baseados em revisões de pull requests.
        Peso 4: Revisão/aprovação de pull request.
        """
        if not self.dados.get("interacoes") or not self.dados["interacoes"].get("reviews_pulls"):
            print("Nenhuma revisão de PR encontrada!")
            return
        
        interacoes_adicionadas = 0
        
        for review in self.dados["interacoes"]["reviews_pulls"]:
            autor_pr = review.get("autor_pr")
            revisor = review.get("revisor")
            
            if autor_pr and revisor and autor_pr != revisor:
                # Revisor → Autor do PR (peso 4)
                self._adicionar_peso(revisor, autor_pr, 4)
                interacoes_adicionadas += 1
        
        print(f"Interações de revisões de PRs processadas: {interacoes_adicionadas} (peso 4 cada)")
    
    def _adicionar_merges_pulls(self):
        """
        Adiciona pesos baseados em merges de pull requests.
        Peso 5: Merge de pull request.
        """
        if not self.dados.get("pulls"):
            print("Nenhum pull request encontrado!")
            return
        
        interacoes_adicionadas = 0
        
        for pull in self.dados["pulls"]:
            autor = pull.get("autor")
            merged_by = pull.get("merged_by")
            
            if autor and merged_by and autor != merged_by:
                # Quem fez merge → Autor do PR (peso 5)
                self._adicionar_peso(merged_by, autor, 5)
                interacoes_adicionadas += 1
        
        print(f"Interações de merges de PRs processadas: {interacoes_adicionadas} (peso 5 cada)")
    
    def _adicionar_arestas_ponderadas(self):
        """
        Adiciona todas as arestas ponderadas ao grafo.
        """
        arestas_adicionadas = 0
        
        for (origem_idx, destino_idx), peso in self.pesos_arestas.items():
            self.grafo.addEdge(origem_idx, destino_idx)
            arestas_adicionadas += 1
        
        print(f"Total de arestas únicas adicionadas: {arestas_adicionadas}")
        
        # Estatísticas dos pesos
        if self.pesos_arestas:
            pesos = list(self.pesos_arestas.values())
            peso_min = min(pesos)
            peso_max = max(pesos)
            peso_medio = sum(pesos) / len(pesos)
            
            print(f"Estatísticas dos pesos - Mín: {peso_min}, Máx: {peso_max}, Média: {peso_medio:.2f}")
    
    def get_peso_aresta(self, origem: int, destino: int) -> int:
        """
        Retorna o peso da aresta entre dois vértices.
        
        Args:
            origem: Índice do vértice origem
            destino: Índice do vértice destino
            
        Returns:
            Peso da aresta (0 se não existir)
        """
        return self.pesos_arestas.get((origem, destino), 0)
    
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
            Instância de AdjacencyListGraph ou AdjacencyMatrixGraph
        """
        return self.grafo
    
    def imprimir_estatisticas(self):
        """
        Imprime estatísticas do grafo integrado.
        """
        if not self.grafo:
            print("Grafo Integrado não foi construído!")
            return
        
        print("=" * 60)
        print("ESTATÍSTICAS DO GRAFO INTEGRADO - TODAS AS INTERAÇÕES")
        print("=" * 60)
        print(f"Número de usuários (vértices): {self.grafo.getVertexCount()}")
        print(f"Número de conexões (arestas): {self.grafo.getEdgeCount()}")
        print(f"Grafo é conexo: {self.grafo.isConnected()}")
        print(f"Grafo é vazio: {self.grafo.isEmptyGraph()}")
        print(f"Grafo é completo: {self.grafo.isCompleteGraph()}")
        
        # Estatísticas dos pesos
        if self.pesos_arestas:
            pesos = list(self.pesos_arestas.values())
            peso_min = min(pesos)
            peso_max = max(pesos)
            peso_total = sum(pesos)
            peso_medio = peso_total / len(pesos)
            
            print(f"\nEstatísticas dos Pesos:")
            print(f"Peso mínimo: {peso_min}")
            print(f"Peso máximo: {peso_max}")
            print(f"Peso médio: {peso_medio:.2f}")
            print(f"Peso total: {peso_total}")
        
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
            
            # Top usuários mais ativos (maior grau de saída)
            print(f"\nTop 5 usuários mais ativos (maior grau de saída):")
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
                    print(f"  {i+1}. {usuario}: {atividade} conexões")
        
        print("=" * 60)
    
    def imprimir_amostra_arestas_com_pesos(self, limite: int = 10):
        """
        Imprime uma amostra das arestas do grafo com seus pesos.
        
        Args:
            limite: Número máximo de arestas a exibir
        """
        if not self.grafo:
            print("Grafo Integrado não foi construído!")
            return
        
        print(f"\nAmostra das primeiras {limite} arestas com pesos:")
        print("-" * 50)
        
        count = 0
        for (origem_idx, destino_idx), peso in self.pesos_arestas.items():
            if count >= limite:
                break
            
            usuario_origem = self.get_usuario_por_indice(origem_idx)
            usuario_destino = self.get_usuario_por_indice(destino_idx)
            
            print(f"{usuario_origem} → {usuario_destino} (peso: {peso})")
            count += 1
        
        if count == 0:
            print("Nenhuma aresta encontrada.")
    
    def exportToGEPHI(self, path: str) -> None:
        """
        Exporta o grafo integrado para formato GEXF com pesos nas arestas.
        
        Args:
            path: Caminho do arquivo a ser criado
        """
        if not self.grafo:
            print("Grafo Integrado não foi construído!")
            return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # Cabeçalho GEXF
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
                f.write('  <meta lastmodifieddate="2024-01-01">\n')
                f.write('    <creator>TrabalhoGrafos - IntegratedGraph</creator>\n')
                f.write('    <description>Grafo integrado com todas as interações GitHub (ponderado)</description>\n')
                f.write('  </meta>\n')
                
                # Tipo de grafo (direcionado)
                f.write('  <graph mode="static" defaultedgetype="directed">\n')
                
                # Atributos dos nós
                f.write('    <attributes class="node">\n')
                f.write('      <attribute id="0" title="grau_entrada" type="integer"/>\n')
                f.write('      <attribute id="1" title="grau_saida" type="integer"/>\n')
                f.write('    </attributes>\n')
                
                # Atributos das arestas
                f.write('    <attributes class="edge">\n')
                f.write('      <attribute id="0" title="peso" type="integer"/>\n')
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
                
                # Arestas (interações com peso)
                f.write('    <edges>\n')
                edge_id = 0
                for (origem_idx, destino_idx), peso in self.pesos_arestas.items():
                    f.write(f'      <edge id="{edge_id}" source="{origem_idx}" target="{destino_idx}" weight="{peso}">\n')
                    f.write('        <attvalues>\n')
                    f.write(f'          <attvalue for="0" value="{peso}"/>\n')
                    f.write('        </attvalues>\n')
                    f.write('      </edge>\n')
                    edge_id += 1
                f.write('    </edges>\n')
                
                f.write('  </graph>\n')
                f.write('</gexf>\n')
            
            print(f"Grafo Integrado exportado com sucesso para: {path}")
            print(f"Total de usuários: {self.grafo.getVertexCount()}")
            print(f"Total de conexões: {self.grafo.getEdgeCount()}")
            print("Para visualizar:")
            print("1. Abra o GEPHI")
            print("2. File > Open > Selecione o arquivo")
            print("3. Layout > Force Atlas 2 (recomendado)")
            print("4. Aparência > Arestas > Peso > peso (para visualizar intensidade)")
            print("5. Aparência > Nós > Tamanho > grau_saida (para destacar usuários ativos)")
            
        except Exception as e:
            print(f"Erro ao exportar grafo integrado: {e}")
            raise


def main():
    """
    Função principal para testar o grafo integrado.
    """
    print("Criando grafo integrado com todas as interações...")
    
    try:
        # Cria o grafo integrado
        integrated_graph = IntegratedGraph()
        
        # Imprime estatísticas
        integrated_graph.imprimir_estatisticas()
        
        # Imprime amostra das arestas com pesos
        integrated_graph.imprimir_amostra_arestas_com_pesos(15)
        
        # Exporta para GEPHI
        print("\n" + "=" * 60)
        print("Exportando grafo integrado para visualização no GEPHI...")
        integrated_graph.exportToGEPHI("grafo_integrado_ponderado.gexf")
        
    except Exception as e:
        print(f"Erro ao criar grafo integrado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
