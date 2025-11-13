from AdjacencyListGraph import AdjacencyListGraph
from dados import carregar_dados_coletados

class CommentGraph:
    """
    Classe específica para modelar o Grafo 1: comentários em issues ou pull requests.
    
    Cada usuário é representado como um nó.
    As interações entre usuários são representadas como arestas direcionadas.
    O grafo é simples e direcionado.
    """
    
    def __init__(self):
        """
        Construtor do grafo de comentários.
        Carrega os dados coletados e constrói o grafo.
        """
        self.dados = carregar_dados_coletados()
        self.usuarios = {}  # Mapear usuário -> índice do vértice
        self.usuarios_reverso = {}  # Mapear índice -> usuário
        self.grafo = None
        
        self._construir_grafo()
    
    def _extrair_usuarios(self):
        """
        Extrai todos os usuários únicos dos dados coletados.
        """
        usuarios_set = []
        
        # Extrai usuários das issues
        if self.dados["issues"]:
            for issue in self.dados["issues"]:
                autor = issue.get("autor")
                fechado_por = issue.get("fechado_por")
                
                if autor and autor not in usuarios_set:
                    usuarios_set.append(autor)
                if fechado_por and fechado_por not in usuarios_set:
                    usuarios_set.append(fechado_por)
        
        # Extrai usuários dos pull requests
        if self.dados["pulls"]:
            for pull in self.dados["pulls"]:
                autor = pull.get("autor")
                merged_by = pull.get("merged_by")
                
                if autor and autor not in usuarios_set:
                    usuarios_set.append(autor)
                if merged_by and merged_by not in usuarios_set:
                    usuarios_set.append(merged_by)
        
        # Extrai usuários das interações
        if self.dados["interacoes"]:
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
        
        # Cria mapeamento usuário -> índice
        for i, usuario in enumerate(usuarios_set):
            self.usuarios[usuario] = i
            self.usuarios_reverso[i] = usuario
        
        print(f"Total de usuários únicos encontrados: {len(usuarios_set)}")
        return len(usuarios_set)
    
    def _construir_grafo(self):
        """
        Constrói o grafo de comentários baseado nos dados coletados.
        """
        print("Construindo grafo de comentários...")
        
        # Extrai usuários únicos
        num_usuarios = self._extrair_usuarios()
        
        if num_usuarios == 0:
            print("Nenhum usuário encontrado nos dados!")
            return
        
        # Cria o grafo com o número de usuários
        self.grafo = AdjacencyListGraph(num_usuarios)
        
        # Adiciona arestas baseadas nos comentários
        self._adicionar_arestas_comentarios()
        
        print(f"Grafo construído com {self.grafo.getVertexCount()} vértices e {self.grafo.getEdgeCount()} arestas")
    
    def _adicionar_arestas_comentarios(self):
        """
        Adiciona arestas baseadas nos comentários em issues e pull requests.
        """
        if not self.dados["interacoes"]:
            print("Nenhuma interação encontrada!")
            return
        
        arestas_adicionadas = 0
        
        # Processa comentários em issues
        for comentario in self.dados["interacoes"].get("comentarios_issues", []):
            autor_issue = comentario.get("autor_issue")
            autor_comentario = comentario.get("autor_comentario")
            
            if autor_issue and autor_comentario and autor_issue != autor_comentario:
                if autor_issue in self.usuarios and autor_comentario in self.usuarios:
                    # Aresta do comentarista para o autor da issue
                    origem = self.usuarios[autor_comentario]
                    destino = self.usuarios[autor_issue]
                    
                    self.grafo.addEdge(origem, destino)
                    arestas_adicionadas += 1
        
        # Processa comentários em pull requests
        for comentario in self.dados["interacoes"].get("comentarios_pulls", []):
            autor_pr = comentario.get("autor_pr")
            autor_comentario = comentario.get("autor_comentario")
            
            if autor_pr and autor_comentario and autor_pr != autor_comentario:
                if autor_pr in self.usuarios and autor_comentario in self.usuarios:
                    # Aresta do comentarista para o autor do PR
                    origem = self.usuarios[autor_comentario]
                    destino = self.usuarios[autor_pr]
                    
                    self.grafo.addEdge(origem, destino)
                    arestas_adicionadas += 1
        
        print(f"Total de arestas adicionadas: {arestas_adicionadas}")
    
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
            Instância de AdjacencyListGraph
        """
        return self.grafo
    
    def imprimir_estatisticas(self):
        """
        Imprime estatísticas do grafo de comentários.
        """
        if not self.grafo:
            print("Grafo não foi construído!")
            return
        
        print("=" * 50)
        print("ESTATÍSTICAS DO GRAFO DE COMENTÁRIOS")
        print("=" * 50)
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
            
            # Calcula estatísticas manualmente (sem usar bibliotecas)
            max_grau_entrada = max(graus_entrada)
            min_grau_entrada = min(graus_entrada)
            soma_grau_entrada = sum(graus_entrada)
            media_grau_entrada = soma_grau_entrada / len(graus_entrada)
            
            max_grau_saida = max(graus_saida)
            min_grau_saida = min(graus_saida)
            soma_grau_saida = sum(graus_saida)
            media_grau_saida = soma_grau_saida / len(graus_saida)
            
            print(f"\nGrau de entrada - Mín: {min_grau_entrada}, Máx: {max_grau_entrada}, Média: {media_grau_entrada:.2f}")
            print(f"Grau de saída - Mín: {min_grau_saida}, Máx: {max_grau_saida}, Média: {media_grau_saida:.2f}")
            
            # Top usuários mais ativos (maior grau de saída)
            print(f"\nTop 5 usuários mais ativos (que mais comentam):")
            usuarios_atividade = []
            for i in range(self.grafo.getVertexCount()):
                usuario = self.get_usuario_por_indice(i)
                atividade = self.grafo.getVertexOutDegree(i)
                usuarios_atividade.append((atividade, usuario))
            
            # Ordena por atividade (grau de saída) - ordenação manual
            for i in range(len(usuarios_atividade)):
                for j in range(i + 1, len(usuarios_atividade)):
                    if usuarios_atividade[i][0] < usuarios_atividade[j][0]:
                        usuarios_atividade[i], usuarios_atividade[j] = usuarios_atividade[j], usuarios_atividade[i]
            
            for i in range(min(5, len(usuarios_atividade))):
                atividade, usuario = usuarios_atividade[i]
                if atividade > 0:
                    print(f"  {i+1}. {usuario}: {atividade} comentários")
        
        print("=" * 50)
    
    def imprimir_amostra_arestas(self, limite: int = 10):
        """
        Imprime uma amostra das arestas do grafo.
        
        Args:
            limite: Número máximo de arestas a exibir
        """
        if not self.grafo:
            print("Grafo não foi construído!")
            return
        
        print(f"\nAmostra das primeiras {limite} arestas:")
        print("-" * 40)
        
        count = 0
        for i in range(self.grafo.getVertexCount()):
            if count >= limite:
                break
            
            sucessores = self.grafo.getSuccessors(i)
            for j in sucessores:
                if count >= limite:
                    break
                
                usuario_origem = self.get_usuario_por_indice(i)
                usuario_destino = self.get_usuario_por_indice(j)
                
                print(f"{usuario_origem} → {usuario_destino}")
                count += 1
        
        if count == 0:
            print("Nenhuma aresta encontrada.")
    
    def exportToGEPHI(self, path: str) -> None:
        """
        Exporta o grafo de comentários para formato GEXF com rótulos de usuários.
        
        Args:
            path: Caminho do arquivo a ser criado
        """
        if not self.grafo:
            print("Grafo não foi construído!")
            return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # Cabeçalho GEXF
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
                f.write('  <meta lastmodifieddate="2024-01-01">\n')
                f.write('    <creator>TrabalhoGrafos - CommentGraph</creator>\n')
                f.write('    <description>Grafo de comentários GitHub para visualização no GEPHI</description>\n')
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
                    usuario_escaped = usuario.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                    
                    f.write(f'      <node id="{i}" label="{usuario_escaped}">\n')
                    f.write(f'        <attvalues>\n')
                    f.write(f'          <attvalue for="0" value="{grau_entrada}"/>\n')
                    f.write(f'          <attvalue for="1" value="{grau_saida}"/>\n')
                    f.write(f'        </attvalues>\n')
                    f.write(f'      </node>\n')
                f.write('    </nodes>\n')
                
                # Arestas (comentários)
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
            
            print(f"Grafo de comentários exportado com sucesso para: {path}")
            print(f"Total de usuários: {self.grafo.getVertexCount()}")
            print(f"Total de interações: {self.grafo.getEdgeCount()}")
            print("Para visualizar:")
            print("1. Abra o GEPHI")
            print("2. File > Open > Selecione o arquivo")
            print("3. Layout > Force Atlas 2 (recomendado)")
            print("4. Aparência > Nós > Tamanho > grau_saida (para destacar usuários mais ativos)")
            
        except Exception as e:
            print(f"Erro ao exportar grafo: {e}")
            raise

def main():
    """
    Função principal para testar o grafo de comentários.
    """
    print("Criando grafo de comentários...")
    
    try:
        # Cria o grafo de comentários
        comment_graph = CommentGraph()
        
        # Imprime estatísticas
        comment_graph.imprimir_estatisticas()
        
        # Imprime amostra das arestas
        comment_graph.imprimir_amostra_arestas(15)
        
        # Exporta para GEPHI
        print("\n" + "=" * 50)
        print("Exportando grafo para visualização no GEPHI...")
        comment_graph.exportToGEPHI("grafo_comentarios.gexf")
        
    except Exception as e:
        print(f"Erro ao criar grafo de comentários: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
