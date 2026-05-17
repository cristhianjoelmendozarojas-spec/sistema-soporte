import base64
import io
import os
from io import BytesIO
from fpdf import FPDF
from datetime import datetime


class ActaPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', align='C')

    def acta_asignacion(self, asignacion, detalles):
        self.alias_nb_pages()
        self.set_auto_page_break(auto=True, margin=20)

        w = self.w
        m = 10
        usable = w - 2 * m

        # ── HEADER ──
        self.set_font('Helvetica', 'B', 9)
        self.cell(usable * 0.35, 5, 'AREA DE SOPORTE TECNICO', 'L', 0, 'L')
        self.cell(usable * 0.30, 5, '', 0, 0, 'C')
        self.set_font('Helvetica', '', 7)
        self.cell(usable * 0.35, 5, f'Fecha: {datetime.now().strftime("%d/%m/%Y")}', 'R', 1, 'R')

        self.set_font('Helvetica', 'B', 7)
        self.cell(usable * 0.35, 4, 'COMPUTADORA / LAPTOP', 'L', 0, 'L')

        self.set_font('Helvetica', 'B', 11)
        self.cell(usable * 0.30, 9, 'ASIGNACION', 0, 0, 'C')

        self.set_font('Helvetica', '', 7)
        resp_text = f'Responsable: {asignacion.created_by.get_full_name() or asignacion.created_by.username}'
        self.cell(usable * 0.35, 4, resp_text, 'R', 1, 'R')

        self.cell(usable * 0.35, 4, '', 'L', 0, 'L')
        self.set_font('Helvetica', 'B', 7)
        self.cell(usable * 0.30, 6, 'ACTA DE ASIGNACION DE EQUIPO', 0, 0, 'C')
        self.set_font('Helvetica', '', 7)
        area = asignacion.employee.departamento
        self.cell(usable * 0.35, 4, f'Area: {area}', 'R', 1, 'R')

        self.cell(usable * 0.35, 4, '', 'L', 0, 'L')
        self.set_font('Helvetica', 'B', 12)
        self.cell(usable * 0.30, 7, asignacion.codigo, 0, 0, 'C')
        self.set_font('Helvetica', '', 7)
        self.cell(usable * 0.35, 4, f'Fecha Acta: {asignacion.fecha_asignacion.strftime("%d/%m/%Y")}', 'R', 1, 'R')

        self.cell(usable * 0.35, 4, '', 'L', 0, 'L')
        self.set_font('Helvetica', 'B', 7)
        tipo = 'ADM' if asignacion.created_by.is_staff else 'STD'
        self.cell(usable * 0.30, 5, f'TIPO: {tipo}', 0, 0, 'C')
        self.set_font('Helvetica', '', 7)
        self.cell(usable * 0.35, 4, f'Empleado: {asignacion.employee.apellido}, {asignacion.employee.nombre}', 'R', 1, 'R')

        self.cell(usable * 0.35, 4, '', 'L', 0, 'L')
        self.cell(usable * 0.30, 4, '', 0, 0, 'C')
        self.set_font('Helvetica', '', 7)
        self.cell(usable * 0.35, 4, f'Cedula: {asignacion.employee.cedula}     Cargo: {asignacion.employee.cargo}', 'R', 1, 'R')

        self.ln(3)

        # ── EQUIPMENT TABLE ──
        col_w = [usable * 0.22, usable * 0.17, usable * 0.18, usable * 0.18, usable * 0.25]
        headers = ['Equipo', 'Marca', 'Modelo', 'Serie', 'Estado']

        self.set_font('Helvetica', 'B', 7)
        self.set_fill_color(230, 230, 230)
        for i, h in enumerate(headers):
            self.cell(col_w[i], 6, h, 1, 0, 'C', True)
        self.ln()

        self.set_font('Helvetica', '', 7)
        for d in detalles:
            eq = d.equipment
            row = [
                eq.codigo_patrimonial,
                eq.marca,
                eq.modelo,
                eq.numero_serie,
                d.get_estado_entrega_display()
            ]
            max_h = 6
            for i, val in enumerate(row):
                self.cell(col_w[i], max_h, val[:35], 1, 0, 'C')
            self.ln()

        self.ln(3)

        # ── COMPONENTES ──
        for d in detalles:
            if d.componentes_data:
                if d.tipo_equipo == 'pc':
                    comp_headers = ['Componente', 'Marca', 'Modelo', 'Capacidad', 'Serie', 'Estado']
                    comp_col_w = [usable * 0.16, usable * 0.16, usable * 0.16, usable * 0.16, usable * 0.16, usable * 0.18]
                elif d.tipo_equipo == 'laptop':
                    comp_headers = ['Componente', 'Marca', 'Modelo', 'SSD', 'HDD', 'RAM', 'Serie', 'Estado']
                    comp_col_w = [usable * 0.14, usable * 0.12, usable * 0.12, usable * 0.12, usable * 0.12, usable * 0.12, usable * 0.12, usable * 0.12]
                else:
                    comp_headers = ['Componente', 'Marca', 'Modelo', 'Serie', 'Estado']
                    comp_col_w = [usable * 0.20, usable * 0.20, usable * 0.20, usable * 0.20, usable * 0.20]

                self.set_font('Helvetica', 'B', 6)
                self.set_fill_color(245, 245, 245)
                for i, h in enumerate(comp_headers):
                    self.cell(comp_col_w[i], 5, h, 1, 0, 'C', True)
                self.ln()

                self.set_font('Helvetica', '', 6)
                for c in d.componentes_data:
                    if d.tipo_equipo == 'pc':
                        vals = [
                            c.get('nombre', '')[:30],
                            c.get('marca', '')[:25],
                            c.get('modelo', '')[:25],
                            c.get('capacidad', '')[:15],
                            c.get('serie', '')[:25],
                            c.get('estado', '')[:15],
                        ]
                    elif d.tipo_equipo == 'laptop':
                        vals = [
                            c.get('nombre', '')[:30],
                            c.get('marca', '')[:20],
                            c.get('modelo', '')[:20],
                            c.get('ssd', '')[:15],
                            c.get('hdd', '')[:15],
                            c.get('memoria_ram', '')[:15],
                            c.get('serie', '')[:20],
                            c.get('estado', '')[:12],
                        ]
                    else:
                        vals = [
                            c.get('nombre', '')[:30],
                            c.get('marca', '')[:25],
                            c.get('modelo', '')[:25],
                            c.get('serie', '')[:25],
                            c.get('estado', '')[:15],
                        ]
                    for i, val in enumerate(vals):
                        self.cell(comp_col_w[i], 5, val, 1, 0, 'C')
                    self.ln()
                self.ln(2)

        # ── MOTIVO ──
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 5, 'Motivo:', 0, 1)
        self.set_font('Helvetica', '', 7)
        self.multi_cell(0, 4, asignacion.motivo)

        if asignacion.observaciones:
            self.ln(2)
            self.set_font('Helvetica', 'B', 8)
            self.cell(0, 5, 'Observaciones:', 0, 1)
            self.set_font('Helvetica', '', 7)
            self.multi_cell(0, 4, asignacion.observaciones)

        self.ln(5)

        # ── SIGNATURES ──
        y_sig = self.get_y()
        self.line(m, y_sig, w - m, y_sig)
        self.ln(1)
        self.set_font('Helvetica', '', 7)
        self.cell(usable * 0.5, 4, 'Responsable Soporte Tecnico', 0, 0, 'C')
        self.cell(usable * 0.5, 4, 'Coordinador TI', 0, 1, 'C')

        # Firma de Soporte Tecnico
        x_left = m
        x_center = m + usable * 0.25
        img_added = False
        try:
            firma = asignacion.created_by.firma
            if firma.imagen and os.path.exists(firma.imagen.path):
                self.image(firma.imagen.path, x=x_center - 20, y=self.get_y(), w=40, h=15)
                self.ln(16)
                img_added = True
            elif firma.datos_firma:
                raw = firma.datos_firma
                if ',' in raw:
                    raw = raw.split(',', 1)[1]
                img_data = base64.b64decode(raw)
                img_io = io.BytesIO(img_data)
                self.image(img_io, x=x_center - 20, y=self.get_y(), w=40, h=15)
                self.ln(16)
                img_added = True
        except Exception:
            pass

        if not img_added:
            self.ln(8)

        self.set_font('Helvetica', 'B', 8)
        nombre_resp = asignacion.created_by.get_full_name() or asignacion.created_by.username
        self.cell(usable * 0.5, 5, nombre_resp, 0, 0, 'C')
        self.cell(usable * 0.5, 5, '________________________', 0, 1, 'C')

        return self


def generar_pdf_asignacion(asignacion, request):
    from .models import AsignacionDetalle
    detalles = AsignacionDetalle.objects.filter(asignacion=asignacion).select_related('equipment')

    pdf = ActaPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.acta_asignacion(asignacion, detalles)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer
