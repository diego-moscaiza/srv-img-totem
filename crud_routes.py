from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import Producto as DBProducto, SessionLocal
from schemas import Producto, ProductoCreate, ProductoUpdate
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
            body { font-family: Arial, sans-serif; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; margin-bottom: 30px; }
            h2 { color: #555; margin: 20px 0 15px 0; }
            .section { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #333; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
            textarea { resize: vertical; min-height: 80px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-right: 5px; }
            button:hover { background: #0056b3; }
            button.danger { background: #dc3545; }
            button.danger:hover { background: #c82333; }
            .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; font-weight: bold; color: #333; }
            tr:hover { background: #f9f9f9; }
            .actions { white-space: nowrap; }
            .actions button { margin-right: 5px; padding: 5px 10px; font-size: 12px; margin-bottom: 0; }
            .alert { padding: 15px; margin-bottom: 20px; border-radius: 4px; display: none; }
            .alert.show { display: block; }
            .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); overflow-y: auto; }
            .modal.show { display: block; }
            .modal-content { background: white; margin: 5% auto; padding: 30px; border-radius: 8px; width: 90%; max-width: 600px; }
            .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
            .close:hover { color: #000; }
            .reload-btn { margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛠️ Panel de Administración - Gestión de Productos</h1>
            
            <div id="alertContainer"></div>
            
            <div class="section">
                <h2>Crear Nuevo Producto</h2>
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
                    <button type="submit">Crear Producto</button>
                </form>
            </div>
            
            <div class="section">
                <h2>Productos Registrados</h2>
                <button class="reload-btn" onclick="cargarProductos()">🔄 Recargar</button>
                <table id="productosTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Código</th>
                            <th>Nombre</th>
                            <th>Precio</th>
                            <th>Categoría</th>
                            <th>Mes</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody id="productosBody">
                    </tbody>
                </table>
            </div>
        </div>

        <div id="editModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="cerrarModal()">&times;</span>
                <h2>Editar Producto</h2>
                <form id="editForm">
                    <div class="grid" id="editFormFields"></div>
                    <button type="submit" style="margin-top: 15px;">Guardar Cambios</button>
                </form>
            </div>
        </div>

        <script>
            let productoEnEdicion = null;

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
                        stock: true
                    };

                    const response = await fetch('/api/productos', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });

                    if (response.ok) {
                        mostrarAlerta('✅ Producto creado exitosamente', 'success');
                        document.getElementById('crearForm').reset();
                        cargarProductos();
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
                    const productos = await response.json();
                    
                    const tbody = document.getElementById('productosBody');
                    tbody.innerHTML = '';
                    
                    productos.forEach(p => {
                        const row = `
                            <tr>
                                <td>${p.id}</td>
                                <td>${p.codigo}</td>
                                <td>${p.nombre}</td>
                                <td>$${p.precio.toFixed(2)}</td>
                                <td>${p.categoria}</td>
                                <td>${p.mes}</td>
                                <td class="actions">
                                    <button onclick="abrirEditModal(${p.id})">✏️ Editar</button>
                                    <button class="danger" onclick="eliminarProducto(${p.id})">🗑️ Eliminar</button>
                                </td>
                            </tr>
                        `;
                        tbody.innerHTML += row;
                    });
                } catch(e) {
                    mostrarAlerta('❌ Error al cargar productos: ' + e.message, 'error');
                }
            }

            async function abrirEditModal(id) {
                try {
                    const response = await fetch(`/api/productos/${id}`);
                    const producto = await response.json();
                    productoEnEdicion = producto;
                    
                    let formHtml = '';
                    const campos = ['codigo', 'nombre', 'descripcion', 'precio', 'categoria', 'imagen_listado', 'imagen_caracteristicas', 'mes', 'ano'];
                    
                    campos.forEach((key, idx) => {
                        const value = producto[key];
                        const isLast = idx === campos.length - 1;
                        const gridSpan = (key === 'descripcion' || key === 'imagen_listado' || key === 'imagen_caracteristicas') ? ' style="grid-column: 1/-1;"' : '';
                        
                        if (key === 'descripcion' || key === 'imagen_listado' || key === 'imagen_caracteristicas') {
                            formHtml += `<div class="form-group"${gridSpan}><label>${key}</label><textarea name="${key}">${value}</textarea></div>`;
                        } else if (key === 'categoria') {
                            formHtml += `<div class="form-group"><label>${key}</label><select name="${key}"><option>${value}</option><option>celulares</option><option>laptops</option><option>televisores</option><option>refrigeradoras</option><option>lavadoras</option></select></div>`;
                        } else {
                            const type = key === 'precio' || key === 'ano' ? 'number' : 'text';
                            const step = key === 'precio' ? ' step="0.01"' : '';
                            formHtml += `<div class="form-group"><label>${key}</label><input type="${type}" name="${key}" value="${value}"${step}></div>`;
                        }
                    });
                    
                    formHtml += `<div class="form-group" style="grid-column: 1/-1;"><label>cuotas (JSON)</label><textarea name="cuotas">${JSON.stringify(producto.cuotas)}</textarea></div>`;
                    
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
                        ano: parseInt(formData.get('ano'))
                    };

                    const response = await fetch(`/api/productos/${productoEnEdicion.id}`, {
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
                if (!confirm('¿Estás seguro de que deseas eliminar este producto?')) return;
                
                try {
                    const response = await fetch(`/api/productos/${id}`, {
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
                alert.className = `alert alert-${tipo} show`;
                alert.textContent = mensaje;
                container.appendChild(alert);
                setTimeout(() => alert.remove(), 4000);
            }

            // Cargar productos al abrir la página
            cargarProductos();
        </script>
    </body>
    </html>
    """


@router.get("/productos", response_model=List[Producto])
async def listar_productos(db: Session = Depends(get_db)):
    """Listar todos los productos"""
    productos = db.query(DBProducto).all()
    return productos


@router.get("/productos/{producto_id}", response_model=Producto)
async def obtener_producto_db(producto_id: int, db: Session = Depends(get_db)):
    """Obtener un producto por ID"""
    producto = db.query(DBProducto).filter(DBProducto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/productos", response_model=Producto)
async def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo producto"""
    db_producto = DBProducto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.put("/productos/{producto_id}", response_model=Producto)
async def actualizar_producto(producto_id: int, producto: ProductoUpdate, db: Session = Depends(get_db)):
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
async def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """Eliminar un producto"""
    db_producto = db.query(DBProducto).filter(DBProducto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(db_producto)
    db.commit()
    return {"mensaje": "Producto eliminado exitosamente"}
