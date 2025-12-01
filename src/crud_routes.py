from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from src.database import Producto as DBProducto, SessionLocal
from src.schemas import Producto, ProductoCreate, ProductoUpdate
from typing import List

router = APIRouter(prefix="/api", tags=["productos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    """Panel de administración en HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Gestión de Productos</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f6f7fb;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1300px;
                margin: 0 auto;
                background: #fff;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(60, 72, 88, 0.12);
                overflow: hidden;
            }
            /* Header */
            .header {
                background: #f6f7fb;
                color: #2d2d2d;
                padding: 40px 30px;
                text-align: center;
                border-bottom: 1px solid #e0e0e0;
            }
            .header h1 { font-size: 2.5em; font-weight: 600; margin-bottom: 10px; }
            .header p { opacity: 0.8; font-size: 1.1em; }
            /* Contenido */
            .content { padding: 30px; }
            /* Navegación */
            .nav {
                display: flex;
                gap: 0;
                margin-bottom: 30px;
                background: #f3f4f8;
                border-radius: 12px;
                padding: 5px;
                border: 1px solid #e0e0e0;
            }
            .nav button {
                flex: 1;
                background: transparent;
                border: none;
                padding: 15px 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                color: #444;
                transition: all 0.3s ease;
                border-radius: 8px;
            }
            .nav button:hover {
                background: #e6eaff;
                color: #2d5be3;
            }
            .nav button.active {
                background: #2d5be3;
                color: #fff;
                box-shadow: 0 2px 8px rgba(45, 91, 227, 0.10);
            }
            /* Secciones */
            .section {
                display: none;
                animation: fadeIn 0.4s ease;
            }
            .section.active { display: block; }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(15px); }
                to { opacity: 1; transform: translateY(0); }
            }
            h2 {
                color: #2d5be3;
                margin-bottom: 25px;
                font-size: 1.8em;
                font-weight: 600;
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 15px;
            }
            .form-group {
                margin-bottom: 18px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #222;
                font-weight: 600;
                font-size: 0.95em;
            }
            input, textarea, select {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: all 0.3s ease;
                font-family: inherit;
                background: #f9fafd;
            }
            input:focus, textarea:focus, select:focus {
                outline: none;
                border-color: #2d5be3;
                box-shadow: 0 0 0 2px #e6eaff;
                background: #fff;
            }
            textarea {
                resize: vertical;
                min-height: 100px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
            }
            /* Botones */
            .btn-group {
                display: flex;
                gap: 10px;
                margin-top: 25px;
            }
            button {
                background: #2d5be3;
                color: #fff;
                padding: 12px 28px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 15px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(45, 91, 227, 0.10);
            }
            button:hover {
                background: #1a3e8a;
                box-shadow: 0 4px 16px rgba(45, 91, 227, 0.13);
            }
            button:active { transform: translateY(0); }
            button.danger {
                background: #f5576c;
                box-shadow: 0 2px 8px rgba(245, 87, 108, 0.10);
            }
            button.danger:hover {
                background: #c82333;
                box-shadow: 0 4px 16px rgba(245, 87, 108, 0.13);
            }
            /* Tabla */
            .table-wrapper {
                overflow-x: auto;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                background: #fff;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }
            th {
                background: #f3f4f8;
                color: #2d5be3;
                font-weight: 600;
                font-size: 0.95em;
            }
            tr:hover {
                background: #f6f7fb;
            }
            .actions {
                white-space: nowrap;
                display: flex;
                gap: 8px;
            }
            .actions button {
                margin-right: 0;
                padding: 8px 12px;
                font-size: 12px;
            }
            /* Alertas */
            .alert {
                padding: 15px 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                display: none;
                border-left: 4px solid;
                animation: slideDown 0.3s ease;
            }
            .alert.show { display: block; }
            @keyframes slideDown {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .alert-success {
                background: #eafaf1;
                color: #1e5d1e;
                border-left-color: #28a745;
            }
            .alert-error {
                background: #fce7e7;
                color: #721c24;
                border-left-color: #f5576c;
            }
            /* Modal */
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.12);
                overflow-y: auto;
                backdrop-filter: blur(2px);
            }
            .modal.show { display: block; }
            .modal-content {
                background: #fff;
                margin: 5% auto;
                padding: 35px;
                border-radius: 15px;
                width: 90%;
                max-width: 650px;
                box-shadow: 0 8px 32px rgba(60, 72, 88, 0.12);
                animation: modalSlide 0.3s ease;
            }
            @keyframes modalSlide {
                from { transform: translateY(-50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            .close {
                color: #999;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                transition: color 0.3s;
            }
            .close:hover {
                color: #2d5be3;
            }
            .reload-btn {
                margin-bottom: 15px;
            }
            .empty-state {
                text-align: center;
                padding: 40px;
                color: #999;
            }
            .empty-state p { font-size: 1.1em; }
            
            /* Galería de productos */
            .productos-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .producto-card {
                background: #fff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                overflow: hidden;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            .producto-card:hover {
                box-shadow: 0 8px 24px rgba(0,0,0,0.12);
                transform: translateY(-2px);
            }
            .producto-imagen {
                width: 100%;
                height: 180px;
                background: #f9fafd;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            .producto-imagen img {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
            }
            .producto-info {
                padding: 15px;
            }
            .producto-codigo {
                font-weight: 600;
                color: #2d5be3;
                font-size: 0.9em;
            }
            .producto-nombre {
                font-weight: 600;
                color: #222;
                margin: 8px 0;
                font-size: 0.95em;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
            .producto-precio {
                color: #2d5be3;
                font-weight: 700;
                font-size: 1.1em;
                margin: 8px 0;
            }
            .producto-meta {
                display: flex;
                gap: 8px;
                margin: 10px 0;
                flex-wrap: wrap;
            }
            .producto-badge {
                font-size: 0.75em;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
            }
            .producto-acciones {
                display: flex;
                gap: 8px;
                margin-top: 12px;
            }
            .producto-acciones button {
                flex: 1;
                padding: 8px 12px;
                font-size: 12px;
                margin: 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛠️ Panel de Administración</h1>
                <p>Gestión moderna de productos y catálogos</p>
            </div>
            
            <div class="content">
            
            <div id="alertContainer"></div>
            
            <!-- Navegación -->
            <div class="nav">
                <button class="nav-btn active" onclick="mostrarSeccion('crear')">➕ Crear Producto</button>
                <button class="nav-btn" onclick="mostrarSeccion('listar')">📋 Productos Registrados</button>
            </div>
            
            <!-- Sección: Crear Producto -->
            <div id="crear" class="section active">
                <h2>➕ Crear Nuevo Producto</h2>
                <form id="crearForm">
                    <div class="grid">
                        <div class="form-group">
                            <label>Código *</label>
                            <input type="text" name="codigo" required placeholder="ej: CELCEL0091">
                        </div>
                        <div class="form-group">
                            <label>Nombre *</label>
                            <input type="text" name="nombre" required placeholder="ej: SAMSUNG GALAXY A06">
                        </div>
                        <div class="form-group" style="grid-column: 1/-1;">
                            <label>Descripción</label>
                            <textarea name="descripcion" placeholder="ej: 128 GB - 4 GB RAM"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Precio *</label>
                            <input type="number" name="precio" step="0.01" required placeholder="ej: 949.00">
                        </div>
                        <div class="form-group">
                            <label>Categoría *</label>
                            <select name="categoria" required>
                                <option value="">Seleccionar...</option>
                                <option>celulares</option>
                                <option>laptops</option>
                                <option>televisores</option>
                                <option>refrigeradoras</option>
                                <option>lavadoras</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Segmento *</label>
                            <select name="segmento" required>
                                <option value="fnb">FNB</option>
                                <option value="gaso">GASO</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Estado *</label>
                            <select name="estado" required>
                                <option value="disponible">Disponible</option>
                                <option value="no disponible">No Disponible</option>
                                <option value="agotado">Agotado</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Stock</label>
                            <select name="stock">
                                <option value="true">Sí</option>
                                <option value="false">No</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Imagen Listado</label>
                            <input type="text" name="imagen_listado" placeholder="catalogos/2025/fnb/noviembre/1-celulares/listado/01.png">
                        </div>
                        <div class="form-group">
                            <label>Imagen Características</label>
                            <input type="text" name="imagen_caracteristicas" placeholder="catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/01.png">
                        </div>
                        <div class="form-group">
                            <label>Mes *</label>
                            <input type="text" name="mes" required placeholder="noviembre">
                        </div>
                        <div class="form-group">
                            <label>Año *</label>
                            <input type="number" name="ano" required placeholder="2025">
                        </div>
                        <div class="form-group" style="grid-column: 1/-1;">
                            <label>Cuotas (JSON) *</label>
                            <textarea name="cuotas" required placeholder='{"3": 338.85, "6": 178.87, "9": 125.7, "12": 99.24}'></textarea>
                        </div>
                    </div>
                    <div class="btn-group">
                        <button type="submit">✅ Crear Producto</button>
                    </div>
                </form>
            </div>
            
            <!-- Sección: Productos Registrados -->
            <div id="listar" class="section">
                <h2>📋 Productos Registrados</h2>
                <button class="reload-btn" onclick="cargarProductos()">🔄 Recargar</button>
                <div id="productosGaleria" class="productos-grid">
                </div>
            </div>
        </div>

        <!-- Modal para editar -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="cerrarModal()">&times;</span>
                <h2>✏️ Editar Producto</h2>
                <form id="editForm">
                    <div class="grid" id="editFormFields"></div>
                    <div class="btn-group">
                        <button type="submit">💾 Guardar Cambios</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            let productoEnEdicion = null;

            // Alternar secciones
            function mostrarSeccion(seccion) {
                // Ocultar todas las secciones
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
                
                // Mostrar la sección seleccionada
                const sectionEl = document.getElementById(seccion);
                if (sectionEl) {
                    sectionEl.classList.add('active');
                }
                
                // Activar el botón correspondiente
                const botones = document.querySelectorAll('.nav-btn');
                botones.forEach((btn, idx) => {
                    if ((seccion === 'crear' && idx === 0) || (seccion === 'listar' && idx === 1)) {
                        btn.classList.add('active');
                    }
                });
                
                // Si es listar, cargar productos
                if (seccion === 'listar') {
                    setTimeout(() => {
                        cargarProductos();
                    }, 100);
                }
            }

            document.getElementById('crearForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                await crearProducto();
            });

            document.getElementById('editForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                await guardarEdicion();
            });

            async function crearProducto() {
                try {
                    const formData = new FormData(document.getElementById('crearForm'));
                    const cuotas = JSON.parse(formData.get('cuotas'));
                    
                    const data = {
                        codigo: formData.get('codigo'),
                        nombre: formData.get('nombre'),
                        descripcion: formData.get('descripcion'),
                        precio: parseFloat(formData.get('precio')),
                        categoria: formData.get('categoria'),
                        imagen_listado: formData.get('imagen_listado'),
                        imagen_caracteristicas: formData.get('imagen_caracteristicas'),
                        cuotas: cuotas,
                        mes: formData.get('mes'),
                        ano: parseInt(formData.get('ano')),
                        segmento: formData.get('segmento'),
                        estado: formData.get('estado'),
                        stock: formData.get('stock') === 'true'
                    };

                    const response = await fetch('/api/productos', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });

                    if (response.ok) {
                        mostrarAlerta('✅ Producto creado exitosamente', 'success');
                        document.getElementById('crearForm').reset();
                        setTimeout(() => {
                            mostrarSeccion('listar');
                        }, 1500);
                    } else {
                        const error = await response.json();
                        mostrarAlerta('❌ Error: ' + (error.detail || 'Error desconocido'), 'error');
                    }
                } catch(e) {
                    mostrarAlerta('❌ Error: ' + e.message, 'error');
                }
            }

            async function cargarProductos() {
                try {
                    const response = await fetch('/api/productos');
                    if (!response.ok) {
                        mostrarAlerta('❌ Error al obtener productos', 'error');
                        return;
                    }
                    const productos = await response.json();
                    
                    const galeria = document.getElementById('productosGaleria');
                    if (!galeria) {
                        console.error('No se encontró elemento productosGaleria');
                        return;
                    }
                    galeria.innerHTML = '';
                    
                    if (!productos || productos.length === 0) {
                        galeria.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #999;">📭 No hay productos registrados</div>';
                        return;
                    }
                    
                    productos.forEach(p => {
                        try {
                            const estadoColor = p.estado === 'disponible' ? '#d4edda' : '#fce7e7';
                            const estadoTextColor = p.estado === 'disponible' ? '#1e5d1e' : '#721c24';
                            const segmentoColor = p.segmento === 'fnb' ? '#cfe2ff' : '#fff3cd';
                            const segmentoTextColor = p.segmento === 'fnb' ? '#084298' : '#664d03';
                            
                            const imagenUrl = p.imagen_listado ? '/ver-ruta/' + p.imagen_listado : '';
                            
                            const card = document.createElement('div');
                            card.className = 'producto-card';
                            card.innerHTML = `
                                <div class="producto-imagen" id="img-${p.id}">
                                    ${imagenUrl ? `<img src="${imagenUrl}" alt="${p.nombre}" style="width: 100%; height: 100%; object-fit: contain; border-radius: 8px; border: 1px solid #e0e0e0;">` : '<div style="display: flex; align-items: center; justify-content: center; height: 100%; width: 100%; font-size: 0.9em; color: #999; border: 2px dashed #d0d0d0; border-radius: 8px;">Sin imagen</div>'}
                                </div>
                                <div class="producto-info">
                                    <div class="producto-codigo">${p.codigo}</div>
                                    <div class="producto-nombre">${p.nombre}</div>
                                    <div class="producto-precio">S/. ${p.precio.toFixed(2)}</div>
                                    <div class="producto-meta">
                                        <span class="producto-badge" style="background: ${segmentoColor}; color: ${segmentoTextColor};">${p.segmento.toUpperCase()}</span>
                                        <span class="producto-badge" style="background: ${estadoColor}; color: ${estadoTextColor};">${p.estado}</span>
                                    </div>
                                    <div class="producto-acciones">
                                        <button onclick="abrirDetalle(${p.id})">👁️ Ver</button>
                                        <button onclick="abrirEditModal(${p.id})">✏️ Editar</button>
                                        <button class="danger" onclick="eliminarProducto(${p.id})">🗑️ Eliminar</button>
                                    </div>
                                </div>
                            `;
                            galeria.appendChild(card);
                            
                            // Manejar error de carga de imagen
                            if (imagenUrl) {
                                const img = card.querySelector('img');
                                if (img) {
                                    img.onerror = function() {
                                        const container = document.getElementById('img-' + p.id);
                                        if (container) {
                                            container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; width: 100%; font-size: 0.9em; color: #999; border: 2px dashed #d0d0d0; border-radius: 8px;">Sin imagen</div>';
                                        }
                                    };
                                }
                            }
                        } catch(e) {
                            console.error('Error procesando producto:', p, e);
                        }
                    });
                } catch(e) {
                    console.error('Error en cargarProductos:', e);
                    mostrarAlerta('❌ Error: ' + e.message, 'error');
                }
            }

            async function abrirDetalle(id) {
                try {
                    const response = await fetch('/api/productos/' + id);
                    const producto = await response.json();
                    
                    let html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; align-items: start;">';
                    
                    // Imagen de listado
                    html += '<div><h4 style="margin-bottom: 12px; color: #2d5be3;">📸 Imagen Listado</h4>';
                    if (producto.imagen_listado && producto.imagen_listado.trim() !== '') {
                        html += `<div id="img-listado" style="width: 100%; height: 300px; background: #f9fafd; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                                    <img src="/ver-ruta/${producto.imagen_listado}" style="width: 100%; height: 100%; object-fit: contain; border-radius: 12px; border: 1px solid #e0e0e0; display: block;">
                                </div>`;
                    } else {
                        html += '<div style="width: 100%; height: 300px; background: #f9fafd; border: 2px dashed #d0d0d0; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 1em;">Sin imagen</div>';
                    }
                    html += '</div>';
                    
                    // Imagen de características
                    html += '<div><h4 style="margin-bottom: 12px; color: #2d5be3;">📸 Imagen Características</h4>';
                    if (producto.imagen_caracteristicas && producto.imagen_caracteristicas.trim() !== '') {
                        html += `<div id="img-caracteristicas" style="width: 100%; height: 300px; background: #f9fafd; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                                    <img src="/ver-ruta/${producto.imagen_caracteristicas}" style="width: 100%; height: 100%; object-fit: contain; border-radius: 12px; border: 1px solid #e0e0e0; display: block;">
                                </div>`;
                    } else {
                        html += '<div style="width: 100%; height: 300px; background: #f9fafd; border: 2px dashed #d0d0d0; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 1em;">Sin imagen</div>';
                    }
                    html += '</div>';
                    
                    html += '</div>';
                    
                    // Información del producto
                    html += '<div style="margin-top: 30px; padding-top: 30px; border-top: 1px solid #e0e0e0;">';
                    html += `<h4 style="color: #2d5be3; margin-bottom: 15px;">📋 Información del Producto</h4>`;
                    html += `<table style="width: 100%; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 10px 0; font-weight: 600; width: 150px;">Código:</td>
                            <td style="padding: 10px 0;">${producto.codigo}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 10px 0; font-weight: 600;">Nombre:</td>
                            <td style="padding: 10px 0;">${producto.nombre}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 10px 0; font-weight: 600;">Precio:</td>
                            <td style="padding: 10px 0; color: #2d5be3; font-weight: 700;">S/. ${producto.precio.toFixed(2)}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 10px 0; font-weight: 600;">Categoría:</td>
                            <td style="padding: 10px 0;">${producto.categoria}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 10px 0; font-weight: 600;">Segmento:</td>
                            <td style="padding: 10px 0;">${producto.segmento.toUpperCase()}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 10px 0; font-weight: 600;">Estado:</td>
                            <td style="padding: 10px 0;">${producto.estado}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 10px 0; font-weight: 600;">Mes:</td>
                            <td style="padding: 10px 0;">${producto.mes}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-weight: 600;">Descripción:</td>
                            <td style="padding: 10px 0;">${producto.descripcion || 'N/A'}</td>
                        </tr>
                    </table>`;
                    html += '</div>';
                    
                    // Modal de detalle
                    const modal = document.createElement('div');
                    modal.className = 'modal show';
                    modal.id = 'detalleModal';
                    modal.style.zIndex = '1100';
                    modal.innerHTML = `
                        <div class="modal-content" style="max-width: 1000px; max-height: 90vh; overflow-y: auto;">
                            <span class="close" onclick="document.getElementById('detalleModal').remove()">&times;</span>
                            <h2>👁️ Detalle del Producto</h2>
                            ${html}
                        </div>
                    `;
                    document.body.appendChild(modal);
                    
                    // Manejar errores de carga de imagen después de insertar en el DOM
                    setTimeout(() => {
                        const imgs = modal.querySelectorAll('img');
                        imgs.forEach(img => {
                            img.addEventListener('error', function() {
                                const parentDiv = this.parentElement;
                                if (parentDiv) {
                                    parentDiv.innerHTML = '<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #999; border: 2px dashed #d0d0d0; border-radius: 12px;">Sin imagen</div>';
                                }
                            });
                        });
                    }, 0);
                } catch(e) {
                    mostrarAlerta('❌ Error: ' + e.message, 'error');
                }
            }

            async function abrirEditModal(id) {
                try {
                    const response = await fetch('/api/productos/' + id);
                    const producto = await response.json();
                    productoEnEdicion = producto;
                    
                    let formHtml = '';
                    const campos = ['codigo', 'nombre', 'descripcion', 'precio', 'categoria', 'segmento', 'estado', 'imagen_listado', 'imagen_caracteristicas', 'mes', 'ano'];
                    
                    campos.forEach((key, idx) => {
                        const value = producto[key];
                        const gridSpan = (key === 'descripcion' || key === 'imagen_listado' || key === 'imagen_caracteristicas') ? ' style="grid-column: 1/-1;"' : '';
                        
                        if (key === 'descripcion' || key === 'imagen_listado' || key === 'imagen_caracteristicas') {
                            formHtml += '<div class="form-group"' + gridSpan + '><label>' + key + '</label><textarea name="' + key + '">' + (value || '') + '</textarea></div>';
                        } else if (key === 'categoria') {
                            formHtml += '<div class="form-group"><label>' + key + '</label><select name="' + key + '"><option>' + value + '</option><option>celulares</option><option>laptops</option><option>televisores</option><option>refrigeradoras</option><option>lavadoras</option></select></div>';
                        } else if (key === 'segmento') {
                            formHtml += '<div class="form-group"><label>' + key + '</label><select name="' + key + '"><option value="fnb" ' + (value === 'fnb' ? 'selected' : '') + '>FNB</option><option value="gaso" ' + (value === 'gaso' ? 'selected' : '') + '>GASO</option></select></div>';
                        } else if (key === 'estado') {
                            formHtml += '<div class="form-group"><label>' + key + '</label><select name="' + key + '"><option value="disponible" ' + (value === 'disponible' ? 'selected' : '') + '>Disponible</option><option value="no disponible" ' + (value === 'no disponible' ? 'selected' : '') + '>No Disponible</option><option value="agotado" ' + (value === 'agotado' ? 'selected' : '') + '>Agotado</option></select></div>';
                        } else {
                            const type = key === 'precio' || key === 'ano' ? 'number' : 'text';
                            const step = key === 'precio' ? ' step="0.01"' : '';
                            formHtml += '<div class="form-group"><label>' + key + '</label><input type="' + type + '" name="' + key + '" value="' + value + '"' + step + '></div>';
                        }
                    });
                    
                    formHtml += '<div class="form-group" style="grid-column: 1/-1;"><label>cuotas (JSON)</label><textarea name="cuotas">' + JSON.stringify(producto.cuotas) + '</textarea></div>';
                    
                    document.getElementById('editFormFields').innerHTML = formHtml;
                    document.getElementById('editModal').classList.add('show');
                } catch(e) {
                    mostrarAlerta('❌ Error: ' + e.message, 'error');
                }
            }

            function cerrarModal() {
                document.getElementById('editModal').classList.remove('show');
            }

            async function guardarEdicion() {
                try {
                    const formData = new FormData(document.getElementById('editForm'));
                    const cuotas = JSON.parse(formData.get('cuotas'));
                    
                    const data = {
                        codigo: formData.get('codigo'),
                        nombre: formData.get('nombre'),
                        descripcion: formData.get('descripcion'),
                        precio: parseFloat(formData.get('precio')),
                        categoria: formData.get('categoria'),
                        imagen_listado: formData.get('imagen_listado'),
                        imagen_caracteristicas: formData.get('imagen_caracteristicas'),
                        cuotas: cuotas,
                        mes: formData.get('mes'),
                        ano: parseInt(formData.get('ano')),
                        segmento: formData.get('segmento'),
                        estado: formData.get('estado')
                    };

                    const response = await fetch('/api/productos/' + productoEnEdicion.id, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });

                    if (response.ok) {
                        mostrarAlerta('✅ Producto actualizado exitosamente', 'success');
                        cerrarModal();
                        cargarProductos();
                    } else {
                        const error = await response.json();
                        mostrarAlerta('❌ Error: ' + (error.detail || 'Error desconocido'), 'error');
                    }
                } catch(e) {
                    mostrarAlerta('❌ Error: ' + e.message, 'error');
                }
            }

            async function eliminarProducto(id) {
                if (!confirm('⚠️ ¿Estás seguro de que deseas eliminar este producto?')) return;
                
                try {
                    const response = await fetch('/api/productos/' + id, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        mostrarAlerta('✅ Producto eliminado exitosamente', 'success');
                        cargarProductos();
                    } else {
                        const error = await response.json();
                        mostrarAlerta('❌ Error: ' + (error.detail || 'Error desconocido'), 'error');
                    }
                } catch(e) {
                    mostrarAlerta('❌ Error: ' + e.message, 'error');
                }
            }

            function mostrarAlerta(mensaje, tipo) {
                const container = document.getElementById('alertContainer');
                const alert = document.createElement('div');
                alert.className = 'alert alert-' + tipo + ' show';
                alert.textContent = mensaje;
                container.appendChild(alert);
                setTimeout(() => alert.remove(), 4000);
            }
        </script>
    </body>
    </html>
    """


@router.get("/productos", response_model=List[Producto])
async def listar_productos(db=Depends(get_db)):
    """Listar todos los productos"""
    import json

    productos = db.query(DBProducto).all()
    # Convertir cuotas de string a dict si es necesario
    for p in productos:
        if isinstance(p.cuotas, str):
            try:
                p.cuotas = json.loads(p.cuotas)
            except:
                p.cuotas = {}
    return productos


@router.get("/productos/{producto_id}", response_model=Producto)
async def obtener_producto_db(producto_id: int, db=Depends(get_db)):
    """Obtener un producto por ID"""
    import json

    producto = db.query(DBProducto).filter(DBProducto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # Convertir cuotas de string a dict si es necesario
    if isinstance(producto.cuotas, str):
        try:
            producto.cuotas = json.loads(producto.cuotas)
        except:
            producto.cuotas = {}
    return producto


@router.post("/productos", response_model=Producto)
async def crear_producto(producto: ProductoCreate, db=Depends(get_db)):
    """Crear un nuevo producto"""
    db_producto = DBProducto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.put("/productos/{producto_id}", response_model=Producto)
async def actualizar_producto(
    producto_id: int, producto: ProductoUpdate, db=Depends(get_db)
):
    """Actualizar un producto"""
    db_producto = db.query(DBProducto).filter(DBProducto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = producto.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_producto, key, value)

    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: int, db=Depends(get_db)):
    """Eliminar un producto"""
    db_producto = db.query(DBProducto).filter(DBProducto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(db_producto)
    db.commit()
    return {"mensaje": "Producto eliminado exitosamente"}
