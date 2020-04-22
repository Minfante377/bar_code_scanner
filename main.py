from PIL import Image
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy.lang import Builder
from functools import partial
from datetime import datetime
from pyzbar import pyzbar
import sys

store = JsonStore('articles.json')
Builder.load_string('''
<RotatedCamera>:
        orientation: 'vertical'
        Camera:
                id:camera
                canvas.before:
                        PushMatrix
                        Rotate:
                                angle: -90
                                origin:self.center
                canvas.after:
                        PopMatrix
                ''')

class MainScreen(Screen):
    
    def __init__(self,**kwargs):
        super (MainScreen,self).__init__(**kwargs)
        self._request_android_permissions()
        Window.clearcolor = (103/255,91/255,93/255,1)
        main_layout = BoxLayout(orientation = "vertical")
        add_button = Button(text = "Agregar nuevo producto")
        add_button.bind(on_release = self.changer_add)
        scan_button = Button(text = "Escanear codigo de barra")
        scan_button.bind(on_release = self.changer_scan)
        main_layout.add_widget(add_button)
        main_layout.add_widget(scan_button)
        self.add_widget(main_layout)

    def changer_add(self,*args):
        self.manager.current = 'add_screen'
    
    def changer_scan(self,*args):
        self.manager.current = 'scan_screen'

    def _request_android_permissions(self):
        if not platform == 'android':
            return
        from android.permissions import request_permission, Permission
        request_permission(Permission.CAMERA)
        request_permission(Permission.WRITE_EXTERNAL_STORAGE)
        request_permission(Permission.READ_EXTERNAL_STORAGE)

class AddScreen(Screen):

    def __init__(self,**kwargs):
        super(AddScreen, self).__init__(**kwargs)
        add_layout = BoxLayout(orientation = "vertical")
        inputs_box = BoxLayout(orientation = "horizontal")
        input_left_box = BoxLayout(orientation = "vertical")
        input_right_box = BoxLayout(orientation = "vertical")
        self.codigo = TextInput(text="Codigo")
        self.descripcion = TextInput(text="Descripcion")
        self.unidad_por_bulto = TextInput(text="Unidades por bulto")
        self.codigo_de_barra = TextInput(text="Codigo de barra")
        self.empresa = TextInput(text = "Empresa")
        self.precio = TextInput(text = "Precio")
        input_left_box.add_widget(self.codigo)
        input_left_box.add_widget(self.descripcion)
        input_left_box.add_widget(self.empresa)
        input_right_box.add_widget(self.unidad_por_bulto)
        input_right_box.add_widget(self.codigo_de_barra)
        input_right_box.add_widget(self.precio)
        inputs_box.add_widget(input_left_box)
        inputs_box.add_widget(input_right_box)
        generar_button = Button(text = "Generar articulo")
        generar_button.bind(on_release = self.create)
        add_layout.add_widget(inputs_box)
        add_layout.add_widget(generar_button)
        previous_button = Button(text = "Volver")
        previous_button.bind(on_release = self.changer)
        add_layout.add_widget(previous_button)
        self.succes = Popup(title = "Aviso de articulo", content = Label(text = "Articulo creado con exito"), size_hint = (0.75,0.25))
        self.warning = Popup(title = "Aviso de articulo", content = Label(text = "Datos invalidos"), size_hint = (0.75,0.25))
        self.add_widget(add_layout)
    
    def changer(self,*args):
        self.manager.current = 'main_screen'

    def create(self,signal):
        global store
        try:
            int(self.codigo_de_barra.text)
            int(self.precio.text)
        except:
            self.codigo.text= "Codigo"
            self.descripcion.text = "Descripcion"
            self.unidad_por_bulto.text = "Unidades por bulto"
            self.codigo_de_barra.text = "Codigo de barra"
            self.empresa.text = "Empresa"
            self.precio.text = "Precio"
            self.warning.open()
            return
        store.put(self.codigo_de_barra.text,descripcion = self.descripcion.text,unidad_bulto = self.unidad_por_bulto.text,
                codigo = self.codigo.text, empresa = self.empresa.text, precio = self.precio.text)
        self.codigo.text= "Codigo"
        self.descripcion.text = "Descripcion"
        self.unidad_por_bulto.text = "Unidades por bulto"
        self.codigo_de_barra.text = "Codigo de barra"
        self.empresa.text = "Empresa"
        self.precio.text = "Precio"
        self.succes.open()

