#!/usr/bin/env python3
"""
Menu Interativo para Análise de Grafos GitHub
===============================================
Permite escolher o tipo de grafo e a implementação desejada
"""

import os
import sys
from CommentGraph import CommentGraph
from IssueCloseGraph import IssueCloseGraph

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_cabecalho():
    """Exibe o cabeçalho bonito do programa"""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "🔗 ANALISADOR DE GRAFOS GITHUB 🔗" + " " * 10 + "║")
    print("║" + " " * 20 + "Trabalho de Grafos" + " " * 19 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

def exibir_menu_principal():
    """Exibe o menu principal de escolha do tipo de grafo"""
    print("┌─────────────────────────────────────────────────────────┐")
    print("│                   📊 TIPOS DE GRAFOS                    │")
    print("├─────────────────────────────────────────────────────────┤")
    print("│                                                         │")
    print("│  1️⃣  Grafo de Comentários                               │")
    print("│      💬 Interações via comentários em Issues/PRs       │")
    print("│                                                         │")
    print("│  2️⃣  Grafo de Fechamento de Issues                      │")
    print("│      🔒 Usuários que fecham issues de outros           │")
    print("│                                                         │")
    print("│  0️⃣  Sair do programa                                   │")
    print("│                                                         │")
    print("└─────────────────────────────────────────────────────────┘")
    print()

def exibir_menu_implementacao():
    """Exibe o menu de escolha da implementação"""
    print("┌─────────────────────────────────────────────────────────┐")
    print("│                ⚙️  IMPLEMENTAÇÃO DO GRAFO               │")
    print("├─────────────────────────────────────────────────────────┤")
    print("│                                                         │")
    print("│  1️⃣  Lista de Adjacência                               │")
    print("│      📝 Eficiente para grafos esparsos                 │")
    print("│      💾 Menor uso de memória                            │")
    print("│                                                         │")
    print("│  2️⃣  Matriz de Adjacência                              │")
    print("│      🔢 Acesso rápido às arestas                       │")
    print("│      ⚡ Eficiente para grafos densos                   │")
    print("│                                                         │")
    print("│  0️⃣  Voltar ao menu anterior                            │")
    print("│                                                         │")
    print("└─────────────────────────────────────────────────────────┘")
    print()

def exibir_menu_acoes(tipo_grafo_nome, implementacao_nome):
    """Exibe o menu de ações disponíveis após criar o grafo"""
    print("┌─────────────────────────────────────────────────────────┐")
    print(f"│                    🎯 AÇÕES DISPONÍVEIS                 │")
    print("├─────────────────────────────────────────────────────────┤")
    print(f"│ Grafo: {tipo_grafo_nome:<45} │")
    print(f"│ Implementação: {implementacao_nome:<35} │")
    print("│                                                         │")
    print("│  1️⃣  Exibir estatísticas do grafo                      │")
    print("│      📈 Vértices, arestas, graus, etc.                 │")
    print("│                                                         │")
    print("│  2️⃣  Mostrar amostra de arestas                        │")
    print("│      👀 Visualizar as 10 primeiras conexões            │")
    print("│                                                         │")
    print("│  3️⃣  Exportar para GEPHI                               │")
    print("│      💾 Gerar arquivo .gexf para visualização          │")
    print("│                                                         │")
    print("│  4️⃣  Voltar ao menu principal                          │")
    print("│                                                         │")
    print("│  0️⃣  Sair do programa                                   │")
    print("│                                                         │")
    print("└─────────────────────────────────────────────────────────┘")
    print()

def obter_escolha_usuario(opcoes_validas):
    """Solicita e valida a escolha do usuário"""
    while True:
        try:
            escolha = input("🔸 Digite sua escolha: ").strip()
            if escolha == '' or not escolha.isdigit():
                print("❌ Por favor, digite um número válido!")
                continue
            
            escolha_num = int(escolha)
            if escolha_num in opcoes_validas:
                return escolha_num
            else:
                print(f"❌ Opção inválida! Escolha entre: {', '.join(map(str, opcoes_validas))}")
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrompido pelo usuário!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Erro: {e}")

def criar_grafo(tipo_grafo, usar_matriz):
    """Cria o grafo conforme as escolhas do usuário"""
    print("\n" + "⏳ " + "─" * 50)
    print("    🔧 CONSTRUINDO O GRAFO...")
    print("─" * 52)
    
    try:
        if tipo_grafo == 1:
            print("📊 Criando Grafo de Comentários...")
            grafo = CommentGraph(usar_matriz=usar_matriz)
            tipo_nome = "Comentários em Issues/PRs"
        else:
            print("📊 Criando Grafo de Fechamento de Issues...")
            grafo = IssueCloseGraph(usar_matriz=usar_matriz)
            tipo_nome = "Fechamento de Issues"
        
        impl_nome = "Matriz de Adjacência" if usar_matriz else "Lista de Adjacência"
        
        print("✅ Grafo criado com sucesso!")
        print(f"📋 Tipo: {tipo_nome}")
        print(f"⚙️  Implementação: {impl_nome}")
        
        return grafo, tipo_nome, impl_nome
        
    except Exception as e:
        print(f"❌ Erro ao criar grafo: {e}")
        print("\n📍 Pressione ENTER para continuar...")
        input()
        return None, None, None

def mostrar_estatisticas(grafo):
    """Exibe as estatísticas do grafo"""
    print("\n" + "📈 " + "═" * 50)
    print("    ESTATÍSTICAS DO GRAFO")
    print("═" * 52)
    
    try:
        grafo.imprimir_estatisticas()
    except Exception as e:
        print(f"❌ Erro ao exibir estatísticas: {e}")
    
    print("\n📍 Pressione ENTER para continuar...")
    input()

def mostrar_amostra_arestas(grafo):
    """Exibe amostra das primeiras 10 arestas"""
    print("\n" + "👀 " + "═" * 50)
    print("    AMOSTRA DE ARESTAS (10 PRIMEIRAS)")
    print("═" * 52)
    
    try:
        grafo.imprimir_amostra_arestas(10)
    except Exception as e:
        print(f"❌ Erro ao exibir amostra: {e}")
    
    print("\n📍 Pressione ENTER para continuar...")
    input()

def exportar_para_gephi(grafo, tipo_nome, impl_nome):
    """Exporta o grafo para formato GEPHI"""
    print("\n" + "💾 " + "═" * 50)
    print("    EXPORTAÇÃO PARA GEPHI")
    print("═" * 52)
    
    # Gera nome do arquivo
    tipo_arquivo = tipo_nome.lower().replace(" ", "_").replace("/", "_")
    impl_arquivo = "matriz" if "Matriz" in impl_nome else "lista"
    nome_arquivo = f"grafo_{tipo_arquivo}_{impl_arquivo}.gexf"
    
    print(f"📂 Arquivo: {nome_arquivo}")
    
    confirmacao = input("🔸 Deseja continuar com a exportação? (s/n): ").strip().lower()
    
    if confirmacao in ['s', 'sim', 'y', 'yes']:
        try:
            print("⏳ Exportando...")
            grafo.exportToGEPHI(nome_arquivo)
            print("✅ Exportação concluída com sucesso!")
            print(f"📁 Arquivo salvo: {nome_arquivo}")
            print("\n🎨 Para visualizar no GEPHI:")
            print("   1. Abra o software GEPHI")
            print("   2. File > Open > Selecione o arquivo")
            print("   3. Aplique um layout (ex: Force Atlas 2)")
        except Exception as e:
            print(f"❌ Erro na exportação: {e}")
    else:
        print("❌ Exportação cancelada!")
    
    print("\n📍 Pressione ENTER para continuar...")
    input()

def menu_principal():
    """Função principal do menu"""
    while True:
        limpar_tela()
        exibir_cabecalho()
        exibir_menu_principal()
        
        escolha_tipo = obter_escolha_usuario([0, 1, 2])
        
        if escolha_tipo == 0:
            print("\n👋 Obrigado por usar o Analisador de Grafos!")
            print("🎓 Trabalho de Grafos - Até logo!")
            break
        
        # Menu de implementação
        while True:
            limpar_tela()
            exibir_cabecalho()
            print("🔸 Grafo selecionado:", "Comentários" if escolha_tipo == 1 else "Fechamento de Issues")
            print()
            exibir_menu_implementacao()
            
            escolha_impl = obter_escolha_usuario([0, 1, 2])
            
            if escolha_impl == 0:
                break  # Volta ao menu principal
            
            usar_matriz = (escolha_impl == 2)
            
            # Criar o grafo
            grafo, tipo_nome, impl_nome = criar_grafo(escolha_tipo, usar_matriz)
            
            if grafo is None:
                continue  # Volta ao menu de implementação
            
            # Menu de ações
            while True:
                limpar_tela()
                exibir_cabecalho()
                exibir_menu_acoes(tipo_nome, impl_nome)
                
                escolha_acao = obter_escolha_usuario([0, 1, 2, 3, 4])
                
                if escolha_acao == 0:
                    print("\n👋 Obrigado por usar o Analisador de Grafos!")
                    print("🎓 Trabalho de Grafos - Até logo!")
                    return
                elif escolha_acao == 1:
                    mostrar_estatisticas(grafo)
                elif escolha_acao == 2:
                    mostrar_amostra_arestas(grafo)
                elif escolha_acao == 3:
                    exportar_para_gephi(grafo, tipo_nome, impl_nome)
                elif escolha_acao == 4:
                    break  # Volta ao menu principal
            
            break  # Sai do loop de implementação

def main():
    """Função principal do programa"""
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido! Até logo!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("📧 Por favor, reporte este erro!")

if __name__ == "__main__":
    main()
