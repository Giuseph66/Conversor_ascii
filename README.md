# Conversor ASCII para XBM com Interface Gráfica

Um conversor avançado que transforma desenhos ASCII em bytes hexadecimal compatíveis com a biblioteca u8g2 para displays OLED/EPD. O sistema inclui interface gráfica intuitiva, importação inteligente de imagens e análise pixel a pixel.

## 🎯 Visão Geral

Este projeto é uma evolução completa do conversor ASCII original (`ASCII_terminal.py`), oferecendo:

- **Interface gráfica moderna** para desenho visual
- **Sistema de importação de imagens** com análise inteligente
- **Conversão automática** para múltiplos formatos de saída
- **Suporte a grades de diferentes tamanhos** (8x8, 16x16, 32x32, etc.)
- **Ferramentas avançadas** como histórico, pincéis de diferentes tamanhos e preview em tempo real

## 🏗️ Arquitetura do Sistema

### Componentes Principais

1. **`ascii_converter_gui.py`** - Interface gráfica principal
2. **`image_importer.py`** - Sistema de importação e processamento de imagens
3. **`pixel_analyzer.py`** - Analisador pixel a pixel para conversão inteligente

### Fluxo de Funcionamento

```
Imagem → Pixel Analyzer → Conversão Inteligente → Grade ASCII → Conversão XBM → Código C
   ↓              ↓              ↓              ↓           ↓
Análise      Classificação   Mapeamento    Representação  Saída Final
Pixel a      de Pixels      para Grade    Visual         Hexadecimal
Pixel
```

## 🔧 Funcionalidades Detalhadas

### 1. Interface de Desenho

