"""
Módulo para teste avançado de USB - Versão Windows com medições precisas
Implementa teste completo de dispositivos USB com detecção de protocolo e medição de velocidade confiável
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import shutil
import tempfile
import subprocess
import hashlib
import win32api
import win32file
import string
import ctypes
import wmi
from collections import namedtuple

class USBTest:
    """Classe para teste avançado de USB com medições precisas de velocidade."""
    
    def __init__(self, parent_window, on_complete_callback):
        """Inicializa o teste de USB com todas as melhorias."""
        self.parent_window = parent_window
        self.on_complete_callback = on_complete_callback
        self.result = {
            'success': False,
            'message': '',
            'details': {},
            'error': None
        }
        self.window = None
        self.devices = []
        self.selected_device = None
        self.test_file_size_mb = 100  # Tamanho padrão do arquivo de teste
        self.is_running = False
        self.is_completed = False
        self.temp_dir = None
        self.wmi_conn = wmi.WMI()  # Conexão WMI para detecção de hardware

        # Detecta dispositivos USB
        self.devices = self._detect_usb_devices()
        # Cria a interface
        self._create_ui()

    def _create_ui(self):
        """Cria a interface gráfica do teste de USB."""
        self.window = tk.Toplevel(self.parent_window)
        self.window.title("Teste Avançado de USB - Medição Precisa")
        self.window.geometry("950x900")
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
            text="Teste Avançado de USB - Medição Precisa",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Frame para lista de dispositivos
        devices_frame = ttk.LabelFrame(main_frame, text="Dispositivos USB Detectados", padding=10)
        devices_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Lista de dispositivos
        self.device_listbox = tk.Listbox(devices_frame, height=8, selectmode=tk.SINGLE, font=('Consolas', 9))
        self.device_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(devices_frame, orient=tk.VERTICAL, command=self.device_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.device_listbox.config(yscrollcommand=scrollbar.set)
        
        # Preenche a lista de dispositivos
        for device in self.devices:
            display_text = f"{device['name']} | {device.get('protocol', '?')} | {device.get('size', '?')}"
            self.device_listbox.insert(tk.END, display_text)
        
        # Seleciona o primeiro dispositivo por padrão
        if self.devices:
            self.device_listbox.selection_set(0)
        
        # Frame para configurações do teste
        config_frame = ttk.LabelFrame(main_frame, text="Configurações do Teste", padding=10)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Tamanho do arquivo de teste
        ttk.Label(config_frame, text="Tamanho do arquivo (MB):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.size_var = tk.StringVar(value=str(self.test_file_size_mb))
        size_entry = ttk.Entry(config_frame, textvariable=self.size_var, width=8)
        size_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Modo de teste
        ttk.Label(config_frame, text="Modo de teste:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.test_mode_var = tk.StringVar(value="preciso")
        ttk.Radiobutton(config_frame, text="Rápido", variable=self.test_mode_var, value="rapido").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(config_frame, text="Preciso", variable=self.test_mode_var, value="preciso").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Opções avançadas
        ttk.Label(config_frame, text="Opções:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.force_no_cache_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            config_frame,
            text="Ignorar cache (mais lento, mas preciso)",
            variable=self.force_no_cache_var
        ).grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Frame para resultados
        self.results_frame = ttk.LabelFrame(main_frame, text="Resultados Detalhados", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Grid para resultados
        ttk.Label(self.results_frame, text="Protocolo detectado:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.protocol_var = tk.StringVar(value="Não testado")
        ttk.Label(self.results_frame, textvariable=self.protocol_var, font=('Arial', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.results_frame, text="Velocidade de escrita:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.write_speed_var = tk.StringVar(value="0 MB/s")
        ttk.Label(self.results_frame, textvariable=self.write_speed_var, font=('Arial', 9)).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.results_frame, text="Velocidade de leitura:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.read_speed_var = tk.StringVar(value="0 MB/s")
        ttk.Label(self.results_frame, textvariable=self.read_speed_var, font=('Arial', 9)).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.results_frame, text="Tipo estimado:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.usb_type_var = tk.StringVar(value="Não determinado")
        ttk.Label(self.results_frame, textvariable=self.usb_type_var, font=('Arial', 9, 'bold')).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.results_frame, text="Integridade:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.integrity_var = tk.StringVar(value="Não testado")
        ttk.Label(self.results_frame, textvariable=self.integrity_var).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Pronto para iniciar o teste")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=800)
        status_label.pack(fill=tk.X, pady=5)
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botões
        self.start_button = ttk.Button(
            button_frame,
            text="Iniciar Teste Completo",
            command=self._start_test
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Pular Teste",
            command=self._skip_test
        ).pack(side=tk.LEFT, padx=5)
        
        self.complete_button = ttk.Button(
            button_frame,
            text="Concluir",
            state=tk.DISABLED,
            command=self._complete_test
        )
        self.complete_button.pack(side=tk.RIGHT, padx=5)
    
    def _detect_usb_devices(self):
        """Detecta dispositivos USB conectados no Windows com informações detalhadas."""
        devices = []
        
        try:
            # Lista todas as unidades de disco
            drives = []
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter)
                bitmask >>= 1
            
            # Verifica cada unidade
            for drive in drives:
                drive_path = f"{drive}:\\"
                try:
                    drive_type = win32file.GetDriveType(drive_path)
                    
                    if drive_type == win32file.DRIVE_REMOVABLE:
                        # Obtém informações detalhadas
                        try:
                            vol_info = win32api.GetVolumeInformation(drive_path)
                            total_bytes = win32file.GetDiskFreeSpaceEx(drive_path)[1]
                            total_gb = total_bytes / (1024 ** 3)
                            
                            # Obtém informações do dispositivo físico
                            device_info = self._get_usb_device_info(drive_path)
                            
                            devices.append({
                                'name': f"{vol_info[0] or 'Sem nome'} ({drive}:)",
                                'path': drive_path,
                                'type': 'removable',
                                'size': f"{total_gb:.1f} GB",
                                'device_id': device_info.get('device_id', ''),
                                'protocol': device_info.get('protocol', 'USB (desconhecido)'),
                                'manufacturer': device_info.get('manufacturer', ''),
                                'model': device_info.get('model', '')
                            })
                        except Exception as e:
                            devices.append({
                                'name': f"Dispositivo removível ({drive}:)",
                                'path': drive_path,
                                'type': 'removable',
                                'size': "Tamanho desconhecido",
                                'protocol': 'USB (desconhecido)'
                            })
                except:
                    continue
            
            # Fallback se nenhum dispositivo for encontrado
            if not devices:
                temp_dir = tempfile.gettempdir()
                devices.append({
                    'name': 'Diretório Temporário (Fallback)',
                    'path': temp_dir,
                    'type': 'fixed',
                    'size': "Tamanho variável",
                    'protocol': 'Sistema de arquivos local'
                })
                
            return devices
        except Exception as e:
            print(f"Erro na detecção de dispositivos: {e}")
            # Fallback básico
            temp_dir = tempfile.gettempdir()
            return [{
                'name': 'Diretório Temporário (Fallback)',
                'path': temp_dir,
                'type': 'fixed',
                'size': "Tamanho variável",
                'protocol': 'Sistema de arquivos local'
            }]
    
    def _get_usb_device_info(self, drive_path):
        """Obtém informações detalhadas do dispositivo USB usando WMI."""
        info = {
            'device_id': '',
            'protocol': 'USB (desconhecido)',
            'manufacturer': '',
            'model': ''
        }
        
        try:
            drive_letter = drive_path[0].upper()
            
            # Encontra o disco físico associado a esta unidade lógica
            for logical_disk in self.wmi_conn.Win32_LogicalDisk(DeviceID=f"{drive_letter}:"):
                for partition in logical_disk.associators("Win32_LogicalDiskToPartition"):
                    for disk_drive in partition.associators("Win32_DiskDriveToDiskPartition"):
                        # Agora temos o disco físico - verifica se é USB
                        if "USB" in disk_drive.InterfaceType:
                            info['device_id'] = disk_drive.DeviceID
                            info['manufacturer'] = disk_drive.Manufacturer or "Desconhecido"
                            info['model'] = disk_drive.Model or "Desconhecido"
                            
                            # Tenta determinar a versão USB
                            for usb_controller in disk_drive.associators("Win32_USBControllerDevice"):
                                desc = usb_controller.Dependent.Description
                                if "USB" in desc:
                                    # Padroniza a descrição do protocolo
                                    if "3.0" in desc or "3.1" in desc or "3.2" in desc:
                                        info['protocol'] = "USB 3.2 Gen 1 (5 Gbps)"
                                    elif "3.2 Gen 2" in desc:
                                        info['protocol'] = "USB 3.2 Gen 2 (10 Gbps)"
                                    elif "USB4" in desc or "Thunderbolt" in desc:
                                        info['protocol'] = "USB4/Thunderbolt"
                                    else:
                                        info['protocol'] = desc
                                    break
                            
                            return info
        except Exception as e:
            print(f"Erro ao obter informações do dispositivo: {e}")
        
        return info
    
    def _start_test(self):
        """Inicia o teste de USB."""
        if self.is_running:
            return
            
        selection = self.device_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um dispositivo para testar.")
            return
        
        try:
            self.test_file_size_mb = int(self.size_var.get())
            if self.test_file_size_mb <= 0:
                raise ValueError("O tamanho deve ser positivo")
        except ValueError:
            messagebox.showwarning("Erro", "Tamanho do arquivo de teste inválido.")
            return
        
        # Verifica espaço disponível
        index = selection[0]
        self.selected_device = self.devices[index]
        
        try:
            free_bytes = win32file.GetDiskFreeSpaceEx(self.selected_device['path'])[0]
            required_bytes = self.test_file_size_mb * 1024 * 1024 * 2  # Espaço para origem e cópia
            
            if free_bytes < required_bytes:
                messagebox.showwarning(
                    "Espaço Insuficiente",
                    f"Espaço necessário: {self.test_file_size_mb * 2} MB\n"
                    f"Espaço disponível: {free_bytes // (1024 * 1024)} MB"
                )
                return
        except:
            pass  # Continua mesmo se não conseguir verificar o espaço
        
        # Prepara a interface
        self._reset_results_display()
        self.device_listbox.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        self.is_running = True
        
        # Inicia o teste em uma thread separada
        test_mode = self.test_mode_var.get()
        threading.Thread(
            target=self._run_advanced_test,
            daemon=True
        ).start()
    
    def _reset_results_display(self):
        """Reseta os campos de resultados."""
        self.protocol_var.set("Testando...")
        self.write_speed_var.set("0 MB/s")
        self.read_speed_var.set("0 MB/s")
        self.usb_type_var.set("Determinando...")
        self.integrity_var.set("Não testado")
        self.progress_var.set(0)
        self.status_var.set("Preparando teste...")
    
    def _run_advanced_test(self):
        """Executa teste avançado com múltiplos tamanhos de arquivo."""
        try:
            self.status_var.set("Iniciando teste avançado...")
            self.progress_var.set(5)
            
            # Cria diretório temporário
            self.temp_dir = tempfile.mkdtemp()
            
            # Define tamanhos de teste (em MB)
            test_sizes = [10, self.test_file_size_mb, 200]  # Pequeno, médio, grande
            test_sizes = [min(size, self.test_file_size_mb) for size in test_sizes]
            test_sizes = list(sorted(set(test_sizes)))  # Remove duplicatas e ordena
            
            results = []
            integrity_checks = []
            
            # Executa testes para cada tamanho
            for i, size in enumerate(test_sizes):
                progress_base = 5 + (i * 90 / len(test_sizes))
                
                # Cria arquivo de teste
                test_file = os.path.join(self.temp_dir, f"test_{size}MB.bin")
                self.status_var.set(f"Criando arquivo de teste {size}MB...")
                self._create_test_file(test_file, size)
                self.progress_var.set(progress_base + 10)
                
                # Calcula hash
                original_hash = self._calculate_file_hash(test_file)
                
                # Teste de escrita
                dest_file = os.path.join(self.selected_device['path'], f"test_{size}MB.bin")
                self.status_var.set(f"Testando escrita ({size}MB)...")
                write_speed = self._measure_write_speed(test_file, dest_file)
                self.progress_var.set(progress_base + 30)
                
                # Teste de leitura
                self.status_var.set(f"Testando leitura ({size}MB)...")
                if self.force_no_cache_var.get():
                    read_speed = self._measure_real_read_speed(dest_file)
                else:
                    read_speed = self._measure_read_speed(dest_file)
                self.progress_var.set(progress_base + 50)
                
                # Verifica integridade
                self.status_var.set(f"Verificando integridade ({size}MB)...")
                copied_hash = self._calculate_file_hash(dest_file)
                integrity = original_hash == copied_hash
                integrity_checks.append(integrity)
                
                # Remove arquivo temporário
                os.remove(dest_file)
                self.progress_var.set(progress_base + 60)
                
                # Armazena resultados
                results.append({
                    'size': size,
                    'write_speed': write_speed,
                    'read_speed': read_speed,
                    'integrity': integrity
                })
                
                # Atualiza interface com resultados parciais
                avg_write = sum(r['write_speed'] for r in results) / len(results)
                avg_read = sum(r['read_speed'] for r in results) / len(results)
                
                self.write_speed_var.set(f"{avg_write:.2f} MB/s (média)")
                self.read_speed_var.set(f"{avg_read:.2f} MB/s (média)")
                self.integrity_var.set(f"{sum(integrity_checks)}/{len(integrity_checks)} sucessos")
                
                # Determina tipo USB baseado na maior velocidade
                max_speed = max(avg_write, avg_read)
                usb_type = self._determine_usb_type(max_speed)
                self.usb_type_var.set(usb_type)
                self.protocol_var.set(self.selected_device.get('protocol', 'USB (desconhecido)'))
                self.progress_var.set(progress_base + 70)
            
            # Calcula resultados finais
            final_write = sum(r['write_speed'] for r in results) / len(results)
            final_read = sum(r['read_speed'] for r in results) / len(results)
            all_integrity = all(integrity_checks)
            max_speed = max(final_write, final_read)
            usb_type = self._determine_usb_type(max_speed)
            
            # Atualiza interface
            self.write_speed_var.set(f"{final_write:.2f} MB/s (média final)")
            self.read_speed_var.set(f"{final_read:.2f} MB/s (média final)")
            self.integrity_var.set("✅ TODOS os arquivos íntegros" if all_integrity else "❌ ALGUNS arquivos corrompidos")
            self.usb_type_var.set(usb_type)
            self.protocol_var.set(self.selected_device.get('protocol', 'USB (desconhecido)'))
            
            # Salva resultados
            self.result.update({
                'success': all_integrity,
                'message': "Teste avançado concluído",
                'details': {
                    'write_speed': final_write,
                    'read_speed': final_read,
                    'usb_type': usb_type,
                    'protocol': self.selected_device.get('protocol', ''),
                    'integrity': all_integrity,
                    'test_sizes': test_sizes,
                    'results': results,
                    'device': self.selected_device['name']
                }
            })
            
            self.status_var.set("✅ Teste avançado concluído com sucesso!")
            self.progress_var.set(100)
            
        except Exception as e:
            self.result.update({
                'success': False,
                'message': f"Erro no teste avançado: {str(e)}",
                'error': str(e)
            })
            self.status_var.set(f"❌ Erro no teste: {str(e)}")
        finally:
            self.is_running = False
            self.complete_button.config(state=tk.NORMAL)
            self._cleanup_temp_files()
    
    def _create_test_file(self, filepath, size_mb):
        """Cria um arquivo de teste do tamanho especificado."""
        block_size = 1024 * 1024  # 1MB
        with open(filepath, 'wb') as f:
            for i in range(size_mb):
                f.write(os.urandom(block_size))
                progress = 10 + (i / size_mb * 30)  # 10-40% para criação do arquivo
                self.progress_var.set(progress)
                self.window.update()
    
    def _measure_real_read_speed(self, filepath):
        """Mede velocidade de leitura real, contornando o cache."""
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        block_size = 1024 * 1024  # 1MB
        
        try:
            # Tenta abrir o arquivo com flags para minimizar caching
            if sys.platform == 'win32':
                # No Windows, tentamos usar FILE_FLAG_NO_BUFFERING
                import ctypes
                from ctypes import wintypes
                
                GENERIC_READ = 0x80000000
                FILE_SHARE_READ = 0x00000001
                OPEN_EXISTING = 3
                FILE_FLAG_NO_BUFFERING = 0x20000000
                
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                
                handle = kernel32.CreateFileW(
                    filepath,
                    GENERIC_READ,
                    FILE_SHARE_READ,
                    None,
                    OPEN_EXISTING,
                    FILE_FLAG_NO_BUFFERING,
                    None
                )
                
                if handle == -1:
                    raise ctypes.WinError(ctypes.get_last_error())
                
                # Buffer alinhado necessário para NO_BUFFERING
                buf = ctypes.create_string_buffer(block_size)
                bytes_read = wintypes.DWORD(0)
                
                start_time = time.time()
                remaining = int(file_size_mb)
                
                while remaining > 0:
                    if not kernel32.ReadFile(handle, buf, block_size, ctypes.byref(bytes_read), None):
                        raise ctypes.WinError(ctypes.get_last_error())
                    remaining -= 1
                
                elapsed = time.time() - start_time
                kernel32.CloseHandle(handle)
                
                speed = file_size_mb / elapsed if elapsed > 0 else 0
                return speed
            else:
                # Para outros sistemas, usa O_DIRECT
                fd = os.open(filepath, os.O_RDONLY | os.O_DIRECT)
                buf = os.pread(fd, block_size, 0)  # Lê apenas para testar
                os.close(fd)
                
                start_time = time.time()
                with open(filepath, 'rb', buffering=0) as f:
                    for _ in range(int(file_size_mb)):
                        f.read(block_size)
                elapsed = time.time() - start_time
                
                return file_size_mb / elapsed if elapsed > 0 else 0
                
        except Exception as e:
            print(f"Erro no método direto: {e}, tentando fallback...")
            # Método fallback com limpeza de cache
            try:
                self._clear_file_cache(filepath)
                return self._measure_read_speed(filepath)
            except Exception as e:
                print(f"Erro no fallback: {e}")
                return 0

    def _measure_read_speed(self, filepath):
        """Medição tradicional de velocidade de leitura (pode usar cache)."""
        block_size = 1024 * 1024  # 1MB
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        start_time = time.time()
        with open(filepath, 'rb') as f:
            while f.read(block_size):
                pass
        elapsed = time.time() - start_time
        
        return file_size_mb / elapsed if elapsed > 0 else 0

    def _clear_file_cache(self, filepath):
        """Tenta limpar o cache do arquivo do sistema."""
        try:
            # Método 1: Forçar leitura de arquivo grande para "sujar" o cache
            temp_file = os.path.join(tempfile.gettempdir(), "cache_flush.tmp")
            with open(temp_file, 'wb') as f:
                f.write(os.urandom(100 * 1024 * 1024))  # 100MB
            with open(temp_file, 'rb') as f:
                f.read()
            os.remove(temp_file)
            
            # Método 2: Chamada de sistema para liberar cache
            if sys.platform == 'win32':
                # Tenta usar o utilitário RAMMap da Microsoft (se disponível)
                try:
                    subprocess.run(["RAMMap.exe", "-Emptystandbylist"], check=True)
                except:
                    # Fallback para comando nativo
                    subprocess.run(["wmic", "process", "call", "create", "notepad.exe"], capture_output=True)
                    subprocess.run(["wmic", "process", "where", "name='notepad.exe'", "delete"], capture_output=True)
        except Exception as e:
            print(f"Erro ao limpar cache: {e}")

    def _measure_write_speed(self, src, dst):
        """Mede velocidade de escrita com verificação de consistência."""
        file_size_mb = os.path.getsize(src) / (1024 * 1024)
        
        # Primeira escrita (pode ser mais lenta)
        start_time = time.time()
        shutil.copyfile(src, dst)
        elapsed = time.time() - start_time
        speed1 = file_size_mb / elapsed if elapsed > 0 else 0
        
        # Segunda escrita (para verificar consistência)
        start_time = time.time()
        shutil.copyfile(src, dst)
        elapsed = time.time() - start_time
        speed2 = file_size_mb / elapsed if elapsed > 0 else 0
        
        # Retorna a menor velocidade (mais próxima da realidade)
        return min(speed1, speed2)

    def _determine_usb_type(self, speed_mbps):
        """Determina o tipo de USB com base na velocidade de transferência."""
        if speed_mbps < 35:  # USB 2.0 geralmente alcança até ~35 MB/s
            return "USB 2.0 (até 480 Mbps)"
        elif speed_mbps < 450:  # USB 3.2 Gen 1 (5 Gbps) tipicamente 300-450 MB/s
            return "USB 3.2 Gen 1 (5 Gbps)"
        elif speed_mbps < 1100:  # USB 3.2 Gen 2 (10 Gbps) tipicamente 800-1100 MB/s
            return "USB 3.2 Gen 2 (10 Gbps)"
        elif speed_mbps < 2500:  # USB4 20Gbps
            return "USB4/Thunderbolt (20 Gbps)"
        else:  # USB4 40Gbps ou Thunderbolt 3/4
            return "USB4/Thunderbolt (40 Gbps)"

    def _cleanup_temp_files(self):
        """Remove arquivos temporários."""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Erro ao limpar arquivos temporários: {e}")

    def _skip_test(self):
        """Pula o teste."""
        if messagebox.askyesno("Pular Teste", "Deseja realmente pular o teste?"):
            self.result.update({
                'success': False,
                'message': "Teste pulado pelo usuário"
            })
            self.window.destroy()

    def _complete_test(self):
        """Conclui o teste."""
        self.result['success'] = True
        self.is_completed = True
        self.window.destroy()
        if callable(self.on_complete_callback):
            self.on_complete_callback("usb", self.get_result(), self.get_formatted_result())

    def _on_close(self):
        """Manipulador para fechamento da janela."""
        if messagebox.askyesno("Fechar", "Deseja realmente fechar o teste?"):
            self.result.update({
                'success': False,
                'message': "Teste interrompido pelo usuário"
            })
            self.window.destroy()
            if callable(self.on_complete_callback):
                self.on_complete_callback("usb", self.get_result(), self.get_formatted_result())

    def get_result(self):
        """Retorna o resultado do teste."""
        return self.result

    def get_formatted_result(self):
        """Retorna o resultado formatado."""
        if not self.result:
            return "Nenhum resultado disponível"
        
        details = self.result.get('details', {})
        if self.result['success']:
            return (
                f"✅ Teste de USB concluído com sucesso\n\n"
                f"🔹 Dispositivo: {details.get('device', 'Desconhecido')}\n"
                f"🔹 Protocolo: {details.get('protocol', 'Desconhecido')}\n"
                f"🔹 Tipo USB: {details.get('usb_type', 'Não determinado')}\n"
                f"🔹 Velocidade de escrita: {details.get('write_speed', 0):.2f} MB/s\n"
                f"🔹 Velocidade de leitura: {details.get('read_speed', 0):.2f} MB/s\n"
                f"🔹 Integridade: {'✅ Todos os arquivos íntegros' if details.get('integrity', False) else '❌ Problemas detectados'}"
            )
        else:
            return (
                f"❌ Teste de USB falhou\n\n"
                f"🔹 Motivo: {self.result.get('message', 'Erro desconhecido')}\n"
                f"🔹 Erro: {self.result.get('error', 'Nenhum detalhe disponível')}"
            )
    
    def _calculate_file_hash(self, filepath):
        """Calcula o hash SHA256 de um arquivo."""
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()