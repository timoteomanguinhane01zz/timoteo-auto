import re
import time
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Comunicação nativa com APIs do Android sem internet
from jnius import autoclass

Uri = autoclass('android.net.Uri')
Intent = autoclass('android.content.Intent')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

# --- GERENCIADOR DE VARIÁVEIS ---
class GestorVariaveis:
    def __init__(self):
        self.variaveis = {}

    def definir(self, chave, valor):
        self.variaveis[chave] = valor

    def obter(self, chave, valor_padrao=None):
        return self.variaveis.get(chave, valor_padrao)

    def processar_texto(self, texto):
        for chave, valor in self.variaveis.items():
            texto = texto.replace(f"{{{chave}}}", str(valor))
        return texto

# --- EXECUTADOR DE AÇÕES (USSD / LOOPS) ---
class ExecutadorAcoes:
    def __init__(self, gestor_var):
        self.var = gestor_var

    def disparar_ussd(self, codigo_ussd_template):
        codigo_final = self.var.processar_texto(codigo_ussd_template)
        encoded_ussd = Uri.encode(codigo_final)
        
        intent = Intent(Intent.ACTION_CALL)
        intent.setData(Uri.parse(f"tel:{encoded_ussd}"))
        
        contexto = PythonActivity.mActivity
        contexto.startActivity(intent)

    def executar_loop(self, vezes, acao_func, *args):
        for i in range(vezes):
            self.var.definir("loop_index", i + 1)
            acao_func(*args)
            time.sleep(1)

# --- MOTOR DE REGRAS (GATILHOS E CONDICIONAIS IF) ---
class MotorAutomacao:
    def __init__(self):
        self.gestor_var = GestorVariaveis()
        self.acoes = ExecutadorAcoes(self.gestor_var)

    def processar_comando(self, texto_comando):
        # Exemplo de comando esperado: ENVIAR:841234567:DIO-1GB
        padrao = r"ENVIAR:(8[4567][0-9]{7}):([A-Z0-9\.\-]+)"
        match = re.search(padrao, texto_comando)

        if match:
            self.gestor_var.definir("cliente_tel", match.group(1))
            self.gestor_var.definir("pacote_cod", match.group(2))
            self.avaliar_regras()

    def avaliar_regras(self):
        pacote = self.gestor_var.obter("pacote_cod")
        numero = self.gestor_var.obter("cliente_tel")

        # Estrutura IF / ELSE de decisão
        if pacote.startswith("DIO"):
            # Envio simples via USSD
            self.acoes.disparar_ussd(f"*150*{numero}*{pacote}#")
        else:
            # Exemplo de envio com repetição/loop se necessário
            self.acoes.executar_loop(1, self.acoes.disparar_ussd, f"*150*{numero}*{pacote}#")

# --- INTERFACE DA APLICAÇÃO ---
class TimoteoAutoApp(App):
    def build(self):
        self.motor = MotorAutomacao()
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.label_status = Label(text="TIMÓTEO AUTO 5G\nStatus: Servidor de Automação Ativo", font_size='18sp')
        
        btn_teste = Button(text="Testar Envio (Simulação)", size_hint=(1, 0.3))
        btn_teste.bind(on_press=self.simular_envio)
        
        layout.add_widget(self.label_status)
        layout.add_widget(btn_teste)
        return layout

    def simular_envio(self, instance):
        # Teste interno da automação
        self.motor.processar_comando("ENVIAR:841234567:DIO-1GB")
        self.label_status.text = "Comando Processado!"

if __name__ == '__main__':
    TimoteoAutoApp().run()
