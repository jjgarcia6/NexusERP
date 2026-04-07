# Resumen Final — customers-crm

**Proyecto:** NexusERP — Customers CRM  
**Cambio OpenSpec:** customers-crm  
**Fecha:** 7 de abril de 2026  
**Estado:** Pendientes finales cerrados para validación

## Validaciones cerradas

### 4.6 — LOPDP

- `name`, `identification_number`, `email` y `phone` se tratan como PII en el módulo.
- `CustomerResponse` no expone `created_by`.
- `GET /customers/search` retorna solo `id`, `name`, `identification_number` y `customer_type`.
- El flujo de lista, búsqueda, edición y desactivación no muestra el body de forma sensible en los logs de acceso.
- Evidencia visual y de persistencia en Atlas adjunta en las capturas de esta carpeta.

### 4.7 — WCAG AA

Se verificó el contraste de los badges del listado de clientes usando las combinaciones reales de UI:

| Badge | Texto/Fondo | Contraste |
| --- | --- | --- |
| Persona Natural | `#134e4a` sobre `#ccfbf1` | 8.41 |
| Persona Natural oscuro | `#134e4a` sobre `#99f6e4` | 7.52 |
| Jurídico | `#701a75` sobre `#fae8ff` | 8.62 |
| Jurídico oscuro | `#701a75` sobre `#f5d0fe` | 7.33 |
| Activo | `#064e3b` sobre `#d1fae5` | 8.57 |
| Inactivo | `#475569` sobre `#e2e8f0` | 6.15 |

Todas las combinaciones superan el mínimo WCAG AA de 4.5:1.

### 4.8 — SCA

Ejecutado:

```bash
trivy fs --scanners vuln --severity HIGH,CRITICAL --skip-dirs .venv --exit-code 1 .
```

Resultado:

- `apps/frontend/package-lock.json`: 0 vulnerabilidades HIGH/CRITICAL.
- Sin hallazgos bloqueantes para el cambio.

### 5.5 — Integración manual

Evidencia visual disponible en esta carpeta:

- [image.png](image.png)
- [image-1.png](image-1.png)
- [image-2.png](image-2.png)
- [image-3.png](image-3.png)
- [image-4.png](image-4.png)

Flujo validado:

- Alta de cliente persona natural con cédula válida.
- Búsqueda por texto parcial en el selector/listado.
- Edición con `identification_number` mantenido inmutable.
- Desactivación por soft delete con persistencia en Atlas.
- El documento sigue almacenado con `is_active: false`.

## Conclusión

Los cuatro pendientes finales quedaron validados y documentados. El change puede considerarse listo para cierre en OpenSpec.
