from AdjacencyListGraph import AdjacencyListGraph
from dados import carregar_dados_coletados

class IssueCloseGraph:
    """
    Classe específica para modelar o Grafo 2: fechamento de issues por outro usuário.
    
    Cada usuário é representado como um nó.
    As interações de fechamento são representadas como arestas direcionadas.
    
    Convenção adotada:
    - Uma aresta é criada de quem FECHA a issue para quem ABRIU a issue,
      desde que sejam usuários distintos.
      Ex.: se user_X fecha uma issue aberta por user_Y (user_X != user_Y),
           adicionamos uma aresta user_X → user_Y.
    O grafo é simples e direcionado.
    """
    
    def __init__(self):
        """
        Construtor do grafo de fechamento de issues.
        Carrega os dados coletados e constrói o grafo.
        """
        self.dados = carregar_dados_coletados()
        self.usuarios = {}          # Mapear usuário -> índice do vértice
        self.usuarios_reverso = {}  # Mapear índice -> usuário
        self.grafo = None
        
        self._construir_grafo()
    
    def _extrair_usuarios(self):
        """
        Extrai todos os usuários únicos relevantes para o grafo 2.
        
        Aqui consideramos:
        - autor de issues
        - usuário que fecha issues (fechado_por)
        """
        usuarios_set = []
        
        # Extrai usuários das issues
        if self.dados.get("issues"):
            for issue in self.dados["issues"]:
               
                # existem na estrutura de dados retornada por carregar_dados_coletados()
                autor = issue.get("autor")
                fechado_por = issue.get("fechado_por")
                
                if autor and autor not in usuarios_set:
                    usuarios_set.append(autor)
                if fechado_por and fechado_por not in usuarios_set:
                    usuarios_set.append(fechado_por)
        
        # Cria mapeamento usuário -> índice
        for i, usuario in enumerate(usuarios_set):
            self.usuarios[usuario] = i
            self.usuarios_reverso[i] = usuario
        
        print(f"Total de usuários únicos encontrados (Grafo 2): {len(usuarios_set)}")
        return len(usuarios_set)
    
    def _construir_grafo(self):
        """
        Constrói o grafo de fechamento de issues baseado nos dados coletados.
        """
        print("Construindo grafo de fechamento de issues (Grafo 2)...")
        
        # Extrai usuários únicos
        num_usuarios = self._extrair_usuarios()
        
        if num_usuarios == 0:
            print("Nenhum usuário encontrado nos dados para o Grafo 2!")
            return
        
        # Cria o grafo com o número de usuários
        self.grafo = AdjacencyListGraph(num_usuarios)
        
        # Adiciona arestas baseadas no fechamento das issues
        self._adicionar_arestas_fechamento()
        
        print(f"Grafo 2 construído com {self.grafo.getVertexCount()} vértices e {self.grafo.getEdgeCount()} arestas")
    
    def _adicionar_arestas_fechamento(self):
        """
        Adiciona arestas baseadas no fechamento de issues.
        
        Regra:
        - Se uma issue foi aberta por 'autor' e fechada por 'fechado_por'
          e autor != fechado_por, então adicionamos uma aresta:
            fechado_por → autor
        """
        if not self.dados.get("issues"):
            print("Nenhuma issue encontrada para o Grafo 2!")
            return
        
        arestas_adicionadas = 0
        
        for issue in self.dados["issues"]:
            # Campos esperados em cada issue:
            autor = issue.get("autor")
            fechado_por = issue.get("fechado_por")
            
            # Ignora se faltar algum campo ou se for o mesmo usuário
            if not autor or not fechado_por:
                continue
            if autor == fechado_por:
                # O grafo 2 considera apenas fechamento por outro usuário
                continue
            
            if autor in self.usuarios and fechado_por in self.usuarios:
                origem = self.usuarios[fechado_por]  # quem fecha
                destino = self.usuarios[autor]       # quem abriu
                
                self.grafo.addEdge(origem, destino)
                arestas_adicionadas += 1
        
        print(f"Total de arestas adicionadas (fechamento de issues): {arestas_adicionadas}")
    
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
        Imprime estatísticas do grafo de fechamento de issues.
        """
        if not self.grafo:
            print("Grafo 2 não foi construído!")
            return
        
        print("=" * 50)
        print("ESTATÍSTICAS DO GRAFO 2 - FECHAMENTO DE ISSUES")
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
            
            # Top usuários que mais FECHAM issues (grau de saída)
            print(f"\nTop 5 usuários que mais fecham issues (grau de saída):")
            usuarios_fechamentos = []
            for i in range(self.grafo.getVertexCount()):
                usuario = self.get_usuario_por_indice(i)
                fechamentos = self.grafo.getVertexOutDegree(i)
                usuarios_fechamentos.append((fechamentos, usuario))
            
            # Ordenação manual decrescente
            for i in range(len(usuarios_fechamentos)):
                for j in range(i + 1, len(usuarios_fechamentos)):
                    if usuarios_fechamentos[i][0] < usuarios_fechamentos[j][0]:
                        usuarios_fechamentos[i], usuarios_fechamentos[j] = usuarios_fechamentos[j], usuarios_fechamentos[i]
            
            for i in range(min(5, len(usuarios_fechamentos))):
                fechamentos, usuario = usuarios_fechamentos[i]
                if fechamentos > 0:
                    print(f"  {i+1}. {usuario}: {fechamentos} issues fechadas de outros usuários")
        
        print("=" * 50)
    
    def imprimir_amostra_arestas(self, limite: int = 10):
        """
        Imprime uma amostra das arestas do grafo.
        
        Args:
            limite: Número máximo de arestas a exibir
        """
        if not self.grafo:
            print("Grafo 2 não foi construído!")
            return
        
        print(f"\nAmostra das primeiras {limite} arestas (fechamentos):")
        print("-" * 40)
        
        count = 0
        for i in range(self.grafo.getVertexCount()):
            if count >= limite:
                break
            
            sucessores = self.grafo.getSuccessors(i)
            for j in sucessores:
                if count >= limite:
                    break
                
                usuario_origem = self.get_usuario_por_indice(i)  # quem fecha
                usuario_destino = self.get_usuario_por_indice(j) # quem abriu
                
                print(f"{usuario_origem} → {usuario_destino}")
                count += 1
        
        if count == 0:
            print("Nenhuma aresta encontrada.")
    
    def exportToGEPHI(self, path: str) -> None:
        """
        Exporta o grafo de fechamento de issues para formato GEXF com rótulos de usuários.
        
        Args:
            path: Caminho do arquivo a ser criado
        """
        if not self.grafo:
            print("Grafo 2 não foi construído!")
            return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # Cabeçalho GEXF
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
                f.write('  <meta lastmodifieddate="2024-01-01">\n')
                f.write('    <creator>TrabalhoGrafos - IssueCloseGraph</creator>\n')
                f.write('    <description>Grafo de fechamento de issues GitHub para visualização no GEPHI</description>\n')
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
                
                # Arestas (fechamentos)
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
            
            print(f"Grafo 2 exportado com sucesso para: {path}")
            print(f"Total de usuários: {self.grafo.getVertexCount()}")
            print(f"Total de interações (fechamentos): {self.grafo.getEdgeCount()}")
            print("Para visualizar:")
            print("1. Abra o GEPHI")
            print("2. File > Open > Selecione o arquivo")
            print("3. Layout > Force Atlas 2 (recomendado)")
            print("4. Aparência > Nós > Tamanho > grau_saida (para destacar quem mais fecha issues)")
            
        except Exception as e:
            print(f"Erro ao exportar grafo 2: {e}")
            raise


def main():
    """
    Função principal para testar o grafo de fechamento de issues (Grafo 2).
    """
    print("Criando grafo de fechamento de issues (Grafo 2)...")
    
    try:
        # Cria o grafo de fechamento de issues
        issue_close_graph = IssueCloseGraph()
        
        # Imprime estatísticas
        issue_close_graph.imprimir_estatisticas()
        
        # Imprime amostra das arestas
        issue_close_graph.imprimir_amostra_arestas(15)
        
        # Exporta para GEPHI
        print("\n" + "=" * 50)
        print("Exportando grafo 2 para visualização no GEPHI...")
        issue_close_graph.exportToGEPHI("grafo_fechamento_issues.gexf")
        
    except Exception as e:
        print(f"Erro ao criar grafo de fechamento de issues (Grafo 2): {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()