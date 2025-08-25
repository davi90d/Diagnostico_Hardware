"""
Módulo para teste de Teclado.
Implementa teste real de teclado com interface visual similar ao testarteclado.com.br.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard

class KeyboardTest:
    """Classe para teste de teclado."""
    
    def __init__(self):
        """Inicializa o teste de teclado."""
        self.window = None
        self.key_buttons = {}
        self.pressed_keys = set()
        self.listener = None
        self.is_running = False
        self.is_completed = False
        self.result = {
            'success': False,
            'message': '',
            'details': {},
            'error': None
        }
    
    def initialize(self):
        """Inicializa o teste de teclado."""
        try:
            self.is_running = True
            return True
        except Exception as e:
            self.result['error'] = str(e)
            return False
    
    def execute(self):
        """Executa o teste de teclado."""
        try:
            # Cria a janela de teste
            self.window = tk.Toplevel()
            self.window.title("Teste de Teclado")
            self.window.geometry("1000x400")
            self.window.resizable(True, True)
            self.window.protocol("WM_DELETE_WINDOW", self._on_close)
            
            # Centraliza a janela
            self.window.update_idletasks()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ttk.Frame(self.window, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            title_label = ttk.Label(
                main_frame,
                text="Teste de Teclado - Pressione todas as teclas para validar",
                font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 10))
            
            # Contador de teclas
            self.counter_var = tk.StringVar(value="0 de 0 teclas pressionadas")
            counter_label = ttk.Label(
                main_frame,
                textvariable=self.counter_var,
                font=("Arial", 12)
            )
            counter_label.pack(pady=(0, 10))
            
            # Frame para o teclado
            keyboard_frame = ttk.Frame(main_frame)
            keyboard_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            self._create_keyboard_layout(keyboard_frame)
            # Frame para botões de ação
            action_frame = ttk.Frame(main_frame)
            action_frame.pack(fill=tk.X, pady=(10, 0))
            skip_button = ttk.Button(
                action_frame,
                text="Pular Teste",
                command=self._skip_test
            )
            skip_button.pack(side=tk.LEFT, padx=5)
            self.complete_button = ttk.Button(
                action_frame,
                text="Concluir Teste",
                state=tk.DISABLED,
                command=self._complete_test
            )
            self.complete_button.pack(side=tk.RIGHT, padx=5)
            # Inicia o listener de teclado
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
    
            
            # Aguarda a conclusão do teste
            self.window.wait_window()
            
            # Retorna o resultado
            return self.is_completed
        except Exception as e:
            self.result['error'] = str(e)
            return False
        finally:
            # Garante que o listener seja encerrado
            if self.listener:
                self.listener.stop()
    
    def _create_keyboard_layout(self, parent):
        """Cria o layout do teclado ABNT2."""
        # Teclas modificadoras que terão botões duplicados visualmente
        dual_keys = {
            'Shift': ['Shift (Esq)', 'Shift (Dir)'],
            'Ctrl': ['Ctrl (Esq)', 'Ctrl (Dir)'],
            'Alt': ['Alt (Esq)', 'Alt (Dir)'],
            'Win': ['Win (Esq)', 'Win (Dir)'],
        }
        # Mapeamento reverso para identificar qual tecla lógica corresponde ao botão visual
        self.visual_to_logical = {}
        keyboard_layout = [
            [('Esc', 1), ('F1', 1), ('F2', 1), ('F3', 1), ('F4', 1), ('F5', 1), ('F6', 1), ('F7', 1), ('F8', 1), ('F9', 1), ('F10', 1), ('F11', 1), ('F12', 1), ('PrtSc', 1), ('ScrLk', 1), ('Pause', 1)],
            [('\'', 1), ('1', 1), ('2', 1), ('3', 1), ('4', 1), ('5', 1), ('6', 1), ('7', 1), ('8', 1), ('9', 1), ('0', 1), ('-', 1), ('=', 1), ('Backspace', 2), ('Insert', 1), ('Home', 1), ('PgUp', 1)],
            [('Tab', 1.5), ('Q', 1), ('W', 1), ('E', 1), ('R', 1), ('T', 1), ('Y', 1), ('U', 1), ('I', 1), ('O', 1), ('P', 1), ('[', 1), (']', 1), ('Delete', 1), ('End', 1), ('PgDn', 1)],
            [('Caps Lock', 1.75), ('A', 1), ('S', 1), ('D', 1), ('F', 1), ('G', 1), ('H', 1), ('J', 1), ('K', 1), ('L', 1), ('Ç', 1), (';', 1), ('`', 1), ('Enter', 2.25)],
            # Linha do Shift (duplicado)
            [(dual_keys['Shift'][0], 1.25), ('\\', 1), ('Z', 1), ('X', 1), ('C', 1), ('V', 1), ('B', 1), ('N', 1), ('M', 1), (',', 1), ('.', 1), ('/', 1), (dual_keys['Shift'][1], 2.75), ('↑', 1)],
            # Linha inferior com Ctrl, Win, Alt (duplicados)
            [
                (dual_keys['Ctrl'][0], 1.25),
                (dual_keys['Win'][0], 1.25),
                (dual_keys['Alt'][0], 1.25),
                ('Space', 6.25),
                (dual_keys['Alt'][1], 1.25),
                (dual_keys['Win'][1], 1.25),
                ('Menu', 1.25),
                (dual_keys['Ctrl'][1], 1.25),
                ('←', 1), ('↓', 1), ('→', 1)
            ]
        ]
        for row in keyboard_layout:
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=2)
            for key, width in row:
                # Se for um botão visual de modificadora, mapeia para a lógica
                logical_key = None
                for logic, visuals in dual_keys.items():
                    if key in visuals:
                        logical_key = logic
                        self.visual_to_logical[key] = logic
                        break
                if not logical_key:
                    logical_key = key
                button = ttk.Button(
                    row_frame,
                    text=key,
                    width=int(width * 4),
                    command=lambda k=key: self._on_virtual_key_press(k)
                )
                button.pack(side=tk.LEFT, padx=1, pady=1)
                self.key_buttons[key] = button
        self.counter_var.set(f"0 de {len(self.key_buttons)} teclas pressionadas")
        # Corrige o nome lógico da tecla barra invertida para coincidir com o layout
        # Adiciona um mapeamento visual para lógica para '\'
        self.visual_to_logical['\\'] = '\\'

    def _mark_all_variants(self, key):
        """Marca todas as variantes (esquerda, direita e genérica) de uma tecla modificadora."""
        variants = {
            'Shift': ['Shift', 'Shift_l', 'Shift_r'],
            'Shift_l': ['Shift', 'Shift_l', 'Shift_r'],
            'Shift_r': ['Shift', 'Shift_l', 'Shift_r'],
            'Ctrl': ['Ctrl', 'Ctrl_l', 'Ctrl_r'],
            'Ctrl_l': ['Ctrl', 'Ctrl_l', 'Ctrl_r'],
            'Ctrl_r': ['Ctrl', 'Ctrl_l', 'Ctrl_r'],
            'Alt': ['Alt', 'Alt_l', 'Alt_r'],
            'Alt_l': ['Alt', 'Alt_l', 'Alt_r'],
            'Alt_r': ['Alt', 'Alt_l', 'Alt_r'],
            'Win': ['Win', 'cmd', 'cmd_l', 'cmd_r'],
            'cmd': ['Win', 'cmd', 'cmd_l', 'cmd_r'],
            'cmd_l': ['Win', 'cmd', 'cmd_l', 'cmd_r'],
            'cmd_r': ['Win', 'cmd', 'cmd_l', 'cmd_r'],
        }
        if key in variants:
            for v in variants[key]:
                if v in self.key_buttons:
                    self.pressed_keys.add(v)
                    self.window.after(0, lambda k=v: self._update_button_style(k, True))
            return True
        return False

    def _on_virtual_key_press(self, key):
        """Permite que o clique no botão do teclado virtual conte como tecla pressionada."""
        # Se for um botão visual de modificadora, marca todos os botões visuais dessa lógica
        if key in self.visual_to_logical:
            logic = self.visual_to_logical[key]
            for visual, logic_key in self.visual_to_logical.items():
                if logic_key == logic:
                    self.pressed_keys.add(visual)
                    self._update_button_style(visual, True)
            self._update_counter()
            if len(self.pressed_keys) == len(self.key_buttons):
                self.complete_button.config(state=tk.NORMAL)
            return
        if key in self.key_buttons and key not in self.pressed_keys:
            self.pressed_keys.add(key)
            self._update_button_style(key, True)
            self._update_counter()
            if len(self.pressed_keys) == len(self.key_buttons):
                self.complete_button.config(state=tk.NORMAL)

    def _on_key_press(self, key):
        """Manipulador de evento de tecla pressionada."""
        if not self.is_running or not self.window:
            return
        try:
            key_str = self._get_key_string(key)
            # Se for uma tecla lógica de modificadora, marca todos os botões visuais dela
            if key_str in ['Shift', 'Ctrl', 'Alt', 'Win']:
                for visual, logic_key in self.visual_to_logical.items():
                    if logic_key == key_str:
                        self.pressed_keys.add(visual)
                        self.window.after(0, lambda k=visual: self._update_button_style(k, True))
                self.window.after(0, self._update_counter)
                if len(self.pressed_keys) == len(self.key_buttons):
                    self.window.after(0, lambda: self.complete_button.config(state=tk.NORMAL))
                return
            if key_str and key_str in self.key_buttons:
                self.pressed_keys.add(key_str)
                self.window.after(0, lambda k=key_str: self._update_button_style(k, True))
            self.window.after(0, self._update_counter)
            if len(self.pressed_keys) == len(self.key_buttons):
                self.window.after(0, lambda: self.complete_button.config(state=tk.NORMAL))
        except Exception as e:
            print(f"Erro ao processar tecla pressionada: {e}")

    def _on_key_release(self, key):
        """Manipulador de evento de tecla liberada."""
        pass

    def _get_key_string(self, key):
        """Converte uma tecla para string."""
        try:
            if hasattr(key, 'name'):
                if key.name == 'space':
                    return 'Space'
                elif key.name in ('shift', 'shift_l', 'shift_r'):
                    return 'Shift'
                elif key.name in ('ctrl', 'ctrl_l', 'ctrl_r'):
                    return 'Ctrl'
                elif key.name in ('alt', 'alt_l', 'alt_r'):
                    return 'Alt'
                elif key.name in ('cmd', 'cmd_l', 'cmd_r', 'win'):
                    return 'Win'
                elif key.name == 'esc':
                    return 'Esc'
                elif key.name in ('menu',):
                    return "Menu"
                elif key.name == 'tab':
                    return 'Tab'
                elif key.name == 'caps_lock':
                    return 'Caps Lock'
                elif key.name == 'enter':
                    return 'Enter'
                elif key.name == 'backspace':
                    return 'Backspace'
                elif key.name == 'delete':
                    return 'Delete'
                elif key.name == 'insert':
                    return 'Insert'
                elif key.name == 'home':
                    return 'Home'
                elif key.name == 'end':
                    return 'End'
                elif key.name == 'page_up':
                    return 'PgUp'
                elif key.name == 'page_down':
                    return 'PgDn'
                elif key.name == 'print_screen':
                    return 'PrtSc'
                elif key.name == 'scroll_lock':
                    return 'ScrLk'
                elif key.name == 'pause':
                    return 'Pause'
                elif key.name == 'up':
                    return '↑'
                elif key.name == 'down':
                    return '↓'
                elif key.name == 'left':
                    return '←'
                elif key.name == 'right':
                    return '→'
                elif key.name.startswith('f') and key.name[1:].isdigit():
                    return key.name.upper()
                else:
                    return None
            char = key.char
            if char:
                if char == '`' or char == '~':
                    return '`'
                elif char == '1' or char == '!':
                    return '1'
                elif char == '2' or char == '@':
                    return '2'
                elif char == '3' or char == '#':
                    return '3'
                elif char == '4' or char == '$':
                    return '4'
                elif char == '5' or char == '%':
                    return '5'
                elif char == '6' or char == '¨':
                    return '6'
                elif char == '7' or char == '&':
                    return '7'
                elif char == '8' or char == '*':
                    return '8'
                elif char == '9' or char == '(':
                    return '9'
                elif char == '0' or char == ')':
                    return '0'
                elif char == '-' or char == '_':
                    return '-'
                elif char == '=' or char == '+':
                    return '='
                elif char == '[' or char == '{':
                    return '['
                elif char == ']' or char == '}':
                    return ']'
                elif char == '\\' or char == '|':
                    return '\\'
                elif char == ';' or char == ':':
                    return ';'
                elif char == '\'' or char == '"':
                    return '\''
                elif char == ',' or char == '<':
                    return ','
                elif char == '.' or char == '>':
                    return '.'
                elif char == '/' or char == '?':
                    return '/'
                elif char.upper() == 'Ç':
                    return 'Ç'
                else:
                    return char.upper()
        except:
            return None

    def _update_button_style(self, key, pressed):
        """Atualiza o estilo do botão."""
        if key in self.key_buttons:
            button = self.key_buttons[key]
            if pressed:
                button.configure(style='Success.TButton')
            else:
                button.configure(style='TButton')

    def _update_counter(self):
        """Atualiza o contador de teclas pressionadas e habilita o botão de concluir se >= 70."""
        total_pressionadas = len(self.pressed_keys)
        total_teclas = len(self.key_buttons)
        self.counter_var.set(f"{total_pressionadas} de {total_teclas} teclas pressionadas")
        # Habilita o botão se 70 ou mais teclas forem pressionadas
        if total_pressionadas >= 70:
            self.complete_button.config(state=tk.NORMAL)
        else:
            self.complete_button.config(state=tk.DISABLED)

    def _skip_test(self):
        """Pula o teste."""
        if messagebox.askyesno(
            "Pular Teste",
            "Tem certeza que deseja pular o teste de teclado?\n\n"
            "O teste será marcado como não concluído."
        ):
            self.result['success'] = False
            self.result['message'] = "Teste pulado pelo usuário"
            self.is_completed = False
            self.window.destroy()
            if self.on_complete_callback:
                self.on_complete_callback(
                    "keyboard",
                    self.result,
                    self.get_formatted_result()
                )

    def _complete_test(self):
        """Conclui o teste."""
        self.result['success'] = True  
        self.result['message'] = "Teste concluído com sucesso"
        self.result['details'] = {
            'total_keys': len(self.key_buttons),
            'pressed_keys': len(self.pressed_keys)
        }
        self.is_completed = True
        self.window.destroy()
        if self.on_complete_callback:
            self.on_complete_callback(
                "keyboard",
                self.result,
                self.get_formatted_result()
            )

    def _on_close(self):
        """Manipulador de evento de fechamento da janela."""
        if messagebox.askyesno(
            "Fechar Teste",
            "Tem certeza que deseja fechar o teste de teclado?\n\n"
            "O teste será marcado como não concluído."
        ):
            self.result['success'] = False
            self.result['message'] = "Teste interrompido pelo usuário"
            self.is_completed = False
            self.window.destroy()
            if self.on_complete_callback:
                self.on_complete_callback(
                    "keyboard",
                    self.result,
                    self.get_formatted_result()
                )

    def get_result(self):
        """Retorna o resultado do teste."""
        return self.result

    def get_formatted_result(self):
        """Retorna o resultado formatado do teste."""
        if self.result['success']:
            return (
                f"Teste de Teclado: SUCESSO\n"
                f"Total de teclas no teclado: {self.result['details'].get('total_keys', 0)}\n"
                f"Teclas pressionadas: {self.result['details'].get('pressed_keys', 0)}"
            )
        else:
            if self.result['error']:
                return f"Teste de Teclado: FALHA\nErro: {self.result['error']}"
            else:
                return f"Teste de Teclado: FALHA\nMotivo: {self.result['message']}"

    def cleanup(self):
        """Limpa os recursos utilizados pelo teste."""
        if self.listener:
            self.listener.stop()
        self.is_running = False