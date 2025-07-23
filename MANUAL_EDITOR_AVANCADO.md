# 🚀 Editor PDF Avançado - Manual Completo

## 📋 Visão Geral

O **Editor PDF Avançado** é uma ferramenta completa para criação e edição visual de templates de PDF com integração total ao banco de dados. Permite criar documentos dinâmicos, personalizáveis e reutilizáveis.

## ✨ Principais Funcionalidades

### 🔄 Dados Dinâmicos
- **Conectar com Cotações**: Vincule diretamente com cotações do sistema
- **Campos Inteligentes**: Use campos que se preenchem automaticamente com dados reais
- **Categorias de Dados**: Cliente, Responsável, Cotação, Itens, Empresa, Meta

### 🎨 Editor Visual
- **Drag & Drop**: Arrastar e soltar elementos livremente
- **Preview em Tempo Real**: Veja como ficará o PDF final
- **Múltiplos Elementos**: Texto, imagens, tabelas, linhas, formas, campos dinâmicos
- **Grid de Auxílio**: Alinhamento preciso com grade visual

### 📄 Gerenciamento de Páginas
- **Múltiplas Páginas**: Crie quantas páginas precisar
- **Tipos de Página**: Capa, Apresentação, Sobre Empresa, Proposta, Personalizada
- **Reordenação**: Mova páginas para cima/baixo facilmente

### 📋 Sistema de Templates
- **Salvar/Carregar**: Preserve seus designs para reutilização
- **Versionamento**: Controle de versões dos templates
- **Importar/Exportar**: Compartilhe templates entre usuários
- **Backup Automático**: Proteção contra perda de dados

## 🎯 Como Usar

### 1. Conectando com uma Cotação

1. **Selecionar Cotação**:
   - Na aba "🔄 Dados", escolha uma cotação no dropdown
   - Clique em "🔄" para atualizar a lista
   - Os dados serão carregados automaticamente

2. **Visualizar Campos**:
   - Após conectar, as listas mostrarão dados reais
   - Ex: "Nome: EMPRESA EXEMPLO LTDA"

### 2. Adicionando Elementos

#### Método 1: Botões de Elementos
1. Na aba "🎨 Elementos", clique no tipo desejado:
   - 📝 Texto
   - 🖼️ Imagem
   - 📊 Tabela
   - ➖ Linha
   - ⬜ Retângulo
   - 🏷️ Logo
   - 📄 Campo Dinâmico

#### Método 2: Duplo Clique nos Campos
1. Na aba "🔄 Dados", dê duplo clique em qualquer campo
2. Um campo dinâmico será adicionado automaticamente
3. Ex: Duplo clique em "Nome (nome)" → Adiciona campo que mostra o nome do cliente

### 3. Editando Elementos

#### Seleção
- **Clique Simples**: Seleciona elemento
- **Duplo Clique**: Edita texto diretamente
- **Clique Direito**: Menu contextual com opções

#### Movimentação
- **Arrastar**: Mova elementos livremente
- **Grid**: Use a grade para alinhamento preciso

#### Menu Contextual (Clique Direito)
- ✂️ **Recortar**: Remove e copia elemento
- 📋 **Copiar**: Copia elemento para área de transferência
- 📄 **Colar**: Cola elemento copiado (posição ligeiramente diferente)
- 🔄 **Duplicar**: Cria cópia imediata
- 🗑️ **Excluir**: Remove elemento
- ⚙️ **Propriedades**: Abre janela detalhada de edição

#### Alinhamento
- ◀️ **Esquerda**: Alinha elementos à esquerda
- ⏸️ **Centro H**: Centraliza horizontalmente
- ▶️ **Direita**: Alinha à direita
- 🔝 **Topo**: Alinha ao topo
- ⏺️ **Centro V**: Centraliza verticalmente
- 🔻 **Base**: Alinha à base

#### Camadas
- 🔼 **Frente**: Traz para frente
- 🔽 **Trás**: Envia para trás
- ⬆️ **Avançar**: Move uma camada à frente
- ⬇️ **Recuar**: Move uma camada para trás

### 4. Campos Dinâmicos

#### Categorias Disponíveis

**👤 Cliente**
- nome, nome_fantasia, cnpj, endereco, cidade, estado, telefone, email, etc.

**👨‍🔧 Responsável**
- nome_completo, email, telefone, username

**📋 Cotação**
- numero_proposta, data_criacao, valor_total, observacoes, etc.

**📦 Itens**
- item_nome, quantidade, valor_unitario, valor_total_item

**🏢 Empresa**
- nome, endereco, cnpj, telefones, email

**📊 Meta (Calculados)**
- total_itens, valor_total_calculado, data_hoje, hora_atual

#### Uso em Textos
- Use `{categoria.campo}` em textos
- Ex: "Proposta para {cliente.nome} - Valor: {cotacao.valor_total}"
- Substitui automaticamente pelos valores reais

### 5. Formatação de Texto

