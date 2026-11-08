# Registro de respaldos y restauración — Demanda360

**Proyecto:** Demanda360  
**Responsable de la prueba:** Brayan Felipe Álvarez Nieto  
**Fecha:** 8 de noviembre de 2026  
**Entorno:** Ubuntu, Docker Compose y PostgreSQL 16  
**Tipo de datos:** Simulados

## 1. Objetivo

Verificar que la base de datos PostgreSQL de Demanda360 pueda respaldarse y restaurarse correctamente en un entorno independiente, comprobando la integridad y consistencia de los datos.

## 2. Resultados de la prueba

| Indicador | Resultado |
|---|---|
| Fecha y hora del respaldo | 2026-11-08 17:10 |
| Archivo generado | `demanda360_20261108_171017.dump` |
| Duración del respaldo | 0,3 segundos |
| Duración de la restauración | 0,3 segundos |
| Restauración y verificación | 1,0 segundo |
| Base original | `demanda360` |
| Base de restauración | `demanda360_restore` |
| Tablas verificadas | 11 |
| Filas verificadas | 232 |
| Saldos comprobados | 11 |
| KPI comprobados | 5 |
| Huella SHA-256 | Correcta |
| Permisos del archivo | `-rw-------` |
| Código de salida | 0 |
| Resultado | EXITOSO |

## 3. Validaciones realizadas

- Se generó correctamente un respaldo mediante `scripts/backup.sh`.
- Se verificó su integridad utilizando SHA-256.
- Se restauró el respaldo en la base independiente `demanda360_restore`.
- Las cantidades de registros coincidieron en las 11 tablas.
- Los saldos de las 11 referencias y los cinco KPI coincidieron.
- Se comprobó que el respaldo se almacenó fuera del repositorio Git.
- Se verificó que el archivo tiene permisos restringidos al propietario.
- La restauración finalizó correctamente, sin modificar la base principal.

## 4. Objetivos de recuperación

**RTO objetivo: 4 horas.** La restauración de la base de datos y su verificación tardaron 1,0 segundo en el laboratorio. Para validar el RTO completo también debe medirse el tiempo de recuperación y disponibilidad de la aplicación web.

**RPO objetivo: 1 hora.** Este objetivo requiere programar respaldos al menos cada hora y comprobar su ejecución. La prueba manual realizada no demuestra todavía el cumplimiento del RPO.

## 5. Conclusión

La prueba de respaldo y restauración de PostgreSQL fue exitosa en el entorno Ubuntu de Demanda360. Se restauraron y verificaron 11 tablas, 232 registros, 11 saldos y cinco KPI utilizando datos simulados.

Los resultados confirman la integridad de la copia evaluada y la capacidad de restaurarla en una base de pruebas independiente.

**Estado:** Prueba funcional aprobada. Queda pendiente verificar la programación periódica de respaldos y medir la recuperación completa del servicio.

## 6. Evidencias

Capturas de la ejecución de `backup.sh`, `restore_prueba.sh`, verificación SHA-256, comparación de datos y permisos del archivo, almacenadas en `docs/evidencias/`.
