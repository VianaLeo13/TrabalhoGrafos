from AdjacencyListGraph import AdjacencyListGraph
from AdjacencyMatrixGraph import AdjacencyMatrixGraph
from dados import carregar_dados_coletados


class PullRequestGraph:
    """
    Classe para modelar o Grafo 3: revisões/aprovações/merges de Pull Requests.

    Convenção:
    - Para cada review aprovado/changes_requested por um revisor diferente do autor,
      adiciona-se uma aresta: revisor -> autor_do_PR
    - Para cada PR que foi mergeado por outro usuário, adiciona-se uma aresta:
      merged_by -> autor_do_PR
    """

    def __init__(self, usar_matriz=False):
        self.usar_matriz = usar_matriz
        self.dados = carregar_dados_coletados()
        self.usuarios = {}
        self.usuarios_reverso = {}
        self.grafo = None

        self._construir_grafo()

    def _extrair_usuarios(self):
        usuarios_set = []

        # Extrai autores e merged_by dos pulls
        if self.dados.get("pulls"):
            for pull in self.dados["pulls"]:
                autor = pull.get("autor")
                merged_by = pull.get("merged_by")

                if autor and autor not in usuarios_set:
                    usuarios_set.append(autor)
                if merged_by and merged_by not in usuarios_set:
                    usuarios_set.append(merged_by)

        # Extrai revisores das interações de reviews
        inter = self.dados.get("interacoes") or {}
        for review in inter.get("reviews_pulls", []):
            revisor = review.get("revisor")
            autor_pr = review.get("autor_pr")
            if revisor and revisor not in usuarios_set:
                usuarios_set.append(revisor)
            if autor_pr and autor_pr not in usuarios_set:
                usuarios_set.append(autor_pr)

        # Cria mapeamento
        for i, usuario in enumerate(usuarios_set):
            self.usuarios[usuario] = i
            self.usuarios_reverso[i] = usuario

        print(f"Total de usuários únicos encontrados (Grafo 3 - PRs): {len(usuarios_set)}")
        return len(usuarios_set)

    def _construir_grafo(self):
        print("Construindo grafo de Pull Requests (Grafo 3)...")
        num_usuarios = self._extrair_usuarios()

        if num_usuarios == 0:
            print("Nenhum usuário encontrado nos dados para o Grafo 3!")
            return

        if self.usar_matriz:
            self.grafo = AdjacencyMatrixGraph(num_usuarios)
            print(f"🔢 Usando Matriz de Adjacência com {num_usuarios} usuários")
        else:
            self.grafo = AdjacencyListGraph(num_usuarios)
            print(f"📋 Usando Lista de Adjacência com {num_usuarios} usuários")

        self._adicionar_arestas_prs()

        print(f"✅ Grafo 3 construído com {self.grafo.getVertexCount()} vértices e {self.grafo.getEdgeCount()} arestas")

    def _adicionar_arestas_prs(self):
        if not self.dados.get("interacoes"):
            print("Nenhuma interação encontrada para PRs!")
            return

        inter = self.dados.get("interacoes")
        added = 0

        # Reviews (revisor -> autor_pr)
        for review in inter.get("reviews_pulls", []):
            revisor = review.get("revisor")
            autor_pr = review.get("autor_pr")
            if not revisor or not autor_pr:
                continue
            if revisor == autor_pr:
                continue

            if revisor in self.usuarios and autor_pr in self.usuarios:
                origem = self.usuarios[revisor]
                destino = self.usuarios[autor_pr]
                self.grafo.addEdge(origem, destino)
                added += 1

        # Merges (merged_by -> autor_pr)
        for merge in inter.get("merges_pulls", []):
            merged_by = merge.get("merged_by")
            autor_pr = merge.get("autor_pr")
            if not merged_by or not autor_pr:
                continue
            if merged_by == autor_pr:
                continue

            if merged_by in self.usuarios and autor_pr in self.usuarios:
                origem = self.usuarios[merged_by]
                destino = self.usuarios[autor_pr]
                self.grafo.addEdge(origem, destino)
                added += 1

        print(f"Total de arestas adicionadas (reviews + merges): {added}")

    def get_usuario_por_indice(self, indice: int) -> str:
        return self.usuarios_reverso.get(indice, f"Usuario_{indice}")

    def get_indice_por_usuario(self, usuario: str) -> int:
        return self.usuarios.get(usuario, -1)

    def get_grafo(self):
        return self.grafo

    def imprimir_estatisticas(self):
        if not self.grafo:
            print("Grafo 3 não foi construido!")
            return

        print("=" * 50)
        print("ESTATÍSTICAS DO GRAFO 3 - PULL REQUESTS (REVIEWS / MERGES)")
        print("=" * 50)
        print(f"Número de usuários (vértices): {self.grafo.getVertexCount()}")
        print(f"Número de interações (arestas): {self.grafo.getEdgeCount()}")
        print(f"Grafo é conexo: {self.grafo.isConnected()}")
        print(f"Grafo é vazio: {self.grafo.isEmptyGraph()}")
        print(f"Grafo é completo: {self.grafo.isCompleteGraph()}")

        if self.grafo.getVertexCount() > 0:
            graus_entrada = []
            graus_saida = []
            for i in range(self.grafo.getVertexCount()):
                graus_entrada.append(self.grafo.getVertexInDegree(i))
                graus_saida.append(self.grafo.getVertexOutDegree(i))

            max_grau_saida = max(graus_saida)
            # Top revisores (maior grau de saída)
            print(f"\nTop 5 revisores/mergers (maior grau de saída):")
            usuarios_atividade = []
            for i in range(self.grafo.getVertexCount()):
                usuario = self.get_usuario_por_indice(i)
                atividade = self.grafo.getVertexOutDegree(i)
                usuarios_atividade.append((atividade, usuario))

            # Ordena manualmente decrescente
            for i in range(len(usuarios_atividade)):
                for j in range(i + 1, len(usuarios_atividade)):
                    if usuarios_atividade[i][0] < usuarios_atividade[j][0]:
                        usuarios_atividade[i], usuarios_atividade[j] = usuarios_atividade[j], usuarios_atividade[i]

            for i in range(min(5, len(usuarios_atividade))):
                atividade, usuario = usuarios_atividade[i]
                if atividade > 0:
                    print(f"  {i+1}. {usuario}: {atividade} ações (reviews/merges)")

        print("=" * 50)

    def imprimir_amostra_arestas(self, limite: int = 10):
        if not self.grafo:
            print("Grafo 3 não foi construido!")
            return

        print(f"\nAmostra das primeiras {limite} arestas (reviews/merges):")
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
        if not self.grafo:
            print("Grafo 3 não foi construido!")
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
                f.write('  <meta lastmodifieddate="2024-01-01">\n')
                f.write('    <creator>TrabalhoGrafos - PullRequestGraph</creator>\n')
                f.write('    <description>Grafo de PRs (reviews e merges) para visualização no GEPHI</description>\n')
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
                    sucessores = self.grafo.getSuccessors(u)
                    for v in sucessores:
                        f.write(f'      <edge id="{edge_id}" source="{u}" target="{v}" />\n')
                        edge_id += 1
                f.write('    </edges>\n')
                f.write('  </graph>\n')
                f.write('</gexf>\n')

            print(f"Grafo 3 exportado com sucesso para: {path}")
            print(f"Total de usuários: {self.grafo.getVertexCount()}")
            print(f"Total de interações: {self.grafo.getEdgeCount()}")

        except Exception as e:
            print(f"Erro ao exportar grafo 3: {e}")
            raise


def main():
    print("Criando grafo de Pull Requests (Grafo 3)...")
    try:
        g = PullRequestGraph()
        g.imprimir_estatisticas()
        g.imprimir_amostra_arestas(15)
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()
