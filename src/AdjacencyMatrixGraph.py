from AbstractGraph import AbstractGraph

class AdjacencyMatrixGraph(AbstractGraph):
    """
    Implementação de grafo direcionado utilizando matriz de adjacência.
    Grafo simples: não permite laços nem múltiplas arestas.
    """
    
    def __init__(self, num_vertices: int):
        """
        Construtor do grafo com matriz de adjacência.
        
        Args:
            num_vertices: Número de vértices do grafo
        """
        super().__init__(num_vertices)
        
        # Inicializa a matriz de adjacência com False (sem arestas)
        self._matrix = []
        for i in range(num_vertices):
            row = []
            for j in range(num_vertices):
                row.append(False)
            self._matrix.append(row)
        
        self._edge_count = 0
    
    def getVertexCount(self) -> int:
        """Retorna o número de vértices do grafo."""
        return self._num_vertices
    
    def getEdgeCount(self) -> int:
        """Retorna o número de arestas do grafo."""
        return self._edge_count
    
    def hasEdge(self, u: int, v: int) -> bool:
        """
        Verifica se existe uma aresta entre os vértices u e v.
        
        Args:
            u: Vértice origem
            v: Vértice destino
            
        Returns:
            True se a aresta existir, False caso contrário
        """
        self._validate_edge(u, v)
        return self._matrix[u][v]
    
    def addEdge(self, u: int, v: int) -> None:
        """
        Adiciona uma aresta entre os vértices u e v.
        Operação idempotente: não duplica arestas existentes.
        
        Args:
            u: Vértice origem
            v: Vértice destino
        """
        self._validate_edge(u, v)
        
        # Verifica se a aresta já existe (idempotência)
        if not self._matrix[u][v]:
            self._matrix[u][v] = True
            self._edge_count += 1
    
    def removeEdge(self, u: int, v: int) -> None:
        """
        Remove a aresta entre os vértices u e v.
        
        Args:
            u: Vértice origem
            v: Vértice destino
        """
        self._validate_edge(u, v)
        
        if self._matrix[u][v]:
            self._matrix[u][v] = False
            self._edge_count -= 1
    
    def isSucessor(self, u: int, v: int) -> bool:
        """
        Verifica se v é sucessor de u (existe aresta u -> v).
        
        Args:
            u: Vértice origem
            v: Vértice destino
            
        Returns:
            True se v for sucessor de u, False caso contrário
        """
        return self.hasEdge(u, v)
    
    def isPredessor(self, u: int, v: int) -> bool:
        """
        Verifica se v é predecessor de u (existe aresta v -> u).
        
        Args:
            u: Vértice de referência
            v: Possível predecessor
            
        Returns:
            True se v for predecessor de u, False caso contrário
        """
        return self.hasEdge(v, u)
    
    def getVertexInDegree(self, u: int) -> int:
        """
        Retorna o grau de entrada do vértice u.
        
        Args:
            u: Vértice
            
        Returns:
            Número de arestas que chegam ao vértice u
        """
        self._validate_vertex(u)
        
        in_degree = 0
        for i in range(self._num_vertices):
            if self._matrix[i][u]:
                in_degree += 1
        
        return in_degree
    
    def getVertexOutDegree(self, u: int) -> int:
        """
        Retorna o grau de saída do vértice u.
        
        Args:
            u: Vértice
            
        Returns:
            Número de arestas que saem do vértice u
        """
        self._validate_vertex(u)
        
        out_degree = 0
        for j in range(self._num_vertices):
            if self._matrix[u][j]:
                out_degree += 1
        
        return out_degree
    
    def isConnected(self) -> bool:
        """
        Verifica se o grafo é conectado (versão para grafo direcionado: fracamente conectado).
        Um grafo direcionado é fracamente conectado se o grafo não direcionado subjacente é conectado.
        
        Returns:
            True se o grafo for conectado, False caso contrário
        """
        if self._num_vertices <= 1:
            return True
        
        if self.isEmptyGraph():
            return False
        
        # DFS para verificar conectividade fraca
        visited = [False] * self._num_vertices
        
        # Encontra o primeiro vértice com pelo menos uma aresta
        start = -1
        for i in range(self._num_vertices):
            if self.getVertexInDegree(i) > 0 or self.getVertexOutDegree(i) > 0:
                start = i
                break
        
        if start == -1:
            return False
        
        # DFS considerando o grafo como não direcionado
        self._dfs_undirected(start, visited)
        
        # Verifica se todos os vértices com arestas foram visitados
        for i in range(self._num_vertices):
            if (self.getVertexInDegree(i) > 0 or self.getVertexOutDegree(i) > 0) and not visited[i]:
                return False
        
        return True
    
    def _dfs_undirected(self, vertex: int, visited) -> None:
        """
        DFS auxiliar para verificar conectividade tratando o grafo como não direcionado.
        
        Args:
            vertex: Vértice atual
            visited: Lista de vértices visitados
        """
        visited[vertex] = True
        
        # Verifica todas as arestas (tanto de saída quanto de entrada)
        for i in range(self._num_vertices):
            if not visited[i] and (self._matrix[vertex][i] or self._matrix[i][vertex]):
                self._dfs_undirected(i, visited)
    
    def isEmptyGraph(self) -> bool:
        """
        Verifica se o grafo é vazio (não possui arestas).
        
        Returns:
            True se o grafo não possuir arestas, False caso contrário
        """
        return self._edge_count == 0
    
    def isCompleteGraph(self) -> bool:
        """
        Verifica se o grafo é completo.
        Um grafo direcionado completo possui uma aresta para cada par ordenado de vértices distintos.
        
        Returns:
            True se o grafo for completo, False caso contrário
        """
        if self._num_vertices <= 1:
            return True
        
        # Um grafo completo direcionado com n vértices tem n*(n-1) arestas
        expected_edges = self._num_vertices * (self._num_vertices - 1)
        
        if self._edge_count != expected_edges:
            return False
        
        # Verifica se existe aresta entre todos os pares de vértices distintos
        for i in range(self._num_vertices):
            for j in range(self._num_vertices):
                if i != j and not self._matrix[i][j]:
                    return False
        
        return True
    
    def __str__(self) -> str:
        """
        Representação string da matriz de adjacência.
        
        Returns:
            String representando a matriz de adjacência
        """
        result = "Matriz de Adjacência:\n"
        result += "   " + " ".join(f"{i:2}" for i in range(self._num_vertices)) + "\n"
        
        for i in range(self._num_vertices):
            result += f"{i:2}: "
            for j in range(self._num_vertices):
                result += f"{int(self._matrix[i][j]):2} "
            result += "\n"
        
        return result
