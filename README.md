# Diagnóstico de Hardware para Windows

## Descrição
Ferramenta completa para diagnóstico de hardware em sistemas Windows. Realiza testes de funcionalidade de diversos componentes do computador e gera relatórios detalhados.

## Características
- ✅ **Interface gráfica intuitiva** com abas organizadas
- ✅ **Detecção automática de hardware** usando APIs nativas do Windows
- ✅ **Testes interativos** para validação de funcionalidade
- ✅ **Relatórios em HTML** com formatação profissional
- ✅ **Executável standalone** sem necessidade de instalação do Python
- ✅ **Compatível com Windows 10/11**

## Requisitos do Sistema
- **Sistema Operacional:** Windows 10 ou superior
- **Privilégios:** Administrador (recomendado para todos os testes)
- **Hardware:** Webcam, microfone e alto-falantes (para testes específicos)

## Instalação e Execução

### Opção 1: Executável Pré-compilado
1. Baixe o arquivo `DiagnosticoHardware.exe`
2. Execute como administrador
3. Aceite as solicitações de privilégios quando necessário

### Opção 2: Execução via Python
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python main.py
```

### Opção 3: Compilar Executável
```bash
# Instalar PyInstaller
pip install pyinstaller

# Executar script de build
python build_exe.py
```

## Funcionalidades

### 📊 Informações de Hardware
- **Placa-mãe:** Fabricante, modelo, número de série
- **Processador:** Marca, modelo, especificações
- **Memória RAM:** Total, módulos instalados, velocidade
- **Discos:** Modelo, tamanho, tipo
- **Placa de vídeo:** Modelo, memória
- **Display:** Resolução, configurações
- **TPM:** Status do Trusted Platform Module
- **Conectividade:** Bluetooth, Wi-Fi

### 🔧 Testes Disponíveis

#### 1. Teste de Bluetooth
- Detecta adaptadores Bluetooth
- Verifica status e funcionalidade
- Lista dispositivos pareados

#### 2. Teste de Teclado
- Teste interativo de todas as teclas
- Detecção de teclas pressionadas em tempo real
- Validação de teclas especiais e combinações

#### 3. Teste de TPM
- Verifica presença do Trusted Platform Module
- Status de ativação
- Versão do TPM

#### 4. Teste de USB
- Lista todos os dispositivos USB conectados
- Informações detalhadas de cada dispositivo
- Status de funcionamento

#### 5. Teste de Webcam
- Captura de vídeo em tempo real
- Teste de resolução
- Captura de imagens de teste

#### 6. Teste de Wi-Fi
- Detecta adaptadores de rede sem fio
- Status de conexão
- Informações da rede conectada

#### 7. Teste de Áudio
- Teste de reprodução de som
- Teste de gravação de áudio
- Verificação de dispositivos de entrada e saída

### 📋 Relatórios
- **Formato HTML:** Relatórios profissionais com CSS
- **Exportação de texto:** Resultados em formato simples
- **Salvamento automático:** Na pasta Documentos do usuário
- **Timestamp:** Data e hora de cada teste

## Estrutura do Projeto

```
windows_version/
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências Python
├── build_exe.py           # Script para gerar executável
├── README.md              # Esta documentação
├── core/                  # Módulos principais
│   ├── __init__.py
│   ├── hardware_info.py   # Coleta de informações de hardware
│   └── report_generator.py # Geração de relatórios
├── gui/                   # Interface gráfica
│   ├── __init__.py
│   └── main_window.py     # Janela principal
└── tests/                 # Módulos de teste
    ├── __init__.py
    ├── audio_test.py       # Teste de áudio
    ├── bluetooth_test.py   # Teste de Bluetooth
    ├── keyboard_test.py    # Teste de teclado
    ├── tpm_test.py        # Teste de TPM
    ├── usb_test.py        # Teste de USB
    ├── webcam_test.py     # Teste de webcam
    └── wifi_test.py       # Teste de Wi-Fi
