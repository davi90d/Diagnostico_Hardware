"""
Módulo para geração de relatórios.
Implementa a geração de relatórios detalhados com informações de hardware e resultados dos testes.
"""

import os
import sys
import time
from datetime import datetime
import platform

class ReportGenerator:
    """Classe para geração de relatórios."""
    
    def __init__(self):
        """Inicializa o gerador de relatórios."""
        self.hardware_info = {}
        self.identification = {}
        self.test_results = {}
        self.test_details = {}
        self.output_directory = None  # Diretório de saída padrão
    
    def set_hardware_info(self, hardware_info):
        """Define as informações de hardware."""
        self.hardware_info = hardware_info
    
    def set_identification(self, identification):
        """Define as informações de identificação."""
        self.identification = identification
    
    def add_test_result(self, test_name, result, formatted_result):
        """Adiciona o resultado de um teste."""
        self.test_results[test_name] = result
        self.test_details[test_name] = formatted_result
    
    def set_output_directory(self, output_directory):
        """Define o diretório de saída para os relatórios."""
        self.output_directory = output_directory
    
    def generate_report(self):
        """Gera o relatório."""
        try:
            # Define o nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = self.output_directory or os.path.join(os.path.expanduser("~"), "Diagnostico_Hardware_Reports")
            
            # Cria o diretório se não existir
            os.makedirs(report_dir, exist_ok=True)
            
            # Define o caminho completo do arquivo
            report_path = os.path.join(report_dir, f"relatorio_{timestamp}.txt")
            
            # Gera o conteúdo do relatório
            content = self._generate_report_content()
            
            # Escreve o relatório no arquivo
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return report_path
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {e}")
    
    def _generate_report_content(self):
        """Gera o conteúdo do relatório."""
        content = []
        
        # Cabeçalho
        content.append("=" * 80)
        content.append("RELATÓRIO DE DIAGNÓSTICO DE HARDWARE")
        content.append("=" * 80)
        content.append("")
        
        # Informações de identificação
        content.append("-" * 80)
        content.append("INFORMAÇÕES DE IDENTIFICAÇÃO")
        content.append("-" * 80)
        
        if self.identification:
            content.append(f"Data e Hora: {self.identification.get('date_time', 'Não disponível')}")
            content.append(f"Nome do Técnico: {self.identification.get('technician_name', 'Não disponível')}")
            content.append(f"ID da Bancada: {self.identification.get('workbench_id', 'Não disponível')}")
        else:
            content.append("Informações de identificação não disponíveis")
        
        content.append("")
        
        # Informações do sistema
        content.append("-" * 80)
        content.append("INFORMAÇÕES DO SISTEMA")
        content.append("-" * 80)
        
        content.append(f"Sistema Operacional: {platform.system()} {platform.release()} {platform.version()}")
        content.append(f"Arquitetura: {platform.machine()}")
        content.append(f"Nome do Computador: {platform.node()}")
        
        content.append("")
        
        # Informações de hardware
        content.append("-" * 80)
        content.append("INFORMAÇÕES DE HARDWARE")
        content.append("-" * 80)
        
        if self.hardware_info:
            # Placa-mãe
            if 'motherboard' in self.hardware_info:
                content.append("Placa-Mãe:")
                content.append(f"  Fabricante: {self.hardware_info['motherboard'].get('manufacturer', 'Não disponível')}")
                content.append(f"  Modelo: {self.hardware_info['motherboard'].get('model', 'Não disponível')}")
                content.append(f"  Número de Série: {self.hardware_info['motherboard'].get('serial_number', 'Não disponível')}")
                content.append("")
            
            # Processador
            if 'cpu' in self.hardware_info:
                content.append("Processador:")
                content.append(f"  Marca: {self.hardware_info['cpu'].get('brand', 'Não disponível')}")
                content.append(f"  Modelo: {self.hardware_info['cpu'].get('model', 'Não disponível')}")
                content.append("")
            
            # Memória RAM
            if 'ram' in self.hardware_info:
                content.append("Memória RAM:")
                
                total = self.hardware_info['ram'].get('total', 'Não disponivel')
                content.append(f"  Total: {total}")

                modules = self.hardware_info['ram'].get('modules',[])
                if modules:
                    for i, module in enumerate(modules, 1):
                        bank_label = module.get('banklabel', f'BANK {i}')
                        size = module.get('size', 'N/A GB')
                        speed = module.get('speed', 'N/A MHz')
                        content.append(f"{bank_label} : {size} {speed}")
                else:
                    content.append(" Não foi possivel obter informações da memória")
                content.append("")

            #Discos
            if 'disks' in self.hardware_info and self.hardware_info['disks']:
                content.append("Discos:")
                for i, disk in enumerate(self.hardware_info['disks'], 1):
                    if isinstance(disk, dict):
                        content.append(f"   Disco{i}: {disk.get('model', 'N/A')} - {disk.get('size', 'N/A')}")
                    else:
                        content.append(f"   Disco {i}: {disk}")
                content.append("")

            #GPU
            if 'gpu' in self.hardware_info and self.hardware_info['gpu']:
                content.append("Placas de Vídeo:")
                for i, gpu in enumerate(self.hardware_info['gpu'], 1):
                    if isinstance(gpu, dict):
                        content.append(f"  GPU {i}: {gpu.get('model', 'N/A')}")
                    else:
                        content.append(f"  GPU{i}: {gpu}")
                content.append("")
                

            
            # Display
            if 'display' in self.hardware_info:
                content.append("Display:")
                content.append(f"  Resolução: {self.hardware_info['display'].get('resolution', 'Não disponível')}")
                content.append("")
            
            # TPM
            if 'tpm' in self.hardware_info:
                content.append("TPM:")
                content.append(f"  Versão: {self.hardware_info['tpm'].get('version', 'Não disponível')}")
                content.append(f"  Status: {self.hardware_info['tpm'].get('status', 'Não disponível')}")
                content.append(f"  Fabricante: {self.hardware_info['tpm'].get('manufacturer', 'Não disponível')}")
                content.append("")
            
            # Bluetooth
            if 'bluetooth' in self.hardware_info:
                content.append("Bluetooth:")
                content.append(f"  Dispositivo: {self.hardware_info['bluetooth'].get('device_name', 'Não disponível')}")
                content.append(f"  Status: {self.hardware_info['bluetooth'].get('device_status', 'Não disponível')}")
                content.append("")
            
            # Wi-Fi
            if 'wifi' in self.hardware_info:
                content.append("Wi-Fi:")
                content.append(f"  Adaptador: {self.hardware_info['wifi'].get('adapter_name', 'Não disponível')}")
                content.append(f"  Status: {self.hardware_info['wifi'].get('adapter_status', 'Não disponível')}")
                content.append(f"  SSID: {self.hardware_info['wifi'].get('connected_ssid', 'Não disponível')}")
                content.append("")
        else:
            content.append("Informações de hardware não disponíveis")
            content.append("")
        
        # Resultados dos testes
        content.append("-" * 80)
        content.append("RESULTADOS DOS TESTES")
        content.append("-" * 80)
        
        if self.test_details:
            for test_name, test_detail in self.test_details.items():
                content.append(test_detail)
                content.append("")
        else:
            content.append("Nenhum teste foi executado")
            content.append("")
        
        # Resumo
        content.append("-" * 80)
        content.append("RESUMO DOS TESTES")
        content.append("-" * 80)
        
        if self.test_results:
            total_tests = len(self.test_results)
            successful_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
            
            content.append(f"Total de Testes: {total_tests}")
            content.append(f"Testes com Sucesso: {successful_tests}")
            content.append(f"Testes com Falha: {total_tests - successful_tests}")
            
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            content.append(f"Taxa de Sucesso: {success_rate:.2f}%")
        else:
            content.append("Nenhum teste foi executado")
        
        content.append("")
        content.append("=" * 80)
        content.append("FIM DO RELATÓRIO")
        content.append("=" * 80)
        
        return "\n".join(content)
