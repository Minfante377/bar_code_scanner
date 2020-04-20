from PIL import Image
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.uix.camera import Camera
from kivy.utils import platform
from functools import partial
from datetime import datetime
from pyzbar import pyzbar
import sys

store = JsonStore('articles.json')

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
        input_left_box.add_widget(self.codigo)
        input_left_box.add_widget(self.descripcion)
        input_right_box.add_widget(self.unidad_por_bulto)
        input_right_box.add_widget(self.codigo_de_barra)
        inputs_box.add_widget(input_left_box)
        inputs_box.add_widget(input_right_box)
        generar_button = Button(text = "Generar articulo")
        generar_button.bind(on_release = self.create)
        add_layout.add_widget(inputs_box)
        add_layout.add_widget(generar_button)
        previous_button = Button(text = "Volver")
        previous_button.bind(on_release = self.changer)
        add_layout.add_widget(previous_button)
        self.add_widget(add_layout)
    
    def changer(self,*args):
        self.manager.current = 'main_screen'

    def create(self,signal):
        global store
        store.put(self.codigo_de_barra.text,descripcion = self.descripcion.text,unidad_bulto = self.unidad_por_bulto.text,
                codigo = self.codigo.text) 

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
        input_left_box.add_widget(self.codigo)
        input_left_box.add_widget(self.descripcion)
        input_right_box.add_widget(self.unidad_por_bulto)
        input_right_box.add_widget(self.codigo_de_barra)
        inputs_box.add_widget(input_left_box)
        inputs_box.add_widget(input_right_box)
        scan_button = Button(text = "Escanear codigo de barras",size_hint = (1.0,0.1))
        scan_button.bind(on_release = self.read_bar_code)
        add_button = Button(text = "Agregar articulo",size_hint = (1.0,0.1))
        previous_button = Button(text = "Volver",size_hint = (1.0,0.1))
        previous_button.bind(on_release = self.changer)
        scan_layout.add_widget(inputs_box)
        scan_layout.add_widget(scan_button)
        scan_layout.add_widget(add_button)
        scan_layout.add_widget(previous_button)
        self.cameraObject = Camera(play= True, resolution = (800,600))
        camera_box = ScatterLayout(do_scale = False, do_translation_x = False, do_translation_y = False, do_rotation= False)
        camera_box.rotation = -90
        camera_box.pos_hint = {'x':0.3,'y': 0.75}
        camera_box.add_widget(self.cameraObject)
        scan_layout.add_widget(camera_box)
        self.add_widget(scan_layout)
    
    def changer(self,*args):
        self.manager.current = 'main_screen'
 
    def read_bar_code(self,signal):
        barcode = []
        codigo_barras = None
        self.cameraObject.export_to_png("/sdcard/tmp.png")
        img = Image.open("/sdcard/tmp.png")
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
