import tkinter as tk
from decimal import Decimal, InvalidOperation
from fractions import Fraction

import customtkinter as ctk

from modules.ajuste import (
    construir_sistema,
    evaluar_polinomio,
    formatear_polinomio,
    resolver_coeficientes,
)
from modules.integracion import regla_del_trapecio
from modules.utils import formatear_a_decimal, formatear_a_fraccion


def parse_fraction(texto: str) -> Fraction:
    """Convierte un valor textual a Fraction."""
    valor = str(texto).strip()
    if not valor:
        raise ValueError("El valor no puede estar vacío.")

    try:
        return Fraction(valor)
    except ValueError:
        pass

    try:
        decimal = Decimal(valor)
        if not decimal.is_finite():
            raise ValueError(f'"{valor}" no es un número finito válido')
        return Fraction(decimal)
    except InvalidOperation as exc:
        raise ValueError(f'"{valor}" no es un número válido.') from exc


def validar_puntos(puntos):
    """Valida que los datos de entrada sean consistentes antes del cálculo."""
    if len(puntos) < 3:
        raise ValueError("Se requieren al menos 3 mediciones para calcular el balance.")

    horas = [hora for hora, _ in puntos]
    if len(set(horas)) != len(horas):
        raise ValueError("No pueden existir dos mediciones con la misma hora.")

    for hora, potencia in puntos:
        if not 0 <= int(hora) <= 23:
            raise ValueError("Cada hora debe estar entre 0 y 23.")
        if potencia == 0:
            continue


class BatteryEnergyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Balance de energía - Centro de datos")
        self.geometry("1280x900")
        self.minsize(1080, 700)
        self.configure(fg_color="#071521")

        self.points = []
        self.coefficients = None
        self.trapecios_usados = None
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        shell = ctk.CTkFrame(self, fg_color="#0b1727", corner_radius=28)
        shell.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_rowconfigure(2, weight=1)

        self._build_header(shell)

        self.tabview = ctk.CTkTabview(
            shell,
            fg_color="#0e1b2b",
            segmented_button_fg_color="#0b1727",
            segmented_button_selected_color="#2563eb",
            segmented_button_selected_hover_color="#1d4ed8",
            segmented_button_unselected_color="#15263a",
            segmented_button_unselected_hover_color="#1c334d",
            text_color="#dbe9ff",
            corner_radius=24,
            border_width=1,
            border_color="#1f2f46",
            command=self._on_tab_changed,
        )
        self.tabview.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=18, pady=(0, 18))

        calc_tab = self.tabview.add("Cálculo")
        graph_tab = self.tabview.add("Gráfica")
        calc_tab.grid_columnconfigure(0, weight=1)
        calc_tab.grid_columnconfigure(1, weight=1)
        calc_tab.grid_rowconfigure(0, weight=1)
        graph_tab.grid_columnconfigure(0, weight=1)
        graph_tab.grid_rowconfigure(1, weight=1)

        left_panel = ctk.CTkFrame(calc_tab, fg_color="#101d2d", corner_radius=24)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)
        left_panel.grid_columnconfigure(0, weight=1)

        right_panel = ctk.CTkFrame(calc_tab, fg_color="#101d2d", corner_radius=24)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        self._build_graph(graph_tab)
        self._build_form(left_panel)
        self._build_results(right_panel)

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 12))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        title_area = ctk.CTkFrame(header, fg_color="transparent")
        title_area.grid(row=0, column=0, sticky="w")

        titulo = ctk.CTkLabel(
            title_area,
            text="Balance energético del centro de datos",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#edf6ff",
        )
        titulo.grid(row=0, column=0, sticky="w")

        subtitulo = ctk.CTkLabel(
            title_area,
            text="Interpolación polinómica para estimar el cambio neto de energía",
            font=ctk.CTkFont(size=12),
            text_color="#9ec1eb",
        )
        subtitulo.grid(row=1, column=0, sticky="w", pady=(6, 0))

        badge = ctk.CTkFrame(header, fg_color="#11283b", corner_radius=16)
        badge.grid(row=0, column=1, sticky="e", padx=(10, 0))
        ctk.CTkLabel(
            badge,
            text="LIVE ANALYTICS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#8ae4ff",
            padx=16,
            pady=8,
        ).pack()

        cards = ctk.CTkFrame(parent, fg_color="transparent")
        cards.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 12))
        cards.grid_columnconfigure((0, 1, 2), weight=1)

        self.metric_points = self._metric_card(cards, "Puntos", "0", "#68d0ff", 0)
        self.metric_hours = self._metric_card(cards, "Rango", "0-24 h", "#4ade80", 1)
        self.metric_state = self._metric_card(cards, "Estado", "Sin cálculo", "#fbbf24", 2)

    def _metric_card(self, parent, title, value, color, col):
        frame = ctk.CTkFrame(parent, fg_color="#0d1a2a", corner_radius=18, border_width=1, border_color="#1c2d42")
        frame.grid(row=0, column=col, sticky="ew", padx=(0, 12))
        frame.grid_columnconfigure(0, weight=1)

        label_title = ctk.CTkLabel(frame, text=title, text_color="#9bb7d4", font=ctk.CTkFont(size=11))
        label_title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 0))

        value_label = ctk.CTkLabel(frame, text=value, text_color=color, font=ctk.CTkFont(size=24, weight="bold"))
        value_label.grid(row=1, column=0, sticky="w", padx=16, pady=(6, 16))
        return value_label

    def _build_form(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#0e1b2b", corner_radius=22, border_width=1, border_color="#1f2f46")
        card.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(6, weight=1)

        title = ctk.CTkLabel(
            card,
            text="Agregar mediciones",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#edf6ff",
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(10, 4))

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.grid(row=1, column=0, sticky="ew", padx=20, pady=(2, 4))
        fields.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(fields, text="Hora (0-23)", text_color="#dbe9ff", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.hour_var = ctk.StringVar(value="")
        self.hour_entry = ctk.CTkEntry(
            fields,
            textvariable=self.hour_var,
            placeholder_text="ej. 6",
            height=34,
            corner_radius=12,
            fg_color="#111d2b",
            border_color="#263b52",
            text_color="#edf6ff",
        )
        self.hour_entry.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(fields, text="Potencia (kW)", text_color="#dbe9ff", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(14, 0))
        self.power_var = ctk.StringVar(value="")
        self.power_entry = ctk.CTkEntry(
            fields,
            textvariable=self.power_var,
            placeholder_text="ej. 12.5 o -3.2",
            height=34,
            corner_radius=12,
            fg_color="#111d2b",
            border_color="#263b52",
            text_color="#edf6ff",
        )
        self.power_entry.grid(row=1, column=1, sticky="ew", pady=(10, 0))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=20, pady=(4, 2))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self.add_button = ctk.CTkButton(
            actions,
            text="Agregar medición",
            command=self._agregar_medicion,
            height=38,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=12,
        )
        self.add_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.clear_button = ctk.CTkButton(
            actions,
            text="Limpiar",
            command=self._limpiar_mediciones,
            height=38,
            fg_color="#1f2937",
            hover_color="#374151",
            corner_radius=12,
        )
        self.clear_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        trapecios = ctk.CTkFrame(card, fg_color="transparent")
        trapecios.grid(row=3, column=0, sticky="ew", padx=20, pady=(2, 4))
        trapecios.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(trapecios, text="Trapecios", text_color="#dbe9ff", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.trapecios_var = ctk.StringVar(value="6")
        self.trapecios_entry = ctk.CTkEntry(
            trapecios,
            textvariable=self.trapecios_var,
            width=120,
            height=34,
            corner_radius=12,
            fg_color="#111d2b",
            border_color="#263b52",
            text_color="#edf6ff",
        )
        self.trapecios_entry.grid(row=0, column=1, sticky="ew")

        self.calculate_button = ctk.CTkButton(
            card,
            text="Calcular balance",
            command=self._calcular,
            height=42,
            fg_color="#22c55e",
            hover_color="#16a34a",
            corner_radius=12,
        )
        self.calculate_button.grid(row=4, column=0, sticky="ew", padx=20, pady=(2, 6))

        self.status_label = ctk.CTkLabel(
            card,
            text="Aún no hay mediciones suficientes.",
            text_color="#9ad2ff",
            anchor="w",
            justify="left",
            wraplength=300,
        )
        self.status_label.grid(row=5, column=0, sticky="ew", padx=20, pady=0)

        self.points_container = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.points_container.grid(row=6, column=0, sticky="nsew", padx=20, pady=(0, 4))
        self.points_container.grid_columnconfigure(0, weight=1)

        self.bind("<Return>", lambda event: self._agregar_medicion())
        self.trapecios_entry.bind("<Return>", lambda event: self._calcular())
        self._render_points()

    def _build_results(self, parent):
        title = ctk.CTkLabel(
            parent,
            text="Resultados",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#edf6ff",
        )
        title.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        stats = ctk.CTkFrame(parent, fg_color="#0d1a2a", corner_radius=20, border_width=1, border_color="#243750")
        stats.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        stats.grid_columnconfigure((0, 1), weight=1)

        self.energy_value = ctk.CTkLabel(
            stats,
            text="0.00 kWh",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#7dd3fc",
        )
        self.energy_value.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))

        self.balance_label = ctk.CTkLabel(
            stats,
            text="Balance: neutro",
            font=ctk.CTkFont(size=16),
            text_color="#dfeafd",
        )
        self.balance_label.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 12))

        self.summary_label = ctk.CTkLabel(
            stats,
            text="Sin cálculo aún",
            text_color="#a9c3db",
            justify="left",
            wraplength=240,
        )
        self.summary_label.grid(row=0, column=1, rowspan=2, sticky="e", padx=18, pady=(18, 12))

        result_card = ctk.CTkFrame(
            parent,
            fg_color="#0d1a2a",
            corner_radius=20,
            border_width=1,
            border_color="#243750",
        )
        result_card.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        result_card.grid_columnconfigure(0, weight=1)
        result_card.grid_rowconfigure(1, weight=1)

        result_header = ctk.CTkFrame(result_card, fg_color="transparent")
        result_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
        result_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            result_header,
            text="Detalle del cálculo",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#edf6ff",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            result_header,
            text="Salida técnica",
            font=ctk.CTkFont(size=12),
            text_color="#8ec5ff",
            anchor="e",
        ).grid(row=0, column=1, sticky="e")

        self.result_text = ctk.CTkTextbox(
            result_card,
            width=500,
            height=260,
            fg_color="#081822",
            border_color="#1b3047",
            corner_radius=18,
            font=ctk.CTkFont(size=12),
            text_color="#dfeafd",
        )
        self.result_text.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.result_text.insert("0.0", "Aquí aparecerán los coeficientes, la función ajustada, el ancho de cada trapecio y la interpretación del balance.")
        self.result_text.configure(state="disabled")

        self._update_summary(0, "neutro", "Sin cálculo aún")

    def _build_graph(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(12, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Función ajustada y regla del trapecio",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#edf6ff",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.graph_info = ctk.CTkLabel(
            header,
            text="Sin cálculo aún",
            font=ctk.CTkFont(size=12),
            text_color="#9ec1eb",
            anchor="e",
        )
        self.graph_info.grid(row=0, column=1, sticky="e", padx=(12, 0))

        graph_card = ctk.CTkFrame(
            parent,
            fg_color="#0d1a2a",
            corner_radius=20,
            border_width=1,
            border_color="#243750",
        )
        graph_card.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        graph_card.grid_columnconfigure(0, weight=1)
        graph_card.grid_rowconfigure(0, weight=1)

        self.graph_canvas = tk.Canvas(
            graph_card,
            background="#081822",
            highlightthickness=0,
            bd=0,
        )
        self.graph_canvas.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.graph_canvas.bind("<Configure>", self._on_graph_resize)
        self._draw_graph()

    def _on_tab_changed(self):
        if getattr(self, "tabview", None) is not None and self.tabview.get() == "Gráfica":
            self.after_idle(self._draw_graph)

    def _on_graph_resize(self, _event=None):
        self._draw_graph()

    @staticmethod
    def _evaluar_float(coeficientes, hora):
        resultado = 0.0
        for coeficiente in reversed(coeficientes):
            resultado = resultado * hora + float(coeficiente)
        return resultado

    @staticmethod
    def _formatear_tick(valor):
        if abs(valor) >= 1000:
            return f"{valor:.0f}"
        texto = f"{valor:.2f}".rstrip("0").rstrip(".")
        return texto if texto not in ("", "-0") else "0"

    def _draw_graph(self):
        canvas = self.graph_canvas
        canvas.delete("all")

        ancho = canvas.winfo_width()
        alto = canvas.winfo_height()
        if ancho <= 1 or alto <= 1:
            return

        margen_izq, margen_der, margen_sup, margen_inf = 64, 24, 44, 46
        ancho_grafica = max(ancho - margen_izq - margen_der, 1)
        alto_grafica = max(alto - margen_sup - margen_inf, 1)

        def x_pixel(hora):
            return margen_izq + (hora / 24.0) * ancho_grafica

        coeficientes = self.coefficients
        trapecios = self.trapecios_usados
        muestras = max(240, int(ancho_grafica))

        valores_y = [0.0]
        valores_y.extend(float(potencia) for _, potencia in self.points)
        if coeficientes:
            for indice in range(muestras + 1):
                hora = 24.0 * indice / muestras
                valores_y.append(self._evaluar_float(coeficientes, hora))
        if coeficientes and trapecios:
            for indice in range(trapecios + 1):
                hora = 24.0 * indice / trapecios
                valores_y.append(self._evaluar_float(coeficientes, hora))

        minimo_y = min(valores_y)
        maximo_y = max(valores_y)
        if minimo_y == maximo_y:
            minimo_y -= 1.0
            maximo_y += 1.0
        margen_y = (maximo_y - minimo_y) * 0.1
        minimo_y -= margen_y
        maximo_y += margen_y

        def y_pixel(valor):
            return margen_sup + ((maximo_y - valor) / (maximo_y - minimo_y)) * alto_grafica

        for indice in range(7):
            hora = indice * 4.0
            x = x_pixel(hora)
            canvas.create_line(
                x, margen_sup, x, margen_sup + alto_grafica,
                fill="#142b3f", dash=(2, 4),
            )
            canvas.create_text(
                x, margen_sup + alto_grafica + 16,
                text=str(int(hora)),
                fill="#9ec1eb",
                font=("TkDefaultFont", 10),
            )

        for indice in range(6):
            valor = minimo_y + (maximo_y - minimo_y) * indice / 5
            y = y_pixel(valor)
            canvas.create_line(
                margen_izq, y, margen_izq + ancho_grafica, y,
                fill="#142b3f", dash=(2, 4),
            )
            canvas.create_text(
                margen_izq - 10, y,
                text=self._formatear_tick(valor),
                anchor="e",
                fill="#9ec1eb",
                font=("TkDefaultFont", 10),
            )

        canvas.create_rectangle(
            margen_izq, margen_sup,
            margen_izq + ancho_grafica, margen_sup + alto_grafica,
            outline="#243750",
        )
        if minimo_y < 0 < maximo_y:
            cero = y_pixel(0.0)
            canvas.create_line(
                margen_izq, cero,
                margen_izq + ancho_grafica, cero,
                fill="#4b6b8a", width=2,
            )

        if coeficientes is not None and trapecios:
            for indice in range(trapecios):
                hora_izq = 24.0 * indice / trapecios
                hora_der = 24.0 * (indice + 1) / trapecios
                potencia_izq = self._evaluar_float(coeficientes, hora_izq)
                potencia_der = self._evaluar_float(coeficientes, hora_der)
                canvas.create_polygon(
                    x_pixel(hora_izq), y_pixel(0.0),
                    x_pixel(hora_izq), y_pixel(potencia_izq),
                    x_pixel(hora_der), y_pixel(potencia_der),
                    x_pixel(hora_der), y_pixel(0.0),
                    fill="#1d4ed8",
                    stipple="gray25",
                    outline="#3b82f6",
                    width=1,
                )

        if coeficientes:
            puntos_curva = []
            for indice in range(muestras + 1):
                hora = 24.0 * indice / muestras
                puntos_curva.extend((
                    x_pixel(hora),
                    y_pixel(self._evaluar_float(coeficientes, hora)),
                ))
            canvas.create_line(
                *puntos_curva,
                fill="#38bdf8",
                width=3,
                joinstyle="round",
            )

        for hora, potencia in self.points:
            x = x_pixel(float(hora))
            y = y_pixel(float(potencia))
            canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                fill="#fbbf24",
                outline="#fff7ed",
                width=2,
            )
            etiqueta = f"({int(hora)}, {formatear_a_decimal(potencia)})"
            if x > margen_izq + ancho_grafica * 0.82:
                anclaje = "se"
                desplazamiento_x = -8
            else:
                anclaje = "sw"
                desplazamiento_x = 8
            desplazamiento_y = -8
            if y < margen_sup + 22:
                anclaje = "ne" if anclaje == "se" else "nw"
                desplazamiento_y = 8
            canvas.create_text(
                x + desplazamiento_x, y + desplazamiento_y,
                text=etiqueta,
                anchor=anclaje,
                fill="#fde68a",
                font=("TkDefaultFont", 10),
            )

        leyenda_y = 16
        canvas.create_line(
            margen_izq, leyenda_y,
            margen_izq + 26, leyenda_y,
            fill="#38bdf8", width=3,
        )
        canvas.create_text(
            margen_izq + 34, leyenda_y,
            text="f(t)", anchor="w",
            fill="#9ec1eb", font=("TkDefaultFont", 10),
        )
        leyenda_x = margen_izq + 90
        canvas.create_oval(
            leyenda_x - 5, leyenda_y - 5,
            leyenda_x + 5, leyenda_y + 5,
            fill="#fbbf24", outline="#fff7ed", width=2,
        )
        canvas.create_text(
            leyenda_x + 12, leyenda_y,
            text="Mediciones", anchor="w",
            fill="#9ec1eb", font=("TkDefaultFont", 10),
        )
        leyenda_x += 125
        canvas.create_rectangle(
            leyenda_x - 8, leyenda_y - 6,
            leyenda_x + 8, leyenda_y + 6,
            fill="#1d4ed8", stipple="gray25", outline="#3b82f6",
        )
        canvas.create_text(
            leyenda_x + 16, leyenda_y,
            text=f"Trapecios ({trapecios or 0})", anchor="w",
            fill="#9ec1eb", font=("TkDefaultFont", 10),
        )

        canvas.create_text(
            margen_izq + ancho_grafica / 2, alto - 12,
            text="Tiempo (h)",
            fill="#9ec1eb",
            font=("TkDefaultFont", 10),
        )
        canvas.create_text(
            16, margen_sup + alto_grafica / 2,
            text="Potencia (kW)",
            angle=90,
            fill="#9ec1eb",
            font=("TkDefaultFont", 10),
        )

        if coeficientes is None:
            if len(self.points) < 3:
                mensaje = "Agrega al menos 3 mediciones para graficar la función."
            else:
                mensaje = "Presiona «Calcular balance» para graficar la función y los trapecios."
            canvas.create_text(
                margen_izq + ancho_grafica / 2,
                margen_sup + alto_grafica / 2,
                text=mensaje,
                width=max(ancho_grafica - 30, 1),
                fill="#7f9fbd",
                font=("TkDefaultFont", 11),
            )

    def _render_points(self):
        self.coefficients = None
        self.trapecios_usados = None
        if hasattr(self, "graph_info"):
            self.graph_info.configure(text="Sin cálculo aún")

        for widget in self.points_container.winfo_children():
            widget.destroy()

        if not self.points:
            empty = ctk.CTkLabel(
                self.points_container,
                text="Sin mediciones por ahora.",
                text_color="#9db2d3",
                anchor="w",
            )
            empty.grid(row=0, column=0, sticky="ew", padx=10, pady=12)
            self.metric_points.configure(text="0")
            self.metric_hours.configure(text="0-24 h")
            self.metric_state.configure(text="Sin cálculo")
            self._draw_graph()
            return

        self.metric_points.configure(text=str(len(self.points)))
        horas = sorted(int(h) for h, _ in self.points)
        self.metric_hours.configure(text=f"{horas[0]}-{horas[-1]} h")

        for index, (hora, potencia) in enumerate(self.points):
            row = ctk.CTkFrame(self.points_container, fg_color="#1a2a3f", corner_radius=12)
            row.grid(row=index, column=0, sticky="ew", padx=4, pady=5)
            row.grid_columnconfigure(0, weight=1)

            label = ctk.CTkLabel(
                row,
                text=f"{index + 1}. Hora {int(hora)} → {formatear_a_decimal(potencia)} kW",
                text_color="#edf6ff",
                anchor="w",
                font=ctk.CTkFont(size=12),
            )
            label.grid(row=0, column=0, sticky="ew", padx=12, pady=10)

            delete_button = ctk.CTkButton(
                row,
                text="Eliminar",
                width=82,
                height=28,
                fg_color="#ef4444",
                hover_color="#dc2626",
                corner_radius=10,
                command=lambda i=index: self._remover_medicion(i),
            )
            delete_button.grid(row=0, column=1, padx=(0, 10), pady=8)

        self._draw_graph()

    def _agregar_medicion(self):
        try:
            hora_texto = self.hour_var.get().strip()
            potencia_texto = self.power_var.get().strip()
            if not hora_texto or not potencia_texto:
                raise ValueError("Completa la hora y la potencia antes de agregar la medición.")

            hora = int(hora_texto)
            if not 0 <= hora <= 23:
                raise ValueError("La hora debe estar entre 0 y 23.")

            if any(actual_hora == hora for actual_hora, _ in self.points):
                raise ValueError("Ya existe una medición para esa hora. Ingresa otra.")

            potencia = parse_fraction(potencia_texto)
            self.points.append((Fraction(hora), potencia))
            self.points.sort(key=lambda punto: punto[0])

            self.hour_var.set("")
            self.power_var.set("")
            self._render_points()
            self.status_label.configure(text=f"Medición agregada. Total de puntos: {len(self.points)}", text_color="#9ad2ff")
        except ValueError as exc:
            self.status_label.configure(text=f"Error: {exc}", text_color="#fca5a5")

    def _remover_medicion(self, index):
        if 0 <= index < len(self.points):
            del self.points[index]
            self._render_points()
            self.status_label.configure(text=f"Medición eliminada. Total de puntos: {len(self.points)}", text_color="#9ad2ff")

    def _limpiar_mediciones(self):
        self.points.clear()
        self._render_points()
        self.status_label.configure(text="Se limpiaron todas las mediciones.", text_color="#93c5fd")

    def _calcular(self):
        if len(self.points) < 3:
            self.status_label.configure(text="Se requieren al menos 3 mediciones para poder calcular.", text_color="#fca5a5")
            return

        try:
            trapecios = int(self.trapecios_var.get().strip())
            if trapecios <= 0:
                raise ValueError("El número de trapecios debe ser mayor que cero.")
        except ValueError:
            self.status_label.configure(text="El número de trapecios debe ser un entero positivo.", text_color="#fca5a5")
            return

        try:
            validar_puntos(self.points)
            matriz = construir_sistema(self.points)
            coeficientes = resolver_coeficientes(matriz)
            energia = regla_del_trapecio(
                lambda t: evaluar_polinomio(coeficientes, t),
                Fraction(0),
                Fraction(24),
                trapecios,
            )

            ancho = Fraction(24) / trapecios
            funcion = formatear_polinomio(coeficientes)
            self.coefficients = coeficientes
            self.trapecios_usados = trapecios
            self.graph_info.configure(text=f"Trapecios: {trapecios}")
            texto = [
                "=== Ajuste polinómico ===",
                f"Sistema generado con {len(self.points)} mediciones.",
                "",
                "Matriz aumentada:",
            ]

            for fila in matriz:
                texto.append("  " + "  ".join(str(formatear_a_fraccion(valor)) for valor in fila))

            texto.extend(["", "Coeficientes (de menor a mayor grado):"])
            for i, coeficiente in enumerate(coeficientes):
                texto.append(f"  a{i} = {formatear_a_fraccion(coeficiente)} ≈ {formatear_a_decimal(coeficiente)}")

            texto.extend([
                "",
                f"Función ajustada: f(t) = {funcion}",
                f"Δt = {formatear_a_decimal(ancho)} h",
                f"Energía neta = {formatear_a_fraccion(energia)} kWh ≈ {formatear_a_decimal(energia)} kWh",
                "",
                "Interpretación del balance:",
            ])

            if energia > 0:
                texto.append(f"La batería terminó con {formatear_a_decimal(energia)} kWh más que su carga inicial.")
                self._update_summary(energia, "positivo", "Predominó la carga")
            elif energia < 0:
                texto.append(f"La batería terminó con {formatear_a_decimal(abs(energia))} kWh menos que su carga inicial.")
                self._update_summary(energia, "negativo", "Predominó la descarga")
            else:
                texto.append("La batería terminó con la misma carga que al inicio del día.")
                self._update_summary(0, "neutro", "Balance nulo")

            self.result_text.configure(state="normal")
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "\n".join(texto))
            self.result_text.configure(state="disabled")
            self.status_label.configure(text="Cálculo realizado correctamente.", text_color="#86efac")
            self.metric_state.configure(text="Listo")
            self._draw_graph()
        except ValueError as exc:
            self.status_label.configure(text=f"Error: {exc}", text_color="#fca5a5")
            self.result_text.configure(state="normal")
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"Se produjo un error: {exc}")
            self.result_text.configure(state="disabled")
            self.metric_state.configure(text="Error")

    def _update_summary(self, energia, estado, texto):
        valor = formatear_a_decimal(abs(energia)) if energia != 0 else "0"
        self.energy_value.configure(text=f"{formatear_a_decimal(energia)} kWh")

        if estado == "positivo":
            self.energy_value.configure(text_color="#7dd3fc")
            self.balance_label.configure(text=f"Balance: positivo ({valor} kWh)", text_color="#86efac")
            self.metric_state.configure(text="Carga")
        elif estado == "negativo":
            self.energy_value.configure(text_color="#fca5a5")
            self.balance_label.configure(text=f"Balance: negativo ({valor} kWh)", text_color="#fca5a5")
            self.metric_state.configure(text="Descarga")
        else:
            self.energy_value.configure(text_color="#dfeafd")
            self.balance_label.configure(text="Balance: neutro", text_color="#dfeafd")
            self.metric_state.configure(text="Neutro")

        self.summary_label.configure(text=texto, text_color="#dbeafe")


if __name__ == "__main__":
    app = BatteryEnergyApp()
    app.mainloop()
