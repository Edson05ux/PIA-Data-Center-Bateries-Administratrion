import customtkinter as ctk
from decimal import Decimal, InvalidOperation
from fractions import Fraction

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
        self.geometry("1280x820")
        self.minsize(1080, 700)
        self.configure(fg_color="#071521")

        self.points = []
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        shell = ctk.CTkFrame(self, fg_color="#0b1727", corner_radius=28)
        shell.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_rowconfigure(1, weight=1)

        self._build_header(shell)

        left_panel = ctk.CTkFrame(shell, fg_color="#101d2d", corner_radius=24)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(18, 10), pady=(0, 18))
        left_panel.grid_columnconfigure(0, weight=1)

        right_panel = ctk.CTkFrame(shell, fg_color="#101d2d", corner_radius=24)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 18), pady=(0, 18))
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

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

        title = ctk.CTkLabel(
            card,
            text="Agregar mediciones",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#edf6ff",
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 10))

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.grid(row=1, column=0, sticky="ew", padx=20, pady=(8, 10))
        fields.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(fields, text="Hora (0-23)", text_color="#dbe9ff", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.hour_var = ctk.StringVar(value="")
        self.hour_entry = ctk.CTkEntry(
            fields,
            textvariable=self.hour_var,
            placeholder_text="ej. 6",
            height=38,
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
            height=38,
            corner_radius=12,
            fg_color="#111d2b",
            border_color="#263b52",
            text_color="#edf6ff",
        )
        self.power_entry.grid(row=1, column=1, sticky="ew", pady=(14, 0))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 8))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self.add_button = ctk.CTkButton(
            actions,
            text="Agregar medición",
            command=self._agregar_medicion,
            height=42,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=12,
        )
        self.add_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.clear_button = ctk.CTkButton(
            actions,
            text="Limpiar",
            command=self._limpiar_mediciones,
            height=42,
            fg_color="#1f2937",
            hover_color="#374151",
            corner_radius=12,
        )
        self.clear_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        trapecios = ctk.CTkFrame(card, fg_color="transparent")
        trapecios.grid(row=3, column=0, sticky="ew", padx=20, pady=(6, 10))
        trapecios.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(trapecios, text="Trapecios", text_color="#dbe9ff", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.trapecios_var = ctk.StringVar(value="6")
        self.trapecios_entry = ctk.CTkEntry(
            trapecios,
            textvariable=self.trapecios_var,
            width=120,
            height=38,
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
            height=46,
            fg_color="#22c55e",
            hover_color="#16a34a",
            corner_radius=12,
        )
        self.calculate_button.grid(row=4, column=0, sticky="ew", padx=20, pady=(8, 14))

        self.status_label = ctk.CTkLabel(
            card,
            text="Aún no hay mediciones suficientes.",
            text_color="#9ad2ff",
            anchor="w",
            justify="left",
            wraplength=300,
        )
        self.status_label.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))

        self.points_container = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.points_container.grid(row=6, column=0, sticky="nsew", padx=20, pady=(0, 18))
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
            height=420,
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

    def _render_points(self):
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
