import flet as ft
from modals.modal_empleado import show_modal_nuevo_empleado
from modals.modal_descuento import show_modal_descuento
from modals.modal_producto import show_modal_editar_producto
from modals.modal_pago import show_modal_pago 
from modals.modal_corte import show_modal_corte  
from database.database import obtener_productos, validar_empleado, obtener_producto_por_barcode
from functools import partial
from datetime import datetime

class Sale:  

    def __init__(self):
        self.productos = []
        self.subtotal = 0.0
        self.descuento_porcentaje = 0.0
        self.descuento = 0.0
        self.total = 0.0
        
    def _calcular_totales(self):
        """Calcula subtotal, descuento y total final"""
        self.subtotal = sum(p[3] * cantidad for p, cantidad in self.productos)
        self.descuento = self.subtotal * (self.descuento_porcentaje / 100)
        self.total = max(0, self.subtotal - self.descuento)  # Evita total negativo

    def aplicar_descuento(self, porcentaje):
        """Aplica un porcentaje de descuento que se mantendrá proporcional"""
        self.descuento_porcentaje = max(0, min(100, float(porcentaje)))  # Asegura 0-100%
        self._calcular_totales()
        
    def agregar_producto(self, producto):
        # Verificar si el producto ya está en el carrito
        for i, (p, cantidad) in enumerate(self.productos):
            if p[0] == producto[0]:  # Comparar por ID
                self.productos[i] = (p, cantidad + 1)
                self._calcular_total()
                return
        
        # Si no existe, agregarlo con cantidad 1
        self.productos.append((producto, 1))
        self._calcular_total()

    def actualizar_cantidad(self, producto_id, nueva_cantidad):
        for i, (p, cantidad) in enumerate(self.productos):
            if p[0] == producto_id:
                if nueva_cantidad <= 0:
                    del self.productos[i]
                else:
                    self.productos[i] = (p, nueva_cantidad)
                self._calcular_total()
                break

    def _calcular_total(self):
        self.total = sum(p[3] * cantidad for p, cantidad in self.productos) - self.descuento

    def agregar_producto_por_codigo(self, codigo_barras):
        producto = obtener_producto_por_barcode(codigo_barras)
        if producto:
            self.agregar_producto(producto)
            return True
        return False
    