- **Grade interativa**: Desenhe clicando ou arrastando o mouse
- **Pincéis configuráveis**: Tamanhos de 1x1 até 5x5 pixels
- **Controles intuitivos**: Botão esquerdo para preto (#), direito para branco (.)
- **Histórico completo**: Sistema de desfazer (Ctrl+Z) com até 50 estados
- **Tamanhos flexíveis**: Suporte a grades de 1x1 até 200x200 pixels

### 2. Sistema de Importação de Imagens

#### Formatos Suportados
- PNG, JPEG, BMP, GIF, TIFF
- Suporte completo a transparência (RGBA)
- Conversão automática de RGB para escala de cinza

#### Processamento Inteligente
```python
# Análise pixel a pixel
def analyze_pixel_color(r, g, b, a=None):
    if a is not None and a < 128:
        return 'transparente'  # Pixel transparente
    elif r > 240 and g > 240 and b > 240:
        return 'branco'        # Pixel branco
    else:
        return 'colorido'      # Pixel com cor
```

#### Mapeamento para Grade
- **Pixels coloridos** → Preto (#) na grade
- **Pixels brancos/transparentes** → Branco (.) na grade
- **Redimensionamento inteligente** mantendo proporções
- **Preview em tempo real** da conversão

### 3. Algoritmo de Conversão XBM

#### Conversão de Linha para Byte
```python
def linha_para_byte(self, linha):
    """
    Transforma caracteres ('.' ou '#') numa máscara de bits.
    Bit 0 (LSB) = primeiro caractere da linha (ESQUERDA).
    """
    bits = 0
    max_bits = min(8, len(linha))
    
    for pos, ch in enumerate(linha[:max_bits]):
        if ch == '#':
            bits |= (1 << pos)  # Set bit na posição
    return bits
```

#### Exemplo de Conversão
```
Linha ASCII: ".#.#...."
Posições:     01234567
Bits:        01010000
Byte:        0x50 (80 decimal)
```

#### Suporte a Grades Grandes
Para grades maiores que 8 pixels de largura, o sistema divide automaticamente em bytes de 8 bits:

```python
# Grade 16x16: cada linha é dividida em 2 bytes
for i in range(0, self.grid_width, 8):
    chunk = row[i:i+8]           # Primeiros 8 pixels
    chunk = chunk.ljust(8, '.')  # Preencher com '.' se necessário
    bytes_result.append(self.linha_para_byte(chunk))
```

### 4. Formatos de Saída

#### Código C (PROGMEM)
```c
// Bytes para PROGMEM (u8g2) - Grade 8x8
// 8 linhas x 8 colunas = 8 bytes

static const unsigned char icone_bits[] PROGMEM = {
  0x3C,  // 00111100 - Linha 0
  0x42,  // 01000010 - Linha 1
  0x81,  // 10000001 - Linha 2
  0x81,  // 10000001 - Linha 3
  0x81,  // 10000001 - Linha 4
  0x81,  // 10000001 - Linha 5
  0x42,  // 01000010 - Linha 6
  0x3C,  // 00111100 - Linha 7
};

// Tamanho: 8 bytes
```

#### Representação Binária
```
Representação binária - Grade 8x8:
Linha 0: 00111100
Linha 1: 01000010
Linha 2: 10000001
Linha 3: 10000001
Linha 4: 10000001
Linha 5: 10000001
Linha 6: 01000010
Linha 7: 00111100
```

#### Representação ASCII
```
Representação ASCII - Grade 8x8:
..####..
.#....#.
#......#
#......#
#......#
#......#
.#....#.
..####..
```

## 📋 Requisitos e Instalação

### Dependências Principais
```bash
# Interface gráfica
tkinter (geralmente incluído com Python)

# Processamento de imagens
opencv-python
numpy
```

### Instalação Completa
```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd ascii

# Instalar dependências
pip install -r requirements_image_importer.txt

# Executar
python3 ascii_converter_gui.py
```

### Instalação do tkinter (se necessário)

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
```bash
brew install python-tk
```

## 🚀 Como Usar

### 1. Desenho Manual
1. **Selecione o tamanho da grade** (8x8, 16x16, etc.)
2. **Escolha o tamanho do pincel** (1x1 a 5x5)
3. **Desenhe clicando** ou **arrastando** o mouse
4. **Use Ctrl+Z** para desfazer ações
5. **Clique em "Converter"** para gerar o código

### 2. Importação de Imagem
1. **Clique em "Importar Imagem"**
2. **Selecione uma imagem** (PNG, JPG, etc.)
3. **Visualize o preview** da conversão
4. **Confirme a importação** para aplicar à grade
5. **Ajuste manualmente** se necessário

### 3. Conversão e Exportação
1. **Clique em "Converter"** para processar
2. **Visualize os resultados** nas abas:
   - **Código C**: Código pronto para Arduino/ESP32
   - **Binário**: Representação em bits
   - **ASCII**: Visualização do padrão
3. **Copie o código** para seu projeto

## 🔍 Análise Técnica

### Algoritmo de Conversão
O sistema implementa um algoritmo de conversão bit a bit que:

1. **Lê cada linha** da grade ASCII
2. **Converte caracteres** para bits ('.' = 0, '#' = 1)
3. **Empacota em bytes** de 8 bits
4. **Gera código C** compatível com u8g2

### Otimizações
- **Histórico eficiente**: Apenas 50 estados mantidos em memória
- **Processamento lazy**: Conversão só quando solicitada
- **Cache de preview**: Imagens processadas uma vez
- **Validação em tempo real**: Verificação de formato durante edição

### Compatibilidade
- **u8g2**: Código C gerado é 100% compatível
- **Arduino/ESP32**: Funciona em qualquer plataforma
- **Displays OLED/EPD**: Suporte a todos os tamanhos
- **Cross-platform**: Funciona em Windows, macOS e Linux

## 📊 Casos de Uso

### 1. Ícones para Displays
- **Logotipos** em 16x16 ou 32x32
- **Símbolos** em 8x8 para menus
- **Animações** frame a frame

### 2. Arte ASCII
- **Desenhos** convertidos para displays
- **Padrões** geométricos
- **Textos** estilizados

### 3. Prototipagem Rápida
- **Testes** de interface
- **Mockups** de ícones
- **Validação** de designs

## 🛠️ Desenvolvimento

### Estrutura do Código
```
ascii_converter_gui.py     # Interface principal
├── AsciiConverterGUI      # Classe principal
├── setup_ui()            # Configuração da interface
├── converte()            # Algoritmo de conversão
└── convert_to_xbm()      # Geração de saída

image_importer.py          # Sistema de importação
├── ImageImporter         # Classe de importação
├── process_image()       # Processamento de imagem
└── show_import_dialog()  # Interface de importação

pixel_analyzer.py          # Análise de pixels
├── analyze_image_pixels() # Análise completa
├── analyze_pixel_color()  # Classificação de pixel
└── show_ascii_conversion_preview() # Preview
```

### Extensibilidade
O sistema foi projetado para ser facilmente extensível:

- **Novos formatos de saída** podem ser adicionados
- **Algoritmos de conversão** podem ser modificados
- **Filtros de imagem** podem ser implementados
- **Exportação** para outros formatos é possível

## 🐛 Solução de Problemas

### Problemas Comuns

1. **Imagem não carrega**
   - Verifique se o OpenCV está instalado
   - Confirme o formato do arquivo

2. **Conversão incorreta**
   - Verifique o tamanho da grade
   - Confirme se a imagem tem contraste adequado

3. **Interface não responde**
   - Verifique se o tkinter está instalado
   - Reinicie o programa

### Debug
Para debug detalhado, execute:
```bash
python3 pixel_analyzer.py imagem.png --details
```

## 📈 Roadmap

- [ ] **Suporte a animações** (múltiplos frames)
- [ ] **Filtros de imagem** avançados
- [ ] **Exportação** para outros formatos (SVG, PNG)
- [ ] **Biblioteca de padrões** pré-definidos
- [ ] **API REST** para conversão remota
- [ ] **Plugin system** para extensões

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. **Fork** o projeto
2. **Crie uma branch** para sua feature
3. **Commit** suas mudanças
4. **Push** para a branch
5. **Abra um Pull Request**

### Áreas para Contribuição
- **Melhorias na interface**
- **Novos algoritmos de conversão**
- **Suporte a mais formatos**
- **Documentação e testes**
- **Otimizações de performance**

## 📄 Licença

Este projeto é de código aberto sob a licença MIT. Sinta-se livre para usar, modificar e distribuir.

## 🙏 Agradecimentos

- **OpenCV** por processamento de imagem
- **tkinter** por interface gráfica
- **u8g2** pela inspiração
- **Comunidade open source** pelo suporte

---

**Desenvolvido com ❤️ para a comunidade maker e IoT** # Conversor_ascii