```

## Como Usar

### 1. Iniciar a Aplicação
- Execute `DiagnosticoHardware.exe` como administrador
- A aplicação verificará automaticamente as dependências
- Aceite as solicitações de privilégios quando necessário

### 2. Visualizar Hardware
- Acesse a aba **"Hardware"**
- Clique em **"Atualizar Informações"** se necessário
- Visualize informações detalhadas de todos os componentes

### 3. Executar Testes
- **Testes individuais:** Aba "Testes" → Clique em "Executar" para cada teste
- **Todos os testes:** Clique em "Executar Todos os Testes"
- **Interação:** Alguns testes requerem interação do usuário

### 4. Visualizar Resultados
- Acesse a aba **"Resultados"**
- Visualize resultados detalhados de cada teste
- Use **"Salvar Resultados"** para exportar

### 5. Gerar Relatório
- Clique em **"Gerar Relatório"**
- Relatório HTML será criado na pasta Documentos
- Abra automaticamente no navegador padrão

## Dependências

### Obrigatórias
- `tkinter` - Interface gráfica (incluído no Python)
- `Pillow` - Processamento de imagens
- `opencv-python` - Captura de vídeo
- `pyaudio` - Processamento de áudio
- `pynput` - Captura de eventos de teclado
- `numpy` - Computação numérica

### Opcionais (mas recomendadas)
- `psutil` - Informações detalhadas do sistema
- `py-cpuinfo` - Informações do processador
- `WMI` - Acesso ao Windows Management Instrumentation

### Para Desenvolvimento
- `pyinstaller` - Geração de executável

## Solução de Problemas

### ❌ Erro de Privilégios
**Problema:** Alguns testes falham por falta de privilégios
**Solução:** Execute como administrador

### ❌ Webcam Não Detectada
**Problema:** Teste de webcam falha
**Soluções:**
- Verifique se a webcam está conectada
- Feche outros programas que usam a webcam
- Atualize os drivers da webcam

### ❌ Áudio Não Funciona
**Problema:** Teste de áudio falha
**Soluções:**
- Verifique se os dispositivos de áudio estão funcionando
- Teste com outros programas primeiro
- Verifique o volume do sistema
- Reinstale os drivers de áudio

### ❌ Informações Incompletas
**Problema:** Algumas informações de hardware não aparecem
**Soluções:**
- Execute como administrador
- Atualize drivers do sistema
- Alguns componentes podem não ser detectados em VMs

### ❌ Dependências Faltantes
**Problema:** Erro ao executar por falta de bibliotecas
**Solução:** 
```bash
pip install -r requirements.txt
```

## Limitações

- **Máquinas Virtuais:** Alguns componentes podem não ser detectados corretamente
- **Hardware Antigo:** Componentes muito antigos podem ter detecção limitada
- **Drivers:** Informações dependem dos drivers instalados
- **Privilégios:** Alguns testes requerem acesso administrativo

## Desenvolvimento

### Estrutura de Código
- **Modular:** Cada teste é um módulo independente
- **Orientado a Objetos:** Classes para cada funcionalidade
- **Thread-safe:** Interface não trava durante testes
- **Tratamento de Erros:** Captura e exibe erros de forma amigável

### Adicionando Novos Testes
1. Crie um novo arquivo em `tests/`
2. Implemente a classe com métodos `initialize()`, `execute()`, `get_result()`
3. Adicione à lista de testes em `main_window.py`
4. Atualize a documentação

### Compilação
O script `build_exe.py` automatiza todo o processo:
- Verifica dependências
- Cria arquivos de configuração
- Compila com PyInstaller
- Gera instalador e documentação

## Versão
**1.0** - Versão para Windows 

## Licença
© 2024 - Ferramenta de Diagnóstico de Hardware
Davi Santos
Analista Tecnico 
---

## Suporte

Esta ferramenta é destinada a diagnósticos básicos e identificação de problemas.

