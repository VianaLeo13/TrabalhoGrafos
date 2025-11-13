from abc import ABC, abstractmethod

class AbstractGraph(ABC):
    """
    Classe abstrata que define a API comum para implementações de grafos.
    Define atributos compartilhados (rótulos e pesos de vértices) e métodos auxiliares.
    """
    
    def __init__(self, num_vertices: int):
        """
        Construtor base para grafos.
        
        Args:
            num_vertices: Número de vértices do grafo
            
        Raises:
            ValueError: Se num_vertices for menor ou igual a 0
        """
        if num_vertices <= 0:
            raise ValueError("Número de vértices deve ser maior que 0")
        
        self._num_vertices = num_vertices
        self._vertex_labels = {}   # Rótulos dos vértices (dict manual)
    
    def _validate_vertex(self, vertex: int) -> None:
        """
        Método auxiliar para validar índices de vértices.
        
        Args:
            vertex: Índice do vértice a ser validado
            
        Raises:
            IndexError: Se o índice do vértice for inválido
        """
        if not (0 <= vertex < self._num_vertices):
            raise IndexError(f"Índice de vértice inválido: {vertex}. Deve estar entre 0 e {self._num_vertices - 1}")
    
    def _validate_edge(self, u: int, v: int) -> None:
        """
        Método auxiliar para validar uma aresta.
        
        Args:
            u: Vértice origem
            v: Vértice destino
            
        Raises:
            IndexError: Se algum índice for inválido
            ValueError: Se for uma auto-aresta (laço)
        """
        self._validate_vertex(u)
        self._validate_vertex(v)
        
        if u == v:
            raise ValueError("Grafos simples não permitem laços (auto-arestas)")
    
    # Métodos abstratos que devem ser implementados pelas classes concretas
    
    @abstractmethod
    def getVertexCount(self) -> int:
        """Retorna o número de vértices do grafo."""
        pass
    
    @abstractmethod
    def getEdgeCount(self) -> int:
        """Retorna o número de arestas do grafo."""
        pass
    
    @abstractmethod
    def hasEdge(self, u: int, v: int) -> bool:
        """Verifica se existe uma aresta entre os vértices u e v."""
        pass
    
    @abstractmethod
    def addEdge(self, u: int, v: int) -> None:
        """Adiciona uma aresta entre os vértices u e v."""
        pass
    
    @abstractmethod
    def removeEdge(self, u: int, v: int) -> None:
        """Remove a aresta entre os vértices u e v."""
        pass
    
    @abstractmethod
    def isSucessor(self, u: int, v: int) -> bool:
        """Verifica se v é sucessor de u."""
        pass
    
    @abstractmethod
    def isPredessor(self, u: int, v: int) -> bool:
        """Verifica se v é predecessor de u."""
        pass
    
    @abstractmethod
    def getVertexInDegree(self, u: int) -> int:
        """Retorna o grau de entrada do vértice u."""
        pass
    
    @abstractmethod
    def getVertexOutDegree(self, u: int) -> int:
        """Retorna o grau de saída do vértice u."""
        pass
    
    @abstractmethod
    def isConnected(self) -> bool:
        """Verifica se o grafo é conectado."""
        pass
    
    @abstractmethod
    def isEmptyGraph(self) -> bool:
        """Verifica se o grafo é vazio (não possui arestas)."""
        pass
    
    @abstractmethod
    def isCompleteGraph(self) -> bool:
        """Verifica se o grafo é completo."""
        pass
    
    # Métodos implementados na classe base
    
    def isDivergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """
        Verifica se duas arestas são divergentes (partem do mesmo vértice).
        
        Args:
            u1, v1: Primeira aresta
            u2, v2: Segunda aresta
            
        Returns:
            True se as arestas forem divergentes, False caso contrário
        """
        self._validate_edge(u1, v1)
        self._validate_edge(u2, v2)
        
        return u1 == u2 and v1 != v2 and self.hasEdge(u1, v1) and self.hasEdge(u2, v2)
    
    def isConvergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """
        Verifica se duas arestas são convergentes (chegam ao mesmo vértice).
        
        Args:
            u1, v1: Primeira aresta
            u2, v2: Segunda aresta
            
        Returns:
            True se as arestas forem convergentes, False caso contrário
        """
        self._validate_edge(u1, v1)
        self._validate_edge(u2, v2)
        
        return v1 == v2 and u1 != u2 and self.hasEdge(u1, v1) and self.hasEdge(u2, v2)
    
    def isIncident(self, u: int, v: int, x: int) -> bool:
        """
        Verifica se a aresta (u,v) é incidente ao vértice x.
        
        Args:
            u, v: Aresta
            x: Vértice
            
        Returns:
            True se a aresta for incidente ao vértice, False caso contrário
        """
        self._validate_edge(u, v)
        self._validate_vertex(x)
        
        return self.hasEdge(u, v) and (u == x or v == x)
    
    def setVertexLabel(self, v: int, label: str) -> None:
        """
        Define o rótulo de um vértice.
        
        Args:
            v: Índice do vértice
            label: Rótulo do vértice
        """
        self._validate_vertex(v)
        self._vertex_labels[v] = label
    
    def getVertexLabel(self, v: int) -> str:
        """
        Retorna o rótulo de um vértice.
        
        Args:
            v: Índice do vértice
            
        Returns:
            Rótulo do vértice (str(v) se não definido)
        """
        self._validate_vertex(v)
        return self._vertex_labels.get(v, str(v))
    
    def exportToGEPHI(self, path: str) -> None:
        """
        Exporta o grafo para formato GEXF (aceito pelo GEPHI).
        
        Args:
            path: Caminho do arquivo a ser criado
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # Cabeçalho GEXF
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n')
                f.write('  <meta lastmodifieddate="2024-01-01">\n')
                f.write('    <creator>TrabalhoGrafos</creator>\n')
                f.write('    <description>Grafo exportado para visualização no GEPHI</description>\n')
                f.write('  </meta>\n')
                
                # Tipo de grafo (direcionado)
                f.write('  <graph mode="static" defaultedgetype="directed">\n')
                
                # Nós (vértices)
                f.write('    <nodes>\n')
                for i in range(self.getVertexCount()):
                    label = self.getVertexLabel(i)
                    f.write(f'      <node id="{i}" label="{label}" />\n')
                f.write('    </nodes>\n')
                
                # Arestas
                f.write('    <edges>\n')
                edge_id = 0
                for u in range(self.getVertexCount()):
                    for v in range(self.getVertexCount()):
                        if self.hasEdge(u, v):
                            f.write(f'      <edge id="{edge_id}" source="{u}" target="{v}" />\n')
                            edge_id += 1
                f.write('    </edges>\n')
                
                f.write('  </graph>\n')
                f.write('</gexf>\n')
            
            print(f"Grafo exportado com sucesso para: {path}")
            print(f"Total de vértices: {self.getVertexCount()}")
            print(f"Total de arestas: {self.getEdgeCount()}")
            
        except Exception as e:
            print(f"Erro ao exportar grafo: {e}")
            raise
