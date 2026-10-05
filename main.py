import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from jnius import autoclass

SmsManager = autoclass('android.telephony.SmsManager')

class AgendadorSMSApp(App):
    def build(self):
        self.layout_principal = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        self.layout_principal.add_widget(Label(
            text="Agendador / Envio Múltiplo (+258)", 
            font_size='20sp', 
            size_hint_y=None, 
            height=40
        ))

        self.txt_numero = TextInput(
            hint_text="Número (ex: 841234567 ou +258841234567)", 
            multiline=False, 
            size_hint_y=None, 
            height=50
        )
        self.layout_principal.add_widget(self.txt_numero)

        self.txt_mensagem = TextInput(
            hint_text="Escreva a mensagem aqui...", 
            multiline=True, 
            size_hint_y=None, 
            height=100
        )
        self.layout_principal.add_widget(self.txt_mensagem)

        btn_enviar = Button(
            text="Enviar SMS", 
            background_color=(0.2, 0.7, 0.3, 1), 
            size_hint_y=None, 
            height=50
        )
        btn_enviar.bind(on_press=self.processar_envio)
        self.layout_principal.add_widget(btn_enviar)

        self.lbl_status = Label(text="Aguardando ação...", size_hint_y=None, height=60)
        self.layout_principal.add_widget(self.lbl_status)

        return self.layout_principal

    def formatar_numero(self, numero):
        numero = numero.strip().replace(" ", "")
        if not numero.startswith("+258"):
            if numero.startswith("258"):
                numero = "+" + numero
            else:
                numero = "+258" + numero
        return numero

    def processar_envio(self, instance):
        num_bruto = self.txt_numero.text
        msg = self.txt_mensagem.text

        if not num_bruto or not msg:
            self.lbl_status.text = "⚠️ Preencha o número e a mensagem!"
            return

        num_final = self.formatar_numero(num_bruto)

        try:
            sms_mgr = SmsManager.getDefault()
            sms_mgr.sendTextMessage(num_final, None, msg, None, None)
            self.lbl_status.text = f"✅ SMS enviada para: {num_final}"
            self.txt_mensagem.text = ""
        except Exception as e:
            self.lbl_status.text = f"❌ Erro ao enviar: {str(e)}"

if __name__ == '__main__':
    AgendadorSMSApp().run()
        
