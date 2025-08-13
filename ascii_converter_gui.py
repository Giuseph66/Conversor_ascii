#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor ASCII para XBM com Interface Gráfica
Converte um desenho em ASCII (# .) para bytes em hexadecimal
compatíveis com u8g2.drawXBM().

Baseado no código T_1.py original.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os

# Importar o sistema de importação de imagem
try:
    from image_importer import create_import_button
    IMAGE_IMPORTER_AVAILABLE = True
except ImportError:
    IMAGE_IMPORTER_AVAILABLE = False
    print("Aviso: Sistema de importação de imagem não disponível. Instale as dependências:")
    print("pip install -r requirements_image_importer.txt")

class AsciiConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor ASCII para XBM")
        
        # Configurar fullscreen
        try:
            self.root.attributes('-zoomed', True)  # Linux
        except:
            pass
        
        self.root.resizable(True, True)
        
        # Variáveis
        self.grid_width = 8
        self.grid_height = 8
        self.cell_size = 40
        self.drawing = False
        self.brush_size = 1  # Tamanho do pincel
        self.show_cell_borders = True  # Controla se as bordas das células são visíveis
        self.grid_data = [['.' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Sistema de histórico para Ctrl+Z
        self.history = []  # Lista de estados anteriores da grade
        self.max_history = 50  # Máximo de estados no histórico
        self.current_history_index = -1  # Índice atual no histórico
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Frame esquerdo - Canvas e controles
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights para o frame esquerdo
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(4, weight=1)  # Canvas deve expandir
        
        # Controles superiores
        control_frame = ttk.Frame(left_frame)
        control_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Controles de largura
        ttk.Label(control_frame, text="Largura:", font=("Arial", 10)).grid(row=0, column=0, padx=(0, 5))
        self.width_var = tk.StringVar(value="8")
        self.width_entry = ttk.Entry(control_frame, textvariable=self.width_var, width=5)
        self.width_entry.grid(row=0, column=1, padx=(0, 10))
        
        # Controles de altura
        ttk.Label(control_frame, text="Altura:", font=("Arial", 10)).grid(row=0, column=2, padx=(0, 5))
        self.height_var = tk.StringVar(value="8")
        self.height_entry = ttk.Entry(control_frame, textvariable=self.height_var, width=5)
        self.height_entry.grid(row=0, column=3, padx=(0, 10))
        
        # Botão para aplicar mudança de tamanho
        ttk.Button(control_frame, text="Aplicar Tamanho", command=self.apply_size_change).grid(row=0, column=4, padx=5)
        
        # Tamanhos pré-definidos
        preset_frame = ttk.Frame(left_frame)
        preset_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(preset_frame, text="Tamanhos rápidos:", font=("Arial", 9)).grid(row=0, column=0, padx=(0, 5))
        
        presets = ["8x8", "16x16", "32x32", "20x31", "10x24", "64x64"]
        for i, preset in enumerate(presets):
            btn = ttk.Button(preset_frame, text=preset, width=6,
                           command=lambda p=preset: self.apply_preset(p))
            btn.grid(row=0, column=i+1, padx=2)
        
        # Controles do pincel
        brush_frame = ttk.Frame(left_frame)
        brush_frame.grid(row=2, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(brush_frame, text="Tamanho do pincel:", font=("Arial", 9)).grid(row=0, column=0, padx=(0, 5))
        
        # Botões de tamanho de pincel
        brush_sizes = [1, 2, 3, 4, 5]
        for i, size in enumerate(brush_sizes):
            btn = ttk.Button(brush_frame, text=f"{size}x{size}", width=4,
                           command=lambda s=size: self.set_brush_size(s))
            btn.grid(row=0, column=i+1, padx=2)
            # Destacar o tamanho atual
            if size == self.brush_size:
                btn.state(['pressed'])
        
        # Label para mostrar tamanho atual do pincel
        self.brush_info_label = ttk.Label(brush_frame, text=f"Pincel: {self.brush_size}x{self.brush_size}", 
                                         font=("Arial", 9, "bold"), foreground="blue")
        self.brush_info_label.grid(row=0, column=len(brush_sizes)+1, padx=(10, 0))
        
        # Título do canvas
        ttk.Label(left_frame, text="Desenhe seu padrão:", font=("Arial", 12, "bold")).grid(row=3, column=0, pady=(0, 10))
        
        # Canvas para desenho
        self.canvas = tk.Canvas(left_frame, bg='white', relief='raised', bd=2)
        self.canvas.grid(row=4, column=0, pady=(0, 10))
        
        # Botões de controle
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=5, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Configurar grid weights para o frame de botões
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.columnconfigure(3, weight=1)
        btn_frame.columnconfigure(4, weight=1)
        btn_frame.columnconfigure(5, weight=1)  # Novo para o botão de importação
        
        ttk.Button(btn_frame, text="Limpar", command=self.clear_grid).grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="Inverter", command=self.invert_grid).grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="Converter", command=self.convert_to_xbm).grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="Desfazer", command=self.undo).grid(row=0, column=3, padx=5, sticky=(tk.W, tk.E))
        
        # Toggle button para bordas das células
        self.border_var = tk.BooleanVar(value=self.show_cell_borders)
        self.border_toggle = ttk.Checkbutton(btn_frame, text="Bordas", 
                                           command=self.toggle_cell_borders, 
                                           variable=self.border_var)
        self.border_toggle.grid(row=0, column=4, padx=5, sticky=(tk.W, tk.E))
        
        # Botão de importação de imagem (se disponível)
        if IMAGE_IMPORTER_AVAILABLE:
            create_import_button(self, btn_frame, 0, 5)
        else:
            # Botão desabilitado se o importador não estiver disponível
            import_btn = ttk.Button(btn_frame, text="Importar Imagem", 
                                   command=self.show_import_error, state="disabled")
            import_btn.grid(row=0, column=5, padx=5, sticky=(tk.W, tk.E))
        
        # Frame de status
        status_frame = ttk.Frame(left_frame)
        status_frame.grid(row=6, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text=f"Grade: {self.grid_width}x{self.grid_height} | Pincel: {self.brush_size}x{self.brush_size}", 
                                     font=("Arial", 9), foreground="green")
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Frame direito - Resultado
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(right_frame, text="Resultado da Conversão:", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(0, 10))
        
        # Frame para controles de copiar/colar (acima das abas)
        copy_paste_frame = ttk.Frame(right_frame)
        copy_paste_frame.grid(row=1, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        copy_paste_frame.columnconfigure(0, weight=1)
        copy_paste_frame.columnconfigure(1, weight=1)
        copy_paste_frame.columnconfigure(2, weight=1)
        copy_paste_frame.columnconfigure(3, weight=1)
        
        # Botões de copiar e colar
        ttk.Button(copy_paste_frame, text="📋 Copiar", 
                  command=self.copy_active_tab).grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(copy_paste_frame, text="📥 Colar", 
                  command=self.paste_to_active_tab).grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(copy_paste_frame, text="🔄 Aplicar", 
                  command=self.apply_from_active_tab).grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(copy_paste_frame, text="🗑️ Limpar", 
                  command=self.clear_active_tab).grid(row=0, column=3, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Notebook para diferentes formatos de saída
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Aba para código C
        c_frame = ttk.Frame(self.notebook)
        self.notebook.add(c_frame, text="Código C")
        
        self.c_text = scrolledtext.ScrolledText(c_frame, width=40, height=10, font=("Courier", 10))
        self.c_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Aba para representação binária
        bin_frame = ttk.Frame(self.notebook)
        self.notebook.add(bin_frame, text="Binário")
        
        self.bin_text = scrolledtext.ScrolledText(bin_frame, width=40, height=10, font=("Courier", 10))
        self.bin_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Aba para ASCII
        ascii_frame = ttk.Frame(self.notebook)
        self.notebook.add(ascii_frame, text="ASCII")
        
        # Área de texto ASCII (sem controles, apenas o texto)
        self.ascii_text = scrolledtext.ScrolledText(ascii_frame, width=40, height=10, font=("Courier", 10))
        self.ascii_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Configurar grid weights para frames
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(2, weight=1)  # Notebook agora está na linha 2
        c_frame.columnconfigure(0, weight=1)
        c_frame.rowconfigure(0, weight=1)
        bin_frame.columnconfigure(0, weight=1)
        bin_frame.rowconfigure(0, weight=1)
        ascii_frame.columnconfigure(0, weight=1)
        ascii_frame.rowconfigure(0, weight=1)
        
        # Calcular tamanho inicial do canvas
        self.update_canvas_size()
        self.draw_grid()
        
        # Salvar estado inicial no histórico
        self.save_state()
        
    def setup_bindings(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)  # Botão esquerdo - preto
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)  # Botão direito - branco
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)  # Arrasto botão esquerdo - preto
        self.canvas.bind("<B3-Motion>", self.on_canvas_right_drag)  # Arrasto botão direito - branco
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<ButtonRelease-3>", self.on_canvas_release)
        
        # Binding para Ctrl+Z (desfazer)
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-Z>", lambda e: self.undo())  # Também funciona com Shift
        
        # Bindings para copiar e colar na aba ativa
        self.root.bind("<Control-c>", lambda e: self.copy_active_tab())
        self.root.bind("<Control-C>", lambda e: self.copy_active_tab())
        self.root.bind("<Control-v>", lambda e: self.paste_to_active_tab())
        self.root.bind("<Control-V>", lambda e: self.paste_to_active_tab())
            
    def apply_preset(self, preset):
        """Aplica um tamanho pré-definido"""
        try:
            width, height = map(int, preset.split('x'))
            self.width_var.set(str(width))
            self.height_var.set(str(height))
            self.apply_size_change()
        except:
            pass
            
    def set_brush_size(self, size):
        """Define o tamanho do pincel"""
        self.brush_size = size
        self.brush_info_label.config(text=f"Pincel: {self.brush_size}x{self.brush_size}")
        self.update_status()
        
        # Atualizar aparência dos botões (abordagem mais simples)
        # Os botões serão atualizados visualmente na próxima interação
            
    def apply_size_change(self):
        """Aplica a mudança de tamanho da grade"""
        try:
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())
            
            # Validações
            if new_width < 1 or new_width > 200:
                messagebox.showerror("Erro", "Largura deve estar entre 1 e 200")
                return
            if new_height < 1 or new_height > 200:
                messagebox.showerror("Erro", "Altura deve estar entre 1 e 200")
                return
                
            if new_width != self.grid_width or new_height != self.grid_height:
                # Confirmar mudança se houver dados
                if any(any(cell == '#' for cell in row) for row in self.grid_data):
                    if not messagebox.askyesno("Confirmar", 
                                             f"Alterar o tamanho da grade de {self.grid_width}x{self.grid_height} para {new_width}x{new_height}?\n"
                                             "Isso apagará o desenho atual."):
                        return
                
                # Atualizar tamanhos
                self.grid_width = new_width
                self.grid_height = new_height
                self.update_canvas_size()
                # Limpar histórico ao mudar tamanho da grade
                self.history = []
                self.current_history_index = -1
                self.clear_grid()
                self.draw_grid()
                self.update_status()
                
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira números válidos para largura e altura")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar tamanho: {str(e)}")
            
    def update_canvas_size(self):
        """Atualiza o tamanho do canvas baseado no tamanho da grade e da tela"""
        # Obter dimensões da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcular tamanho disponível para o canvas (deixar espaço para controles e resultados)
        available_width = screen_width - 600  # Espaço para controles e resultados
        available_height = screen_height - 200  # Espaço para controles
        
        # Calcular tamanho da célula para caber na tela
        max_cell_width = available_width // self.grid_width
        max_cell_height = available_height // self.grid_height
        
        # Usar o menor dos dois para manter células quadradas
        self.cell_size = min(max_cell_width, max_cell_height, 50)  # Máximo de 50px por célula
        
        # Calcular tamanho total do canvas
        canvas_width = self.grid_width * self.cell_size
        canvas_height = self.grid_height * self.cell_size
        
        # Redimensionar canvas
        self.canvas.config(width=canvas_width, height=canvas_height)
        
        # Atualizar status
        self.update_status()
        
    def draw_grid(self):
        """Desenha a grade no canvas"""
        self.canvas.delete("grid")
        
        # Desenhar linhas verticais
        for i in range(self.grid_width + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_height * self.cell_size, fill='gray', tags="grid")
            
        # Desenhar linhas horizontais
        for i in range(self.grid_height + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid_width * self.cell_size, y, fill='gray', tags="grid")
            
        # Preencher células com dados atuais
        self.fill_cells()
        
    def fill_cells(self):
        """Preenche as células do canvas com os dados atuais"""
        self.canvas.delete("cells")
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Definir cor de preenchimento
                fill_color = 'black' if self.grid_data[row][col] == '#' else 'white'
                
                # Definir cor da borda
                outline_color = 'lightgray' if self.show_cell_borders else ''
                
                # Criar retângulo da célula
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                          fill=fill_color, 
                                          outline=outline_color, 
                                          width=1 if self.show_cell_borders else 0,
                                          tags="cells")
                    
    def get_canvas_coords(self, event):
        """Converte coordenadas do evento para coordenadas da grade"""
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if 0 <= row < self.grid_height and 0 <= col < self.grid_width:
            return row, col
        return None, None
        
    def on_canvas_click(self, event):
        """Manipula clique esquerdo no canvas (preto)"""
        row, col = self.get_canvas_coords(event)
        if row is not None and col is not None:
            # Aplicar pincel do tamanho selecionado (preto)
            self.apply_brush(row, col, '#')
            self.fill_cells()
            
    def on_canvas_right_click(self, event):
        """Manipula clique direito no canvas (branco)"""
        row, col = self.get_canvas_coords(event)
        if row is not None and col is not None:
            # Aplicar pincel do tamanho selecionado (branco)
            self.apply_brush(row, col, '.')
            self.fill_cells()
            
    def on_canvas_drag(self, event):
        """Manipula arrastar no canvas com botão esquerdo (preto)"""
        row, col = self.get_canvas_coords(event)
        if row is not None and col is not None:
            # Aplicar pincel do tamanho selecionado (preto)
            self.apply_brush(row, col, '#')
            self.fill_cells()
            
    def on_canvas_right_drag(self, event):
        """Manipula arrastar no canvas com botão direito (branco)"""
        row, col = self.get_canvas_coords(event)
        if row is not None and col is not None:
            # Aplicar pincel do tamanho selecionado (branco)
            self.apply_brush(row, col, '.')
            self.fill_cells()
            
    def on_canvas_release(self, event):
        """Manipula soltura do botão do mouse"""
        pass
        
    def clear_grid(self):
        """Limpa toda a grade"""
        # Salvar estado anterior no histórico
        self.save_state()
        
        self.grid_data = [['.' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.fill_cells()
        
    def invert_grid(self):
        """Inverte todos os valores da grade"""
        # Salvar estado anterior no histórico
        self.save_state()
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.grid_data[row][col] = '#' if self.grid_data[row][col] == '.' else '.'
        self.fill_cells()
        
    def linha_para_byte(self, linha):
        """
        Transforma caracteres ('.' ou '#') numa máscara de bits.
        Bit 0 (LSB) = primeiro caractere da linha (ESQUERDA).
        """
        bits = 0
        max_bits = min(8, len(linha))  # Limitar a 8 bits por byte
        
        for pos, ch in enumerate(linha[:max_bits]):
            if ch == '#':
                bits |= (1 << pos)
        return bits
        
    def converte(self, desenho):
        """Converte o desenho para bytes"""
        if len(desenho) != self.grid_height:
            raise ValueError(f"O desenho deve ter exatamente {self.grid_height} linhas.")
            
        bytes_result = []
        
        # Para grades maiores que 8, dividir em bytes de 8 bits
        for row in desenho:
            if self.grid_width <= 8:
                # Uma linha = um byte (se couber)
                bytes_result.append(self.linha_para_byte(row))
            else:
                # Dividir linha em bytes de 8 bits
                for i in range(0, self.grid_width, 8):
                    chunk = row[i:i+8]
                    # Preencher com '.' se necessário
                    chunk = ''.join(chunk).ljust(8, '.')
                    bytes_result.append(self.linha_para_byte(chunk))
                    
        return bytes_result
        
    def convert_to_xbm(self):
        """Converte o desenho para formato XBM e exibe os resultados"""
        try:
            # Converter linhas para bytes
            bytes_hex = self.converte(self.grid_data)
            
            # Gerar código C
            c_code = f"// Bytes para PROGMEM (u8g2) - Grade {self.grid_width}x{self.grid_height}\n"
            c_code += f"// {self.grid_height} linhas x {self.grid_width} colunas = {len(bytes_hex)} bytes\n\n"
            c_code += "static const unsigned char icone_bits[] PROGMEM = {\n"
            for b in bytes_hex:
                c_code += f"  0x{b:02X},\n"
            c_code += "};\n\n"
            c_code += f"// Tamanho: {len(bytes_hex)} bytes"
            
            # Gerar representação binária
            bin_code = f"Representação binária - Grade {self.grid_width}x{self.grid_height}:\n"
            if self.grid_width <= 8:
                for i, b in enumerate(bytes_hex):
                    bin_code += f"Linha {i}: {b:08b}\n"
            else:
                byte_count = 0
                for row_idx in range(self.grid_height):
                    bin_code += f"Linha {row_idx}: "
                    for col in range(0, self.grid_width, 8):
                        if byte_count < len(bytes_hex):
                            bin_code += f"{bytes_hex[byte_count]:08b} "
                            byte_count += 1
                    bin_code += "\n"
                
            # Gerar representação ASCII
            ascii_code = f"Representação ASCII - Grade {self.grid_width}x{self.grid_height}:\n"
            for row in self.grid_data:
                ascii_code += "".join(row) + "\n"
                
            # Atualizar textos
            self.c_text.delete(1.0, tk.END)
            self.c_text.insert(1.0, c_code)
            
            self.bin_text.delete(1.0, tk.END)
            self.bin_text.insert(1.0, bin_code)
            
            self.ascii_text.delete(1.0, tk.END)
            self.ascii_text.insert(1.0, ascii_code)
            
            # Selecionar primeira aba
            self.notebook.select(0)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na conversão: {str(e)}")

    def apply_brush(self, center_row, center_col, color='#'):
        """
        Aplica o pincel do tamanho selecionado na posição central
        color: '#' para preto, '.' para branco
        """
        # Salvar estado anterior no histórico
        self.save_state()
        
        # Calcular área afetada pelo pincel
        # Para pincel 1x1: apenas a célula central
        # Para pincel 2x2: 2x2 células a partir da posição
        # Para pincel 3x3: 3x3 células a partir da posição, etc.
        
        if self.brush_size == 1:
            # Pincel 1x1: apenas a célula clicada
            if 0 <= center_row < self.grid_height and 0 <= center_col < self.grid_width:
                self.grid_data[center_row][center_col] = color
        else:
            # Pincel maior: calcular a área correta
            # O pincel deve cobrir exatamente o tamanho especificado
            start_row = center_row
            end_row = min(self.grid_height, center_row + self.brush_size)
            start_col = center_col
            end_col = min(self.grid_width, center_col + self.brush_size)
            
            for row in range(start_row, end_row):
                for col in range(start_col, end_col):
                    # Definir cor da célula
                    self.grid_data[row][col] = color

    def update_status(self):
        """Atualiza o texto do status label"""
        border_status = "ON" if self.show_cell_borders else "OFF"
        undo_status = f"Desfazer: {len(self.history)}" if len(self.history) > 1 else "Desfazer: N/A"
        mouse_info = "🖱️ Esq: Preto | Dir: Branco"
        import_status = "📁 Importar: Disponível" if IMAGE_IMPORTER_AVAILABLE else "📁 Importar: Não disponível"
        
        self.status_label.config(text=f"Grade: {self.grid_width}x{self.grid_height} | Pincel: {self.brush_size}x{self.brush_size} | Bordas: {border_status} | {undo_status} | {mouse_info} | {import_status}")

    def toggle_cell_borders(self):
        """Alterna a visibilidade das bordas das células"""
        self.show_cell_borders = self.border_var.get()
        self.draw_grid() # Redesenha a grade para mostrar/ocultar as bordas
        self.update_status() # Atualiza o status para mostrar o estado atual

    def save_state(self):
        """Salva o estado atual da grade no histórico"""
        # Criar uma cópia profunda do estado atual
        current_state = [row[:] for row in self.grid_data]
        
        # Se estamos no meio do histórico, remover estados futuros
        if self.current_history_index < len(self.history) - 1:
            self.history = self.history[:self.current_history_index + 1]
        
        # Adicionar novo estado ao histórico
        self.history.append(current_state)
        self.current_history_index = len(self.history) - 1
        
        # Manter apenas os últimos max_history estados
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
            self.current_history_index = len(self.history) - 1
            
        # Atualizar status
        self.update_status()
        
    def undo(self):
        """Desfaz a última ação (Ctrl+Z)"""
        if self.current_history_index > 0:
            self.current_history_index -= 1
            # Restaurar estado anterior
            previous_state = self.history[self.current_history_index]
            self.grid_data = [row[:] for row in previous_state]
            self.fill_cells()
            self.update_status()
        else:
            # Não há mais estados para desfazer
            messagebox.showinfo("Desfazer", "Não há mais ações para desfazer.")
            
    def can_undo(self):
        """Verifica se é possível desfazer"""
        return self.current_history_index > 0

    def show_import_error(self):
        """Exibe uma mensagem de erro se o importador de imagem não estiver disponível"""
        messagebox.showerror("Erro de Importação", 
                             "O sistema de importação de imagem não está disponível.\n"
                             "Por favor, instale as dependências necessárias:\n"
                             "pip install -r requirements_image_importer.txt")

    def copy_ascii(self):
        """Copia o conteúdo ASCII da área de texto para o clipboard"""
        ascii_content = self.ascii_text.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(ascii_content)
        self.root.update() # Atualiza a interface
        messagebox.showinfo("Copiado", "Conteúdo ASCII copiado para o clipboard!")

    def paste_ascii(self):
        """Cola o conteúdo ASCII do clipboard para a área de texto"""
        try:
            pasted_content = self.root.clipboard_get()
            
            # Limpar e validar o conteúdo colado
            cleaned_content = self.clean_ascii_content(pasted_content)
            
            if cleaned_content:
                self.ascii_text.delete(1.0, tk.END)
                self.ascii_text.insert(1.0, cleaned_content)
                messagebox.showinfo("Colado", "Conteúdo ASCII colado com sucesso!")
            else:
                messagebox.showwarning("Aviso", "O conteúdo colado não é um formato ASCII válido.")
                
        except Exception as e:
            messagebox.showwarning("Aviso", f"Não foi possível colar o conteúdo do clipboard: {str(e)}")
    
    def clean_ascii_content(self, content):
        """Limpa e valida o conteúdo ASCII colado"""
        if not content:
            return ""
            
        # Remover caracteres de controle e espaços extras
        lines = content.strip().splitlines()
        cleaned_lines = []
        
        for line in lines:
            # Remover espaços em branco e caracteres inválidos
            cleaned_line = ''.join(char for char in line if char in ['#', '.', ' '])
            # Substituir espaços por pontos (branco)
            cleaned_line = cleaned_line.replace(' ', '.')
            
            if cleaned_line:  # Se a linha não estiver vazia
                cleaned_lines.append(cleaned_line)
        
        # Verificar se o conteúdo tem o formato correto
        if len(cleaned_lines) == 0:
            return ""
            
        # Verificar se todas as linhas têm o mesmo comprimento
        line_lengths = set(len(line) for line in cleaned_lines)
        if len(line_lengths) != 1:
            return ""
            
        # Verificar se o comprimento é válido para a grade atual
        line_length = list(line_lengths)[0]
        if line_length != self.grid_width:
            return ""
            
        # Verificar se o número de linhas é válido
        if len(cleaned_lines) != self.grid_height:
            return ""
            
        return '\n'.join(cleaned_lines)

    def apply_ascii_to_grid(self):
        """Aplica o conteúdo da área de texto ASCII para a grade"""
        ascii_content = self.ascii_text.get(1.0, tk.END).strip()
        
        if not ascii_content:
            messagebox.showwarning("Aviso", "A área de texto ASCII está vazia.")
            return
            
        lines = ascii_content.splitlines()
        
        # Validações
        if len(lines) != self.grid_height:
            messagebox.showerror("Erro", f"O conteúdo ASCII deve ter exatamente {self.grid_height} linhas.\n"
                               f"Atual: {len(lines)} linhas")
            return
            
        # Verificar cada linha
        for i, line in enumerate(lines):
            if len(line) != self.grid_width:
                messagebox.showerror("Erro", f"A linha {i+1} deve ter exatamente {self.grid_width} caracteres.\n"
                                   f"Atual: {len(line)} caracteres")
                return
                
            # Verificar caracteres válidos
            for j, char in enumerate(line):
                if char not in ['#', '.']:
                    messagebox.showerror("Erro", f"Caractere inválido na linha {i+1}, coluna {j+1}: '{char}'\n"
                                       f"Use apenas '#' (preto) ou '.' (branco)")
                    return
        
        # Confirmar aplicação se houver dados na grade
        if any(any(cell == '#' for cell in row) for row in self.grid_data):
            if not messagebox.askyesno("Confirmar", 
                                     f"Aplicar o padrão ASCII à grade {self.grid_width}x{self.grid_height}?\n"
                                     "Isso substituirá o desenho atual."):
                return
        
        # Aplicar à grade
        try:
            for i, line in enumerate(lines):
                for j, char in enumerate(line):
                    self.grid_data[i][j] = char
            
            # Atualizar interface
            self.fill_cells()
            self.update_status()
            self.save_state()  # Salva o estado após a aplicação
            
            messagebox.showinfo("Sucesso", f"Padrão ASCII aplicado à grade {self.grid_width}x{self.grid_height}!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar padrão ASCII: {str(e)}")

    def clear_ascii_text(self):
        """Limpa o conteúdo da área de texto ASCII"""
        self.ascii_text.delete(1.0, tk.END)
        messagebox.showinfo("Limpo", "Área de texto ASCII limpa!")

    def copy_active_tab(self):
        """Copia o conteúdo da aba ativa para o clipboard"""
        active_tab = self.notebook.tab(self.notebook.select(), "text")
        if active_tab == "Código C":
            content = self.c_text.get(1.0, tk.END).strip()
        elif active_tab == "Binário":
            content = self.bin_text.get(1.0, tk.END).strip()
        elif active_tab == "ASCII":
            content = self.ascii_text.get(1.0, tk.END).strip()
        else:
            content = ""

        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
        messagebox.showinfo("Copiado", f"Conteúdo da aba '{active_tab}' copiado para o clipboard!")

    def paste_to_active_tab(self):
        """Cola o conteúdo do clipboard para a aba ativa"""
        try:
            pasted_content = self.root.clipboard_get()
            
            active_tab = self.notebook.tab(self.notebook.select(), "text")
            if active_tab == "Código C":
                self.c_text.delete(1.0, tk.END)
                self.c_text.insert(1.0, pasted_content)
            elif active_tab == "Binário":
                self.bin_text.delete(1.0, tk.END)
                self.bin_text.insert(1.0, pasted_content)
            elif active_tab == "ASCII":
                self.ascii_text.delete(1.0, tk.END)
                self.ascii_text.insert(1.0, pasted_content)
            else:
                messagebox.showwarning("Aviso", "Nenhuma aba ativa para colar o conteúdo.")
                
            messagebox.showinfo("Colado", f"Conteúdo colado na aba '{active_tab}'!")
                
        except Exception as e:
            messagebox.showwarning("Aviso", f"Não foi possível colar o conteúdo do clipboard: {str(e)}")

    def apply_from_active_tab(self):
        """Aplica o conteúdo da aba ativa para a grade"""
        active_tab = self.notebook.tab(self.notebook.select(), "text")
        
        # Obter conteúdo da aba ativa
        if active_tab == "Código C":
            content = self.c_text.get(1.0, tk.END).strip()
            # Tentar extrair apenas o conteúdo ASCII do código C
            ascii_content = self.extract_ascii_from_c_code(content)
        elif active_tab == "Binário":
            content = self.bin_text.get(1.0, tk.END).strip()
            # Tentar converter binário para ASCII
            ascii_content = self.convert_binary_to_ascii(content)
        elif active_tab == "ASCII":
            ascii_content = self.ascii_text.get(1.0, tk.END).strip()
        else:
            ascii_content = ""

        if not ascii_content:
            messagebox.showwarning("Aviso", f"A área de texto da aba '{active_tab}' está vazia ou não contém dados válidos.")
            return
            
        lines = ascii_content.splitlines()
        
        # Validações
        if len(lines) != self.grid_height:
            messagebox.showerror("Erro", f"O conteúdo deve ter exatamente {self.grid_height} linhas.\n"
                               f"Atual: {len(lines)} linhas")
            return
            
        # Verificar cada linha
        for i, line in enumerate(lines):
            if len(line) != self.grid_width:
                messagebox.showerror("Erro", f"A linha {i+1} deve ter exatamente {self.grid_width} caracteres.\n"
                                   f"Atual: {len(line)} caracteres")
                return
                
            # Verificar caracteres válidos
            for j, char in enumerate(line):
                if char not in ['#', '.']:
                    messagebox.showerror("Erro", f"Caractere inválido na linha {i+1}, coluna {j+1}: '{char}'\n"
                                       f"Use apenas '#' (preto) ou '.' (branco)")
                    return
        
        # Confirmar aplicação se houver dados na grade
        if any(any(cell == '#' for cell in row) for row in self.grid_data):
            if not messagebox.askyesno("Confirmar", 
                                     f"Aplicar o padrão da aba '{active_tab}' à grade {self.grid_width}x{self.grid_height}?\n"
                                     "Isso substituirá o desenho atual."):
                return
        
        # Aplicar à grade
        try:
            for i, line in enumerate(lines):
                for j, char in enumerate(line):
                    self.grid_data[i][j] = char
            
            # Atualizar interface
            self.fill_cells()
            self.update_status()
            self.save_state()  # Salva o estado após a aplicação
            
            messagebox.showinfo("Sucesso", f"Padrão da aba '{active_tab}' aplicado à grade {self.grid_width}x{self.grid_height}!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar padrão: {str(e)}")
    
    def extract_ascii_from_c_code(self, c_code):
        """Extrai conteúdo ASCII do código C"""
        # Tentar encontrar padrões ASCII no código C
        lines = c_code.splitlines()
        ascii_lines = []
        
        for line in lines:
            # Procurar por linhas que contenham apenas # e .
            if all(char in ['#', '.', ' ', '\t'] for char in line):
                # Limpar espaços e tabs
                cleaned_line = ''.join(char for char in line if char in ['#', '.'])
                if cleaned_line and len(cleaned_line) <= self.grid_width:
                    ascii_lines.append(cleaned_line)
        
        if len(ascii_lines) == self.grid_height:
            return '\n'.join(ascii_lines)
        return ""
    
    def convert_binary_to_ascii(self, binary_content):
        """Converte conteúdo binário para ASCII"""
        lines = binary_content.splitlines()
        ascii_lines = []
        
        for line in lines:
            # Procurar por padrões binários (0s e 1s)
            if all(char in ['0', '1', ' '] for char in line):
                # Converter 0 para . e 1 para #
                ascii_line = line.replace('0', '.').replace('1', '#')
                # Remover espaços
                ascii_line = ''.join(char for char in ascii_line if char in ['#', '.'])
                if ascii_line and len(ascii_line) <= self.grid_width:
                    ascii_lines.append(ascii_line)
        
        if len(ascii_lines) == self.grid_height:
            return '\n'.join(ascii_lines)
        return ""

    def clear_active_tab(self):
        """Limpa o conteúdo da aba ativa"""
        active_tab = self.notebook.tab(self.notebook.select(), "text")
        if active_tab == "Código C":
            self.c_text.delete(1.0, tk.END)
        elif active_tab == "Binário":
            self.bin_text.delete(1.0, tk.END)
        elif active_tab == "ASCII":
            self.ascii_text.delete(1.0, tk.END)
        messagebox.showinfo("Limpo", f"Área de texto da aba '{active_tab}' limpa!")

def main():
    root = tk.Tk()
    app = AsciiConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 