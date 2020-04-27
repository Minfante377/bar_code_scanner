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
from kivy.uix.filechooser import FileChooserListView
from functools import partial
from datetime import datetime
from pyzbar import pyzbar
from table import TableView, TableColumn
import sys
from kivy.config import Config

Config.set('kivy','exit_on_escape','0')

store = JsonStore('articles.json')
shopping_car = JsonStore('shopping_car.json')

Builder.load_string('''
<RotatedCamera>:
        orientation: 'vertical'
        Camera:
                id:camera
                resolution: (1600,1200)
                canvas.before:
                        PushMatrix
                        Rotate:
                                angle: -90
                                origin:self.center
                canvas.after:
                        PopMatrix
                ''')
Builder.load_string('''
<FileBrowser>
    file_chooser: file_chooser
    FileChooserListView:
        id:file_chooser
        on_selection:
            root.selected_file(*args)
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
        shopping_button = Button(text = "Carrito de compras")
        shopping_button.bind(on_release = self.changer_shop)
        db_button = Button(text = "Base de datos")
        db_button.bind(on_release = self.changer_db)
        main_layout.add_widget(add_button)
        main_layout.add_widget(scan_button)
        main_layout.add_widget(shopping_button)
        main_layout.add_widget(db_button)
        self.add_widget(main_layout)

    def changer_add(self,*args):
        self.manager.current = 'add_screen'
    
    def changer_scan(self,*args):
        self.manager.current = 'scan_screen'

    def changer_shop(self,*args):
        self.manager.current = 'table_screen'
    
    def changer_db(self,*args):
        self.manager.current = 'db_screen'

    def _request_android_permissions(self):
        if not platform == 'android':
            return
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])

class FileBrowser(BoxLayout):
    
    def __init__(self,**kwargs):
        super(FileBrowser,self).__init__(**kwargs)
        self.file_chooser.path = "/sdcard/"
    
    def selected_file(self,*args):
        try:
            self.file_chooser.path = args[1][0]
        except:
            pass

class AddScreen(Screen):

    def __init__(self,**kwargs):
        super(AddScreen, self).__init__(**kwargs)
        add_layout = BoxLayout(orientation = "vertical")
        inputs_box = BoxLayout(orientation = "horizontal")
        input_left_box = BoxLayout(orientation = "vertical")
        input_right_box = BoxLayout(orientation = "vertical")
        self.codigo = TextInput(hint_text = "Codigo")
        self.descripcion = TextInput(hint_text="Descripcion")
        self.unidad_por_bulto = TextInput(hint_text="Unidades por bulto")
        self.codigo_de_barra = TextInput(hint_text="Codigo de barra")
        self.empresa = TextInput(hint_text = "Empresa")
        self.precio = TextInput(hint_text = "Precio")
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
        self.file_chooser = FileBrowser()
        self.browse_content = BoxLayout(orientation = 'vertical')
        self.browse_content.add_widget(self.file_chooser)
        self.import_button = Button(text = "Importar archivo", on_release = self.import_csv,size_hint = (1.0,0.2))
        self.browse_content.add_widget(self.import_button)
        self.browse_popup = Popup(title = "Importar archivo",content = self.browse_content,size_hint = (0.75,0.75))
        import_button = Button(text = "Importar")
        import_button.bind(on_release = self.browse_popup.open)
        add_layout.add_widget(import_button)
        previous_button = Button(text = "Volver")
        previous_button.bind(on_release = self.changer)
        add_layout.add_widget(previous_button)
        self.succes = Popup(title = "Aviso de articulo", content = Label(text = "Articulo creado con exito"), size_hint = (0.9,0.25))
        self.warning = Popup(title = "Aviso de articulo", content = Label(text = "Datos invalidos"), size_hint = (0.9,0.25))
        self.add_widget(add_layout)
    
    def changer(self,*args):
        self.manager.current = 'main_screen'

    def create(self,signal):
        global store
        try:
            int(self.codigo_de_barra.text)
            float(self.precio.text)
        except:
            self.codigo.text= ""
            self.descripcion.text = ""
            self.unidad_por_bulto.text = ""
            self.codigo_de_barra.text = ""
            self.empresa.text = ""
            self.precio.text = ""
            self.warning.open()
            return
        if self.codigo.text == '' or self.descripcion.text == '' or self.unidad_por_bulto.text == '' or self.empresa == '':
            self.warning.open()
            return
        store.put(self.codigo_de_barra.text,descripcion = self.descripcion.text,unidad_bulto = self.unidad_por_bulto.text,
                codigo = self.codigo.text, empresa = self.empresa.text, precio = self.precio.text)
        self.codigo.text= ""
        self.descripcion.text = ""
        self.unidad_por_bulto.text = ""
        self.codigo_de_barra.text = ""
        self.empresa.text = ""
        self.precio.text = ""
        self.succes.open()
    
    def import_csv(self,button):
        path = self.file_chooser.file_chooser.path
        try:
            f = open(path,'r')
        except:
            return
        lines = f.readlines()
        for line in lines:
            line = line.strip("\n")
            line = line.split(",")
            store.put(line[0],descripcion = line[2],unidad_bulto = line[4],
                codigo = line[1], empresa = line[3], precio = line[5])
        self.browse_popup.dismiss()
        self.succes.open()

class RotatedCamera(BoxLayout):

    def takePicture(self,path):
        camera = self.ids['camera']
        camera.export_to_png(path)

class ScanScreen(Screen):
        
    def __init__(self,**kwargs):
        super(ScanScreen, self).__init__(**kwargs)
        scan_layout = BoxLayout(orientation = "vertical")
        inputs_box = BoxLayout(orientation = "horizontal",size_hint = (1.0,0.1))
        input_left_box = BoxLayout(orientation = "vertical")
        input_right_box = BoxLayout(orientation = "vertical")
        self.codigo = TextInput(hint_text="Codigo")
        self.descripcion = TextInput(hint_text="Descripcion")
        self.unidad_por_bulto = TextInput(hint_text="Unidades por bulto")
        self.codigo_de_barra = TextInput(hint_text="Codigo de barra")
        self.codigo_de_barra.bind(text = self.refresh_data)
        self.empresa = TextInput(hint_text = "Empresa")
        self.precio = TextInput(hint_text = "Precio")
        self.quantity = TextInput(hint_text = "Cantidad",size_hint = (1.0,0.03))
        input_left_box.add_widget(self.codigo)
        input_left_box.add_widget(self.descripcion)
        input_left_box.add_widget(self.empresa)
        input_right_box.add_widget(self.unidad_por_bulto)
        input_right_box.add_widget(self.codigo_de_barra)
        input_right_box.add_widget(self.precio)
        inputs_box.add_widget(input_left_box)
        inputs_box.add_widget(input_right_box)
        scan_button = Button(text = "Escanear codigo de barras",size_hint = (1.0,0.05))
        scan_button.bind(on_release = self.read_bar_code)
        add_button = Button(text = "Agregar articulo",size_hint = (1.0,0.05))
        add_button.bind(on_release = self.add_item)
        previous_button = Button(text = "Volver",size_hint = (1.0,0.05))
        previous_button.bind(on_release = self.changer)
        scan_layout.add_widget(inputs_box)
        scan_layout.add_widget(self.quantity)
        scan_layout.add_widget(scan_button)
        scan_layout.add_widget(add_button)
        scan_layout.add_widget(previous_button)
        self.cameraObject = RotatedCamera(size_hint = (1.0,0.5))
        self.cameraObject.ids['camera'].allow_strech = True
        self.cameraObject.ids['camera'].keep_ratio = False
        self.cameraObject.ids['camera'].play = True
        scan_layout.add_widget(self.cameraObject)
        self.succes = Popup(title = "Aviso de articulo", content = Label(text = "Articulo agregado con exito"), size_hint = (0.9,0.25))
        self.warning = Popup(title = "Aviso de articulo", content = Label(text = "Datos invalidos"), size_hint = (0.9,0.25))
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
    
    def add_item(self,signal): 
        global shopping_car
        try:
            int(self.codigo_de_barra.text)
            float(self.precio.text)
            int(self.quantity.text)
        except:
            self.codigo.text= ""
            self.descripcion.text = ""
            self.unidad_por_bulto.text = ""
            self.codigo_de_barra.text = ""
            self.empresa.text = ""
            self.precio.text = ""
            self.quantity.text = ""
            self.warning.open()
            return
        
        if not store.exists(self.codigo_de_barra.text):
            warning = Popup(title = "Error", content = Label(text = "El codigo de barras no existe en su base de datos"), size_hint = (0.9,0.25))
            warning.open()
            self.codigo.text= ""
            self.descripcion.text = ""
            self.unidad_por_bulto.text = ""
            self.codigo_de_barra.text = ""
            self.empresa.text = ""
            self.precio.text = ""
            self.quantity.text = ""
            return

        shopping_car.put(self.codigo_de_barra.text,descripcion = self.descripcion.text,unidad_bulto = self.unidad_por_bulto.text,
                codigo = self.codigo.text, empresa = self.empresa.text, precio = self.precio.text, cantidad = self.quantity.text)
        self.codigo.text= ""
        self.descripcion.text = ""
        self.unidad_por_bulto.text = ""
        self.codigo_de_barra.text = ""
        self.empresa.text = ""
        self.precio.text = ""
        self.quantity.text = ""
        self.succes.open()
    
    def refresh_data(self,input_text,text):
        codigo_barras = self.codigo_de_barra.text
        if store.exists(codigo_barras):
            self.unidad_por_bulto.text = store.get(codigo_barras)['unidad_bulto']
            self.codigo.text = store.get(codigo_barras)['codigo']
            self.descripcion.text = store.get(codigo_barras)['descripcion']
            self.empresa.text = store.get(codigo_barras)['empresa']
            self.precio.text = store.get(codigo_barras)['precio']


class TableScreen(Screen):
        
    def __init__(self,**kwargs):
        super(TableScreen, self).__init__(**kwargs)
        self.refresh() 

    def on_pre_enter(self):
        self.refresh()

    def changer(self,*args):
        self.manager.current = 'main_screen'
    
    def refresh(self,):
        self.layout = BoxLayout(orientation = "vertical")
        self.table_layout = BoxLayout(orientation = "horizontal",size_hint = (1.0,1.0))
        self.article_layout = BoxLayout(orientation = "vertical")
        self.quantity_layout = BoxLayout(orientation = "vertical",size_hint = (0.1,1.0))
        self.delete_layout = BoxLayout(orientation = "vertical",size_hint = (0.2,1.0))
        self.total_layout = BoxLayout(orientation = "horizontal",size_hint = (1.0,0.2))
        self.table_layout.clear_widgets()
        self.labels = TableView(size_hint = (0.877,1.0)) 
        self.labels.add_column(TableColumn("Codigo",key = "codigo",hint_text='0'))
        self.labels.add_column(TableColumn("Descripcion",key = "descripcion",hint_text='0'))
        self.labels.add_column(TableColumn("Empresa",key = "empresa",hint_text='0'))
        self.labels.add_column(TableColumn("Unidades por bulto",key = "cantidad_bulto",hint_text='0'))
        self.labels.add_column(TableColumn("Precio",key = "precio" ,hint_text='0'))
        self.table = TableView(size_hint = (1.0,1.0)) 
        self.table.add_column(TableColumn("Codigo",key = "codigo",hint_text='0'))
        self.table.add_column(TableColumn("Descripcion",key = "descripcion",hint_text='0'))
        self.table.add_column(TableColumn("Empresa",key = "empresa",hint_text='0'))
        self.table.add_column(TableColumn("Unidades por bulto",key = "cantidad_bulto",hint_text='0'))
        self.table.add_column(TableColumn("Precio",key = "precio" ,hint_text='0'))
        row = {"codigo":"Codigo","descripcion":"Descripcion",
                "empresa":"Empresa","cantidad_bulto":"Unidades por bulto",
                "precio":"Precio"}
        self.labels.add_row(row)
        i = 0
        self.content = BoxLayout(orientation = 'vertical')
        delete = Button(text = "Eliminar", on_release = self.delete)
        delete.bind(on_release = self.delete)
        self.delete_label = Label(text = "Esta a punto de eliminar un elemento")
        self.content.add_widget(self.delete_label)
        self.content.add_widget(delete)
        self.delete_popup = Popup(title = "Eliminar", content = self.content , size_hint = (0.9,0.25))
        for key in shopping_car.keys():
            row = {"codigo":shopping_car.get(key)['codigo'],"descripcion":shopping_car.get(key)['descripcion'],
                "empresa":shopping_car.get(key)['empresa'],"cantidad_bulto":shopping_car.get(key)['unidad_bulto'],
                "precio":shopping_car.get(key)['precio']}
            self.table.add_row(row)
            self.quantity_layout.add_widget(TextInput(text = shopping_car.get(key)['cantidad'],id = str(i)))
            self.delete_layout.add_widget(Button(text = "Eliminar",id = str(i), on_release = self.call_delete_popup))
            i = i + 1
        for children in self.quantity_layout.children:
            children.bind(text = self.refresh_total)
        self.article_layout.add_widget(self.labels)
        self.table_layout.add_widget(self.table)
        self.table_layout.add_widget(self.quantity_layout)
        self.table_layout.add_widget(self.delete_layout)
        self.article_layout.add_widget(self.table_layout)
        self.clear_content = BoxLayout(orientation = 'vertical')
        clear_button = Button(text = "Eliminar")
        clear_button.bind(on_release = self.clear)
        self.clear_label = Label(text = "Esta a punto de eliminar todos los elementos")
        self.clear_content.add_widget(self.clear_label)
        self.clear_content.add_widget(clear_button)
        self.clear_popup = Popup(title = "Eliminar", content = self.clear_content , size_hint = (0.9,0.25))
        self.clear_button = Button(text = "Borrar todo",size_hint = (1.0,0.1))
        self.clear_button.bind(on_release = self.clear_popup.open) 
        self.content = BoxLayout(orientation = "vertical")
        export = Button(text = "Export", on_release = self.export)
        self.export_name = TextInput(hint_text = "Nombre del archivo")
        self.content.add_widget(self.export_name)
        self.content.add_widget(export)
        self.export_popup = Popup(title = "Exportar archivo", content = self.content , size_hint = (0.9,0.25))
        export_button = Button(text = "Exportar",size_hint = (1.0,0.1))
        export_button.bind(on_release = self.export_popup.open)
        previous_button = Button(text = "Volver",size_hint = (1.0,0.1))
        previous_button.bind(on_release = self.changer)
        self.discount = TextInput(text = "0.0")
        discount_button = Button(text = "Aplicar descuento")
        discount_button.bind(on_release = self.apply_discount)
        self.discount_warning = Popup(title = "Error!", content = Label(text = "Descuento invalido"), size_hint = (0.9,0.25))
        self.succes_export_popup = Popup(title = "Exportar Archivo", content = Label(text = "Archivo exportado con exito"), size_hint = (0.9,0.25))
        self.total = Label(text = "Total")
        self.calculate_total(0)
        self.total_layout.add_widget(self.discount) 
        self.total_layout.add_widget(discount_button) 
        self.total_layout.add_widget(self.total)
        self.layout.add_widget(self.article_layout)
        self.layout.add_widget(self.total_layout)
        self.layout.add_widget(export_button)
        self.layout.add_widget(self.clear_button)
        self.layout.add_widget(previous_button)
        self.clear_widgets()
        self.add_widget(self.layout)
   
    def call_delete_popup(self,button):
        i = 0
        for key in shopping_car.keys():
            if i == int(button.id):
                break
            i = i+1
        self.delete_index = i
        self.delete_popup.open()

    def delete(self,button):
        key = shopping_car.keys()[self.delete_index]
        shopping_car.delete(key)
        self.delete_popup.dismiss()
        self.refresh()
    
    def clear(self,button):
        for key in shopping_car.keys():
            shopping_car.delete(key)
        self.clear_popup.dismiss()
        self.refresh()
    
    def calculate_total(self,discount):
        i = 0
        total = 0
        for key in shopping_car.keys():
            price = float(shopping_car.get(key)['precio'])
            for children in self.quantity_layout.children:
                if int(children.id) == i:
                    quantity = int(children.text)
            total = total + quantity * price
        total = (1 - discount) * total
        self.total.text = "%.2f" % total
    
    def apply_discount(self,button):
        try:
            discount = float(self.discount.text) 
        except:
            self.discount_warning.open()
            return
        if discount > 100 or discount < 0:
            self.discount_warning.open()
            return
        discount = discount/100
        self.calculate_total(discount)
    
    def refresh_total(self,text_input,text):
        try:
            discount = float(self.discount.text) 
        except:
            self.discount_warning.open()
            return
        if discount > 100 or discount < 0:
            self.discount_warning.open()
            return
        discount = discount/100
        self.calculate_total(discount)
    
    def export(self,button):
        name = self.export_name.text
        i = 0
        f = open("/sdcard/"+name+".csv","w+")
        f.write("Codigo,Descripcion,Empresa,Unidades por bulto,Precio unitario,Cantidad,Subtotal\n")
        for key in shopping_car.keys():
            codigo = shopping_car.get(key)['codigo']
            descripcion = shopping_car.get(key)['descripcion']
            empresa = shopping_car.get(key)['empresa']
            cantidad_bulto = shopping_car.get(key)['unidad_bulto']
            precio = shopping_car.get(key)['precio']
            for children in self.quantity_layout.children:
                if int(children.id) == i:
                    quantity = int(children.text)
            subtotal = str(quantity * float(precio))
            f.write("%s,%s,%s,%s,%s,%s,%s\n" %(codigo,descripcion,empresa,cantidad_bulto,precio,str(quantity),subtotal))
        f.write(" , , , , ,Descuento,%s\n" % (self.discount.text))
        f.write(" , , , , ,Total,%s\n" % (self.total.text))
        f.close()
        self.export_popup.dismiss()
        self.succes_export_popup.open()

class DbScreen(Screen):
        
    def __init__(self,**kwargs):
        super(DbScreen, self).__init__(**kwargs)
        self.refresh() 

    def on_pre_enter(self):
        self.refresh()

    def changer(self,*args):
        self.manager.current = 'main_screen'
    
    def refresh(self,):
        self.layout = BoxLayout(orientation = "vertical")
        self.table_layout = BoxLayout(orientation = "horizontal",size_hint = (1.0,1.0))
        self.article_layout = BoxLayout(orientation = "vertical")
        self.delete_layout = BoxLayout(orientation = "vertical",size_hint = (0.2,1.0))
        self.total_layout = BoxLayout(orientation = "horizontal",size_hint = (1.0,0.2))
        self.table_layout.clear_widgets()
        self.labels = TableView(size_hint = (0.913,1.0)) 
        self.labels.add_column(TableColumn("Codigo",key = "codigo",hint_text='0'))
        self.labels.add_column(TableColumn("Descripcion",key = "descripcion",hint_text='0'))
        self.labels.add_column(TableColumn("Empresa",key = "empresa",hint_text='0'))
        self.labels.add_column(TableColumn("Unidades por bulto",key = "cantidad_bulto",hint_text='0'))
        self.labels.add_column(TableColumn("Precio",key = "precio" ,hint_text='0'))
        self.table = TableView(size_hint = (1.0,1.0)) 
        self.table.add_column(TableColumn("Codigo",key = "codigo",hint_text='0'))
        self.table.add_column(TableColumn("Descripcion",key = "descripcion",hint_text='0'))
        self.table.add_column(TableColumn("Empresa",key = "empresa",hint_text='0'))
        self.table.add_column(TableColumn("Unidades por bulto",key = "cantidad_bulto",hint_text='0'))
        self.table.add_column(TableColumn("Precio",key = "precio" ,hint_text='0'))
        row = {"codigo":"Codigo","descripcion":"Descripcion",
                "empresa":"Empresa","cantidad_bulto":"Unidades por bulto",
                "precio":"Precio"}
        self.labels.add_row(row)
        i = 0
        self.content = BoxLayout(orientation = 'vertical')
        delete = Button(text = "Eliminar", on_release = self.delete)
        delete.bind(on_release = self.delete)
        self.delete_label = Label(text = "Esta a punto de eliminar un elemento")
        self.content.add_widget(self.delete_label)
        self.content.add_widget(delete)
        self.delete_popup = Popup(title = "Eliminar", content = self.content , size_hint = (0.9,0.25))
        for key in store.keys():
            row = {"codigo":store.get(key)['codigo'],"descripcion":store.get(key)['descripcion'],
                "empresa":store.get(key)['empresa'],"cantidad_bulto":store.get(key)['unidad_bulto'],
                "precio":store.get(key)['precio']}
            self.table.add_row(row)
            self.delete_layout.add_widget(Button(text = "Eliminar",id = str(i), on_release = self.call_delete_popup))
            i = i + 1
        self.article_layout.add_widget(self.labels)
        self.table_layout.add_widget(self.table)
        self.table_layout.add_widget(self.delete_layout)
        self.article_layout.add_widget(self.table_layout) 
        self.clear_content = BoxLayout(orientation = 'vertical')
        clear_button = Button(text = "Eliminar")
        clear_button.bind(on_release = self.clear)
        self.clear_label = Label(text = "Esta a punto de eliminar todos los elementos")
        self.clear_content.add_widget(self.clear_label)
        self.clear_content.add_widget(clear_button)
        self.clear_popup = Popup(title = "Eliminar", content = self.clear_content , size_hint = (0.9,0.25))
        self.clear_button = Button(text = "Borrar todo",size_hint = (1.0,0.1))
        self.clear_button.bind(on_release = self.clear_popup.open) 
        self.content = BoxLayout(orientation = "vertical")
        previous_button = Button(text = "Volver",size_hint = (1.0,0.1))
        previous_button.bind(on_release = self.changer)
        self.discount = TextInput(text = "0.0")
        self.layout.add_widget(self.article_layout)
        self.layout.add_widget(self.clear_button)
        self.layout.add_widget(previous_button)
        self.clear_widgets()
        self.add_widget(self.layout)
    
    def call_delete_popup(self,button):
        i = 0
        for key in store.keys():
            if i == int(button.id):
                break
            i = i+1
        self.delete_index = i
        self.delete_popup.open()

    def delete(self,button):
        key = store.keys()[self.delete_index]
        store.delete(key)
        self.delete_popup.dismiss()
        self.refresh()
    
    def clear(self,button):
        for key in store.keys():
            store.delete(key)
        self.clear_popup.dismiss()
        self.refresh()

class ScanApp(App):
    def __init(self,**kwargs):
        super().__init__(**kwargs)

    def build(self):
        manager = ScreenManager()
        main_screen = MainScreen(name='main_screen')
        add_screen = AddScreen(name='add_screen')
        scan_screen = ScanScreen(name = 'scan_screen')
        table_screen = TableScreen(name = 'table_screen')
        db_screen = DbScreen(name = "db_screen")
        manager.add_widget(main_screen)
        manager.add_widget(add_screen)
        manager.add_widget(scan_screen)
        manager.add_widget(table_screen)
        manager.add_widget(db_screen)
        manager.current = 'main_screen'
        return manager
   
    def on_pause(self):
       return True

    


ScanApp().run()
