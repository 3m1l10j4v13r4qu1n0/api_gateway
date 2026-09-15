# Skill: Documentación de Software estilo APA

## Descripción
Proporciona reglas para estandarizar la documentación de proyectos de software siguiendo las normas APA 7ma edición.

## Plantilla para Documentación de Software

```markdown
# [Título del Proyecto]

## Resumen
[150-250 palabras describiendo el proyecto]

## 1. Introducción
### 1.1 Contexto
### 1.2 Objetivos
### 1.3 Alcance

## 2. Metodología
### 2.1 Arquitectura
### 2.2 Tecnologías Utilizadas
### 2.3 Diseño de Base de Datos

## 3. Implementación
### 3.1 Estructura del Proyecto
### 3.2 Funcionalidades Principales
### 3.3 Interfaz de Usuario

## 4. Resultados
### 4.1 Pruebas Realizadas
### 4.2 Rendimiento
### 4.3 Limitaciones

## 5. Discusión
### 5.1 Comparación con Otras Soluciones
### 5.2 Mejoras Futuras

## 6. Conclusiones

## Referencias

## Apéndices
### Apéndice A: Documentación de API
### Apéndice B: Configuración del Entorno
### Apéndice C: Código Fuente Relevante
```

## Ejemplo de Citas

### Cita de Librería
```markdown
La librería React (Facebook, 2013) proporciona una arquitectura basada en 
componentes para construir interfaces de usuario.
```

### Cita de Artículo Técnico
```markdown
Según Martin (2017), los principios SOLID son fundamentales para el 
diseño de software orientado a objetos.
```

### Cita de Documentación Oficial
```markdown
La API de RESTful debe seguir los principios de statelessness y 
uniform interface (Fielding, 2000).
```

## Formato de Referencias

### Formato General
```
Apellido, N. A. (Año). Título del trabajo. Fuente. URL
```

### Ejemplos

#### Documentación Oficial
```
React. (2023). Documentación oficial de React. Meta Platforms. 
https://react.dev/
```

#### Libro de Programación
```
Martin, R. C. (2017). Clean Architecture: A Craftsman's Guide to 
Software Structure and Design. Prentice Hall.
```

#### Artículo Académico
```
Fielding, R. T. (2000). Architectural Styles and the Design of 
Network-based Software Architectures [Tesis de Doctorado, 
Universidad de California, Irvine]. 
https://www.ics.uci.edu/~fielding/pubs/dissertation/top.htm
```

## Comandos Útiles

### Para compilar LaTeX
```bash
pdflatex documento.tex
```

### Para verificar ortografía
```bash
aspell -l es check documento.tex
```

### Para convertir Markdown a PDF
```bash
pandoc documento.md -o documento.pdf
```

## Notas Importantes

1. Adaptar al contexto del proyecto
2. Mantener formato consistente
3. Priorizar la comprensión del lector
4. Mantener referencias actualizadas
5. Verificar que todas las fuentes citadas estén en la lista de referencias