def main(page: ft.Page):

    page.window.alignment = ft.alignment.center
    page.window.icon = "Icon.ico"
    page.title = "Sistema de Punto de Venta"
    page.theme_mode = ft.ThemeMode.LIGHT

    def handle_window_event(e):
        if e.data == "close":
            page.open(confirm_dialog)

    page.window.prevent_close = True
    page.window.on_event = handle_window_event

    def no_click(e):
        page.close(confirm_dialog)

    def yes_click(e):
        page.close(confirm_dialog)
        page.window.destroy()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Favor de confirmar"),
        content=ft.Text("¿Está seguro de que desea salir?"),
        actions=[
            ft.ElevatedButton("Si", on_click=yes_click),
            ft.OutlinedButton("No", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def route_change(e):
        page.views.clear()
        
        # Ruta /login
        if page.route == "/login":
            
            codigo_input = ft.TextField(label="Ingrese su nombre", filled=True, autofocus=True,border_color='#EBEBEB', border_radius=7)
            password_input = ft.TextField(label="Ingrese su contraseña", password=True, can_reveal_password=True, filled=True, autofocus=True,border_color='#EBEBEB', border_radius=7)
            error_text = ft.Text(color="red", visible=False)
            
                
            def on_login(e):
                empleado = validar_empleado(codigo_input.value, password_input.value)
                if empleado:
                    page.session.set("empleado_id", empleado[0])
                    page.session.set("empleado_nombre", empleado[1])  # Almacenamos el nombre
                    page.go("/main")
                else:
                    error_text.value = "Credenciales incorrectas"
                    error_text.visible = True
                    page.update()
                    
            cover = ft.Container(
                height=page.height * 2,
                padding=100,
                expand=True,
                bgcolor='#FFF1F4',
                content= ft.Image (
                    src="Logo.png",
                )
            )
            
            form = ft.Container(
                content = ft.Column(
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    controls=[
                        ft.Text("Inicio de sesión", size=32, weight=ft.FontWeight.BOLD),
                        
                        ft.Row(
                            [ft.Text(datetime.now().strftime("%d/%m/%y"),size=16, weight=ft.FontWeight.BOLD)],
                        alignment=ft.MainAxisAlignment.END
                        
                        ),
                        ft.Text("Identificador",size=25),
                        codigo_input,
                        ft.Text("Contraseña",size=25),
                        password_input,
                        error_text,
                        ft.Container(    
                            content= ft.FilledButton("Iniciar Sesion",           
                                bgcolor='#FFCDFA', 
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=7),
                                    text_style=ft.TextStyle(
                                        size=20
                                    )
                                ),
                                height=50,
                                width=700,
                                color=ft.Colors.BLACK,
                                on_click=on_login
                            ),  
                        ),
                        ft.ElevatedButton(
                            "Nuevo usuario",
                            style=ft.ButtonStyle(
                                bgcolor='#FFCDFA',
                                color=ft.Colors.BLACK,
                                shape=ft.RoundedRectangleBorder(radius=7)
                            ),
                            on_click= lambda e: show_modal_nuevo_empleado(page)
                            ),
                        ft.Divider(),
                        ft.Row(
                            [ft.Text("ó",size=17)],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Row(
                            [ft.Text("Escanea tu gafete",size=25)],
                            alignment=ft.MainAxisAlignment.CENTER 
                        ),
                        ft.Row(
                            [ft.Icon(ft.Icons.BARCODE_READER, size=100,color='black')],
                            alignment=ft.MainAxisAlignment.CENTER 
                        )
                    ],               
                ),
                padding=30,
                expand=True
            )    
            
            page.views.append(
                ft.View(                    
                    "/login",                   
                    [
                        ft.Row(
                            [
                                cover,
                                form
                            ],
                            expand=True,
                            
                        )
                    ],
                    padding=0,   
                )
            )
        
        # Ruta /main (tu vista principal)
        elif page.route == "/main":
            
            if not page.session.get("empleado_id"):
                page.go("/login")
                return

            def yes_click(e):
                page.views.clear()
                page.go("/login")

            def no_click(e):
                page.close(confirm_logout)
                    
            def on_logout(e):
                page.open(confirm_logout)
                
            confirm_logout = ft.AlertDialog(
                modal=True,
                title=ft.Text("Esta a punto de cerrar sesion"),
                content=ft.Text("Todo cambio no confirmado sera eliminado, ¿continuar?"),
                actions=[
                    ft.ElevatedButton("Si", on_click=yes_click),
                    ft.OutlinedButton("No", on_click=no_click),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            sale=Sale()

            codigo_barras_buffer = ""

            def on_keyboard(e: ft.KeyboardEvent):
                nonlocal codigo_barras_buffer
                if page.route == "/main":
                    if e.key == "Enter":  # Tecla Enter
                        if codigo_barras_buffer:
                            if sale.agregar_producto_por_codigo(codigo_barras_buffer):
                                actualizar_sidebar()
                            codigo_barras_buffer = ""
                    elif len(e.key) == 1 and e.key.isalnum():  # Teclas alfanuméricas
                        codigo_barras_buffer += e.key
                    elif codigo_barras_buffer:  # Timeout implícito
                        codigo_barras_buffer = ""

            page.on_keyboard_event = on_keyboard
            
            def nuevo_pedido(e):
                # Limpiar todos los datos del carrito
                sale.productos = []
                sale.subtotal = 0.0
                sale.descuento_porcentaje = 0.0
                sale.descuento = 0.0
                sale.total = 0.0
                # Actualizar la interfaz
                actualizar_sidebar()

            page.appbar = ft.AppBar(
                shadow_color=ft.Colors.BLACK87,  # Color de la sombra
                elevation=15,
                bgcolor=ft.Colors.BLACK,
                leading=ft.Container(
                    padding=10,
                    content=ft.Row(
                        controls=[
                            ft.Text("Vale's", weight=ft.FontWeight.BOLD, size=25, color='white'),
                            ft.Text('PdV', weight=ft.FontWeight.BOLD, size=25, color='#D013BD'),
                        ],
                    ),
                ),

                title=ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Image(src="Logo.png", fit=ft.ImageFit.CONTAIN, height=50),
                ),

                actions=[
                    ft.Container(
                        padding=10,
                        content=ft.Row(
                            controls=[           
                                ft.TextButton(
                                    text ='Crear/Editar articulo', 
                                    style=ft.ButtonStyle(   
                                        color=ft.Colors.WHITE,  # Color del texto
                                    ),
                                    on_click=lambda e: show_modal_editar_producto(page, lambda: actualizar_lista_productos())
                                ),
                                ft.ElevatedButton(
                                    'Corte',
                                    color='Black',
                                    width=90,
                                    bgcolor="#D9D9D9",
                                    style=ft.ButtonStyle(color=ft.Colors.BLACK,shape=ft.RoundedRectangleBorder(radius=7)),
                                    on_click=lambda e: show_modal_corte(page)
                                    
                                ),
                                ft.Container(width=2),
                                ft.ElevatedButton(
                                    'Nuevo Pedido',
                                    color='Black',
                                    bgcolor='#FFCDFA',
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                                    on_click=nuevo_pedido
                                ),
                            ]
                        ),
                    )
                ]
            )

            def crear_producto_tile(producto, on_agregar):
                return ft.Column(
                controls=[
                    ft.ListTile(
                        content_padding=ft.padding.all(15),
                        leading=ft.Column([
                            ft.Text(producto[1], weight=ft.FontWeight.BOLD, color='Black', size=20),
                            ft.Text(f"Marca: {producto[2]}", weight=ft.FontWeight.NORMAL, size=15),    
                        ]),
                        title=ft.Container(
                            alignment=ft.alignment.center_right,
                            content=ft.Text(f"Precio: ${producto[3]}", size=15, weight=ft.FontWeight.BOLD)
                        ),
                        trailing=ft.ElevatedButton(
                            "Agregar",
                            color='Black',
                            bgcolor='#FFCDFA',
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                            on_click=on_agregar
                        )
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_400)  # ← Divider añadido aquí
                ]
            )

            def crear_item_carrito(producto, cantidad, on_aumentar, on_disminuir, on_cambio_cantidad):
                precio_total = producto[3] * cantidad
                
                cantidad_field = ft.Container(
                    bgcolor='#D9D9D9',
                    alignment=ft.alignment.center,
                    width=50,
                    border_radius=5,
                    content=ft.TextField(
                        value=str(cantidad),
                        text_align=ft.TextAlign.CENTER,
                        border=ft.InputBorder.NONE,
                        on_change=lambda e: on_cambio_cantidad(e.control.value),
                        input_filter=ft.NumbersOnlyInputFilter(),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        on_blur=lambda e: e.control.update() if not e.control.value else None
                    )
                )
                
                return ft.Container(
                    content=ft.Column([
                        ft.Text(producto[1], weight=ft.FontWeight.BOLD, size=16),
                        ft.Row(
                            spacing=0,
                            controls=[
                                ft.Text("Cant.", size=15),
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE,
                                    icon_color=ft.Colors.BLACK,
                                    on_click=on_disminuir,
                                    tooltip="Reducir cantidad"
                                ),
                                cantidad_field,
                                ft.IconButton(
                                    icon=ft.Icons.ADD,
                                    icon_color=ft.Colors.BLACK,
                                    on_click=on_aumentar,
                                    tooltip="Aumentar cantidad"
                                ),
                                ft.Container(expand=True),
                                ft.Text(f"${precio_total:.2f}", size=20, weight=ft.FontWeight.BOLD)
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        )
                    ]),
                    padding=10,
                    margin=5,
                    border_radius=10,
                    bgcolor="#f0f0f0"
                )

            def actualizar_cantidad_producto(e, producto_id, cambio):
                for i, (p, cantidad) in enumerate(sale.productos):
                    if p[0] == producto_id:
                        nueva_cantidad = cantidad + cambio
                        if nueva_cantidad <= 0:
                            del sale.productos[i]
                        else:
                            sale.productos[i] = (p, nueva_cantidad)
                            
                        sale._calcular_total()
                        actualizar_sidebar()
                        break

            def cambiar_cantidad_producto(nueva_cantidad_str, producto_id):
                try:
                    if nueva_cantidad_str:  # Solo si no está vacío
                        nueva_cantidad = int(nueva_cantidad_str)
                        if nueva_cantidad > 0:
                            sale.actualizar_cantidad(producto_id, nueva_cantidad)
                            actualizar_sidebar()
                        else:
                            # Elimina el producto si la cantidad es 0 o negativa
                            sale.actualizar_cantidad(producto_id, 0)
                            actualizar_sidebar()
                    else:
                        pass        
                except ValueError:
                    # Si hay error, simplemente no hacemos nada (mantiene el valor anterior)
                    pass
            
            def actualizar_sidebar():
                items_carrito = []

                
                for producto, cantidad in sale.productos:
                    aumentar = partial(
                        actualizar_cantidad_producto,
                        producto_id=producto[0],
                        cambio=+1
                    )
                    disminuir = partial(
                        actualizar_cantidad_producto,
                        producto_id=producto[0],
                        cambio=-1
                    )
                    
                    cambiar_cantidad = partial(
                        cambiar_cantidad_producto,
                        producto_id=producto[0]
                    )
            
                    items_carrito.append(
                        crear_item_carrito(producto, cantidad, aumentar, disminuir, cambiar_cantidad)
                    )
                    
                sale._calcular_totales()
                
                # 1. Crear área desplazable (solo para productos)
                scroll_area = ft.ListView(
                    controls=[
                        ft.Text("Los productos que escanees o busques aparecerán aquí", size=12),
                        ft.Divider(height=1),
                        *items_carrito
                    ],
                    expand=True
                )
                total_controls = [
                    ft.Row(
                        [ft.Text(f"Subtotal: ${sale.subtotal:.2f}")],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ]
                
                # Solo mostrar descuento si es mayor a 0
                if sale.descuento > 0:
                    total_controls.append(
                        ft.Row(
                            [
                                ft.Text(
                                    f"Descuento ({sale.descuento_porcentaje}%): -${sale.descuento:.2f}", 
                                    color="red"
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    )
                
                total_controls.append(
                    ft.Row(
                        [ft.Text(f"Total: ${sale.total:.2f}", weight=ft.FontWeight.BOLD, size=30)],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
                
                # Resto de la función permanece igual...
                fixed_controls = ft.Column(
                    controls=[
                        ft.Divider(),
                        ft.FilledButton(
                            "Agregar descuento",
                            color='Black',
                            bgcolor='#FFCDFA',
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                            icon=ft.Icons.DISCOUNT,
                            icon_color='black',
                            on_click=lambda e: show_modal_descuento(page, sale, actualizar_sidebar),
                            disabled=len(sale.productos) == 0
                        ),
                        ft.Column(total_controls, spacing=5),
                        ft.Container(
                            content=ft.FilledButton(
                                "Continuar",
                                width=700,
                                height=50,
                                color='Black',
                                bgcolor='#FFCDFA',
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=7),
                                    text_style=ft.TextStyle(
                                        size=30,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ),
                                on_click=lambda e: show_modal_pago(
                                    page, 
                                    sale, 
                                    page.session.get("empleado_id"), 
                                    nuevo_pedido,
                                    actualizar_sidebar
                                ),
                                disabled=len(sale.productos) == 0
                            ),
                            alignment=ft.alignment.center,
                            expand=True
                        )
                    ],
                    spacing=10,
                    tight=True
                )
                # 3. Estructura final combinada
                sidebar.content = ft.Column(
                    controls=[
                        scroll_area,  # Parte desplazable
                        fixed_controls  # Parte fija
                    ],
                    spacing=0,
                    expand=True
                )
                sidebar.update()

            search_bar=ft.Container(
                bgcolor=ft.Colors.WHITE,
                alignment=ft.alignment.center,
                height=50,
                border_radius=15,
                content=ft.Row(
                    controls=[
                        ft.Container(width=5),
                        ft.Icon(ft.Icons.SEARCH),  
                        ft.TextField(
                            hint_text="Buscar...",
                            border=ft.InputBorder.NONE,
                            expand=True,
                            on_change=lambda e: actualizar_lista_productos(e.control.value)
                        )
                    ]
                )
            )
            
            

            def filtrar_productos(texto_busqueda="", criterio_orden="nombre"):
                productos = obtener_productos()  # Obtenemos todos los productos
            
                # Filtrado
                if texto_busqueda:
                    texto_busqueda = texto_busqueda.lower()
                    productos = [
                        p for p in productos 
                        if (texto_busqueda in p[1].lower() or  # Nombre
                            texto_busqueda in p[2].lower() or  # Marca
                            texto_busqueda in p[5].lower())    # Categoría
                    ]
            
                # Ordenamiento
                if criterio_orden == "nombre":
                    productos.sort(key=lambda x: x[1].lower())  # Índice 1 es nombre
                elif criterio_orden == "marca":
                    productos.sort(key=lambda x: x[2].lower())  # Índice 2 es marca
                elif criterio_orden == "categoria":
                    productos.sort(key=lambda x: x[5].lower())  # Índice 5 es categoría
            
                return productos

            def actualizar_lista_productos(texto_busqueda="", criterio_orden="nombre"):
                # Obtiene productos filtrados y ordenados
                productos = filtrar_productos(texto_busqueda, criterio_orden)
            
                # Reconstruye la lista
                lista.content.controls = [
                    crear_producto_tile(
                        producto,
                        lambda e, p=producto: (
                            sale.agregar_producto(p),
                            actualizar_sidebar()
                        )
                    )
                    for producto in productos
                ]
                lista.update()

            lista = ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                expand=True,
                content=ft.ListView(
                    controls=[
                        crear_producto_tile(
                            producto,
                            lambda e, p=producto: (
                                sale.agregar_producto(p),
                                actualizar_sidebar()
                            )
                        )
                        for producto in obtener_productos()
                    ]
                )
            )
            
            sidebar = ft.Container(
                alignment=ft.alignment.top_center,
                expand=3,
                padding=15,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                content=ft.Column(
                    controls=[
                        ft.Text("Los productos que escanees o busques aparecerán aquí", size=12),
                        ft.Divider(height=1)
                    ],
                    scroll="auto",
                    expand=True
                )
            )

            filter_text = ft.Text('Filtrar por: Nombre', size=16, weight=ft.FontWeight.W_600)
            def on_filter_selected(e):
                # Actualiza el texto del filtro
                filter_text.value = f"Filtrar por: {e.control.text}"
            
                # Determina el criterio de ordenamiento
                criterio = "nombre"  # Por defecto
                if e.control.text == "Marca":
                    criterio = "marca"
                elif e.control.text == "Categoria":
                    criterio = "categoria"
            
                # Actualiza la lista con el nuevo orden
                actualizar_lista_productos(criterio_orden=criterio)
                page.update()

            filtro=ft.Container( 
                content=ft.Row( 
                    controls=[
                        ft.Text('Listado de Productos', weight=ft.FontWeight.BOLD, size=20),
                        ft.Container(expand=True),
                        filter_text,
                        ft.PopupMenuButton(  
                            icon = "FILTER_LIST",
                            icon_color=ft.Colors.BLACK,
                            tooltip="Filtrar",
                            items=[
                                ft.PopupMenuItem(text="Nombre", on_click=on_filter_selected),
                                ft.PopupMenuItem(text="Categoria", on_click=on_filter_selected),
                                ft.PopupMenuItem(text="Marca", on_click=on_filter_selected)
                            ],
                        )
                    ]
                )
            )

            product_container = ft.Column(
                controls=[
                    search_bar,
                    filtro,
                    lista
                ],
                expand=7
            )

            main_container = ft.Row(
                controls=[
                    product_container,
                    sidebar
                ],
                spacing=40,
                expand=True
            ) 

            page.views.append(
                ft.View(
                    "/main",
                    [
                        # Aquí colocas TODOS tus controles actuales:
                        page.appbar,  # Tu AppBar original
                        main_container,  # Tu contenedor principal
                        ft.Row(
                            [
                                ft.Text(
                                    f"Iniciaste sesión como: {page.session.get('empleado_nombre')}",
                                    size=17,
                                    color=ft.Colors.BLACK,
                                    weight=ft.FontWeight.W_600
                                ),
                                ft.FilledButton(
                                "Cerrar sesion",
                                bgcolor='White',
                                color='Black',
                                style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=7)),   
                                on_click=on_logout
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ],
                    padding=ft.padding.only(left=40, top=40, right=40, bottom=10),
                    bgcolor=ft.Colors.PINK_100
                )
            )
        
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    # Configuración inicial del router
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")  # Inicia en el login

ft.app(target=main, assets_dir="assets")