Na aba "🎨 Elementos":
- **Fonte**: Arial, Times, Helvetica, Courier
- **Tamanho**: 8pt a 72pt
- **Estilo**: Negrito, Itálico
- **Cor**: Seletor de cores completo

### 6. Gerenciamento de Páginas

Na aba "📄 Páginas":

#### Navegação
- **◀ ▶**: Navegar entre páginas
- **Contador**: Mostra página atual

#### Gerenciamento
- **➕ Nova Página**: Adiciona página em branco
- **📋 Duplicar**: Copia página atual
- **🗑️ Excluir**: Remove página (mínimo 1)
- **⬆️⬇️ Mover**: Reordena páginas

#### Configurações
- **Nome**: Nome personalizado da página
- **Tipo**: Capa, Apresentação, Sobre Empresa, Proposta, Personalizada

### 7. Sistema de Templates

Na aba "📋 Templates":

#### Gerenciamento
- **💾 Salvar**: Salva template atual
- **📂 Carregar**: Carrega template existente
- **📤 Exportar**: Exporta para arquivo
- **📥 Importar**: Importa de arquivo
- **🔄 Restaurar**: Volta ao template padrão

#### Versionamento
- **Versão**: Controla versão atual (ex: 1.0, 1.1)
- **📌 Nova Versão**: Cria nova versão numerada

#### Templates Salvos
- **Lista**: Mostra todos os templates salvos
- **Duplo Clique**: Carrega template selecionado

## ⌨️ Atalhos de Teclado

- **Ctrl+Z**: Desfazer (planejado)
- **Ctrl+Y**: Refazer (planejado)
- **Delete**: Excluir elemento selecionado
- **Clique Direito**: Menu contextual

## 🎨 Painel de Propriedades

### Lado Direito da Tela
- **Seleção Automática**: Atualiza conforme elemento selecionado
- **Edição Rápida**: Campos básicos para edição imediata
- **Duplo Clique**: Abre janela de propriedades detalhadas

### Janela de Propriedades Detalhadas
- **Aba Geral**: ID, tipo, configurações básicas
- **Aba Aparência**: Fonte, cor, estilo
- **Aba Posição**: X, Y, largura, altura

## 🔄 Botões de Ação

### Principais
- **🔄 Atualizar Preview**: Regenera visualização
- **📄 Gerar PDF**: Cria PDF final (em desenvolvimento)
- **💾 Salvar Rápido**: Salva template rapidamente
- **🗑️ Limpar Tudo**: Remove tudo e reinicia

## 💡 Dicas e Boas Práticas

### ✅ Recomendações

1. **Sempre Conecte uma Cotação**: Para ter dados reais nos campos dinâmicos
2. **Use o Grid**: Ajuda no alinhamento preciso dos elementos
3. **Salve Frequentemente**: Use "💾 Salvar Rápido" regularmente
4. **Teste com Dados Reais**: Conecte diferentes cotações para testar
5. **Nomeie as Páginas**: Use nomes descritivos para organização
6. **Versione Templates**: Crie versões numeradas para controle

### ⚠️ Atenções

1. **Backup de Templates**: Exporte templates importantes
2. **Teste Antes de Usar**: Sempre teste com dados reais antes da produção
3. **Resolução dos Elementos**: Use tamanhos apropriados para impressão
4. **Posicionamento**: Lembre-se das margens do papel

### 🔧 Solução de Problemas

**Elemento não seleciona**:
- Verifique se está clicando exatamente no elemento
- Tente clicar na borda do elemento

**Campo dinâmico mostra [campo.nome]**:
- Verifique se uma cotação está conectada
- Confirme se o campo existe na cotação selecionada

**Preview não atualiza**:
- Clique em "🔄 Atualizar Preview"
- Verifique se há erros no console

**Template não salva**:
- Verifique permissões da pasta `data/templates_avancados`
- Confirme se há espaço em disco

## 🚀 Funcionalidades Avançadas

### 📐 Alinhamento Automático
- Selecione múltiplos elementos (Ctrl+Clique)
- Use menu contextual para alinhamento
- Elementos se alinham baseado no primeiro selecionado

### 🎯 Snap to Grid
- Elementos "grudam" na grade automaticamente
- Facilita alinhamento preciso
- Pode ser desabilitado nas configurações

### 🔄 Campos Calculados
- `{meta.total_itens}`: Número total de itens
- `{meta.valor_total_calculado}`: Soma dos valores dos itens
- `{meta.data_hoje}`: Data atual
- `{meta.hora_atual}`: Hora atual

### 📋 Templates Hierárquicos
- Templates base para toda empresa
- Templates por usuário
- Templates por cliente
- Sistema de herança automática

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte este manual
2. Verifique os logs no console
3. Entre em contato com o suporte técnico

---

**Versão do Manual**: 1.0  
**Última Atualização**: Dezembro 2024  
**Compatível com**: Editor PDF Avançado v1.0+