class RotatedCamera(BoxLayout):

    def takePicture(self,path):
        camera = self.ids['camera']
        camera.export_to_png(path)

class ScanScreen(Screen):
        
    def __init__(self,**kwargs):
        super(ScanScreen, self).__init__(**kwargs)
        scan_layout = BoxLayout(orientation = "vertical")
        inputs_box = BoxLayout(orientation = "horizontal",size_hint = (1.0,0.2))
        input_left_box = BoxLayout(orientation = "vertical")
        input_right_box = BoxLayout(orientation = "vertical")
        self.codigo = TextInput(text="Codigo")
        self.descripcion = TextInput(text="Descripcion")
        self.unidad_por_bulto = TextInput(text="Unidades por bulto")
        self.codigo_de_barra = TextInput(text="Codigo de barra")
        self.empresa = TextInput(text = "Empresa")
        self.precio = TextInput(text = "Precio")
        input_left_box.add_widget(self.codigo)
        input_left_box.add_widget(self.descripcion)
        input_left_box.add_widget(self.empresa)
        input_right_box.add_widget(self.unidad_por_bulto)
        input_right_box.add_widget(self.codigo_de_barra)
        input_right_box.add_widget(self.precio)
        scan_button = Button(text = "Escanear codigo de barras",size_hint = (1.0,0.1))
        scan_button.bind(on_release = self.read_bar_code)
        add_button = Button(text = "Agregar articulo",size_hint = (1.0,0.1))
        previous_button = Button(text = "Volver",size_hint = (1.0,0.1))
        previous_button.bind(on_release = self.changer)
        scan_layout.add_widget(inputs_box)
        scan_layout.add_widget(scan_button)
        scan_layout.add_widget(add_button)
        scan_layout.add_widget(previous_button)
        self.cameraObject = RotatedCamera()
        self.cameraObject.ids['camera'].resolution = (1920, 1080) 
        self.cameraObject.ids['camera'].allow_strech = True
        self.cameraObject.ids['camera'].play = True
        scan_layout.add_widget(self.cameraObject)
        self.add_widget(scan_layout)
    
    def changer(self,*args):
        self.manager.current = 'main_screen'
 
    def read_bar_code(self,signal):
        barcode = []
        codigo_barras = None
        self.cameraObject.takePicture("/sdcard/tmp.png")
        img = Image.open("/sdcard/tmp.png")
        img = img.rotate(-90)
        barcode = pyzbar.decode(img)
        try:
            codigo_barras = barcode[0].data.decode("utf-8")
            print(codigo_barras)
            self.codigo_de_barra.text = codigo_barras
        except Exception as e:
            print(e)
            pass
        if store.exists(codigo_barras):
            self.unidad_por_bulto.text = store.get(codigo_barras)['unidad_bulto']
            self.codigo.text = store.get(codigo_barras)['codigo']
            self.descripcion.text = store.get(codigo_barras)['descripcion']
            self.empresa.text = store.get(codigo_barras)['empresa']
            self.precio.text = store.get(codigo_barras)['precio']
class ScanApp(App):
    def __init(self,**kwargs):
        super().__init__(**kwargs)

    def build(self):
        manager = ScreenManager()
        main_screen = MainScreen(name='main_screen')
        add_screen = AddScreen(name='add_screen')
        scan_screen = ScanScreen(name = 'scan_screen')
        manager.add_widget(main_screen)
        manager.add_widget(add_screen)
        manager.add_widget(scan_screen)
        manager.current = 'main_screen'
        return manager
    

    


ScanApp().run()
