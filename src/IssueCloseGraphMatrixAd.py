from AdjacencyMatrixGraph import AdjacencyMatrixGraph
from dados import carregar_dados_coletados


class IssueCloseGraphyMatrixAd:
    """
    Classe específica para modelar o Grafo 2: fechamento de issues por outro usuário por meio de matrix de adjacencia .
    """

    def __init__(self):
        self.dados = carregar_dados_coletados()
        self.usuarios = {}
        self.usuarios_reverso = {}
        self.grafo = None

        self.construir_grafo()

    def _extrair_usuarios(self):
        usuarios_set = []

        if self.dados.get("issues"):
            for issue in self.dados["issues"]:
                autor = issue.get("autor")
                fechado_por = issue.get("fechado_por")

                if autor and autor not in usuarios_set:
                    usuarios_set.append(autor)
                if fechado_por and fechado_por not in usuarios_set:
                    usuarios_set.append(fechado_por)

        # corrigido: enumarate -> enumerate
        for i, usuario in enumerate(usuarios_set):
            self.usuarios[usuario] = i
            self.usuarios_reverso[i] = usuario

        print(f"Total de usuários únicos no grafo 2: {len(usuarios_set)}")
        return len(usuarios_set)

    def construir_grafo(self):
        print("Construindo grafo de fechamento de issues (Grafo 2) usando matriz de adjacência...")

        num_usuarios = self._extrair_usuarios()

        if num_usuarios == 0:
            print("Nenhum usuário encontrado para construir o grafo 2.")
            return
        
        self.grafo = AdjacencyMatrixGraph(num_usuarios)

        self._adicionar_arestas_fechamento()

        # corrigido: printf -> print
        print(f"Grafo 2 construido com {self.grafo.getVertexCount()} vértices e {self.grafo.getEdgeCount()} arestas.")

    def _adicionar_arestas_fechamento(self):

        if not self.dados.get("issues"):
            print("Nenhuma issue encontrada nos dados para adicionar arestas ao grafo 2.")
            return
        
        arestas_adicionadas = 0

        for issue in self.dados["issues"]:
            autor = issue.get("autor")
            fechado_por = issue.get("fechado_por")

            if not autor or not fechado_por:
                continue
            if autor == fechado_por:
                continue

            if autor in self.usuarios and fechado_por in self.usuarios:
                origem = self.usuarios[fechado_por]
                destino = self.usuarios[autor]

                self.grafo.addEdge(origem, destino)
                arestas_adicionadas += 1

                print(f"Total de arestas adicionadas (fechamento de issues) : {arestas_adicionadas}")

    def get_usuario_por_indice(self, indice: int) -> str:
        return self.usuarios_reverso.get(indice, f"Usuario_{indice}")
    
    def get_indice_por_usuario(self, usuario: str) -> int:
        return self.usuarios.get(usuario, -1)
    
    def get_grafo(self):
        return self.grafo
        
    def imprimir_estatisticas(self):

        if not self.grafo:
            print("Grafo de fechamento de issues não foi construído.")
            return

        print("=" * 50)
        print("ESTATÍSTICAS DO GRAFO 2 - FECHAMENTO DE ISSUES")
        print("=" * 50)
        print(f"Número de usuários (vértices): {self.grafo.getVertexCount()}")
        print(f"Número de interações de fechamento (arestas): {self.grafo.getEdgeCount()}")
        print(f"O grafo é conexo: {self.grafo.isConnected()}")
        print(f"O grafo é vazio: {self.grafo.isEmptyGraph()}")
        print(f"O grafo é completo: {self.grafo.isCompleteGraph()}")

        if self.grafo.getVertexCount() > 0:
            graus_entrada = []
            graus_saida = []

            for v in range(self.grafo.getVertexCount()):
                grau_entrada = self.grafo.getVertexInDegree(v)
                grau_saida = self.grafo.getVertexOutDegree(v)

                graus_entrada.append(grau_entrada)
                graus_saida.append(grau_saida)

            max_grau_entrada = max(graus_entrada)
            min_grau_entrada = min(graus_entrada)
            media_grau_entrada = sum(graus_entrada) / len(graus_entrada)

            max_grau_saida = max(graus_saida)
            min_grau_saida = min(graus_saida)
            media_grau_saida = sum(graus_saida) / len(graus_saida)

            print(f"Grau de entrada - Máximo: {max_grau_entrada}, Mínimo: {min_grau_entrada}, Média: {media_grau_entrada:.2f}")
            print(f"Grau de saída   - Máximo: {max_grau_saida}, Mínimo: {min_grau_saida}, Média: {media_grau_saida:.2f}")

            usuarios_fechamentos = []
            for i in range(self.grafo.getVertexCount()):
                usuario = self.get_usuario_por_indice(i)
                fechamentos = self.grafo.getVertexOutDegree(i)
                usuarios_fechamentos.append((fechamentos, usuario))
            
            # ordenação manual
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

        if not self.grafo:
            print("Grafo 2 não foi construído!")
            return
        
        print(f"\nAmostra das primeiras {limite} arestas (fechamentos):")
        print("-" * 40)
        
        count = 0
        for i in range(self.grafo.getVertexCount()):
            if count >= limite:
                break
            
            sucessores = [j for j in range(self.grafo.getVertexCount()) if j != i and self.grafo.hasEdge(i, j)]
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

        if not self.grafo:
            print("Grafo 2 não foi construído!")
            return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
                f.write('  <meta lastmodifieddate="2024-01-01">\n')
                f.write('    <creator>TrabalhoGrafos - IssueCloseGraph</creator>\n')
                f.write('    <description>Grafo de fechamento de issues GitHub para visualização no GEPHI</description>\n')
                f.write('  </meta>\n')
                
                f.write('  <graph mode="static" defaultedgetype="directed">\n')
                
                f.write('    <attributes class="node">\n')
                f.write('      <attribute id="0" title="grau_entrada" type="integer"/>\n')
                f.write('      <attribute id="1" title="grau_saida" type="integer"/>\n')
                f.write('    </attributes>\n')
                
                f.write('    <nodes>\n')
                for i in range(self.grafo.getVertexCount()):
                    usuario = self.get_usuario_por_indice(i)
                    grau_entrada = self.grafo.getVertexInDegree(i)
                    grau_saida = self.grafo.getVertexOutDegree(i)

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
                
                f.write('    <edges>\n')
                edge_id = 0
                for u in range(self.grafo.getVertexCount()):
                    sucessores = [v for v in range(self.grafo.getVertexCount()) if v != u and self.grafo.hasEdge(u, v)]
                    for v in sucessores:
                        f.write(f'      <edge id="{edge_id}" source="{u}" target="{v}" />\n')
                        edge_id += 1
                f.write('    </edges>\n')
                
                f.write('  </graph>\n')
                f.write('</gexf>\n')
            
            print(f"Grafo 2 exportado com sucesso para: {path}")
        
        except Exception as e:
            print(f"Erro ao exportar grafo 2: {e}")
            raise


def main():
    print("Criando grafo de fechamento de issues (Grafo 2)...")
    
    try:
        issue_close_graph_matrix_ad = IssueCloseGraphyMatrixAd()
        
        issue_close_graph_matrix_ad.imprimir_estatisticas()
        issue_close_graph_matrix_ad.imprimir_amostra_arestas(15)
        
        print("\n" + "=" * 50)
        print("Exportando grafo 2 para visualização no GEPHI...")
        issue_close_graph_matrix_ad.exportToGEPHI("grafo_fechamento_issues_matrix_ad.gexf")
        
    except Exception as e:
        print(f"Erro ao criar grafo de fechamento de issues (Grafo 2): {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
