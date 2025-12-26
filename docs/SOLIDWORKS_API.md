# SolidWorks API Coverage - Project Vulcan

Complete reference for the SolidWorks-Python bridge capabilities.

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     Project Vulcan Server                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI REST Layer                         │  │
│  │  /solidworks/*           - Core modeling                      │  │
│  │  /solidworks-assembly/*  - Assembly operations                │  │
│  │  /solidworks-drawings/*  - Drawing creation                   │  │
│  │  /solidworks-batch/*     - Batch operations                   │  │
│  │  /solidworks-advanced/*  - Sheet metal, weldments, routing   │  │
│  │  /solidworks-simulation/*- FEA, thermal, frequency           │  │
│  │  /solidworks-pdm/*       - Vault operations                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐   │
│  │              solidworks_bridge.py                            │   │
│  │  • Thread-safe connection pooling                            │   │
│  │  • Automatic reconnection                                    │   │
│  │  • Version detection (2020-2025)                            │   │
│  │  • High-level API wrappers                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐   │
│  │              win32com.client + pythoncom                     │   │
│  │              COM/OLE Automation Layer                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼ COM Interface
┌────────────────────────────────────────────────────────────────────┐
│                   SolidWorks Application (C++)                     │
│  IModelDoc2, IAssemblyDoc, IDrawingDoc, IFeatureManager,          │
│  ISketchManager, IMate2, ISimulation, IEdmVault5, ...             │
└────────────────────────────────────────────────────────────────────┘
```

---

## API Coverage Summary

| Module | Endpoints | Coverage | Add-in Required |
|--------|-----------|----------|-----------------|
| Core Modeling | 45+ | 85% | No |
| Assembly | 30+ | 75% | No |
| Drawings | 25+ | 70% | No |
| Batch Operations | 10+ | 90% | No |
| Sheet Metal | 15+ | 80% | No |
| Weldments | 12+ | 70% | No |
| Routing | 8+ | 60% | Routing Add-in |
| Simulation | 20+ | 65% | Simulation Add-in |
| PDM | 25+ | 70% | PDM Client |

---

## 1. Core Modeling (`/solidworks/*`)

### Sketch Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks/sketch/create` | POST | Create sketch on plane |
| `/solidworks/sketch/line` | POST | Draw line |
| `/solidworks/sketch/circle` | POST | Draw circle |
| `/solidworks/sketch/rectangle` | POST | Draw rectangle |
| `/solidworks/sketch/arc` | POST | Draw arc |
| `/solidworks/sketch/spline` | POST | Draw spline |
| `/solidworks/sketch/polygon` | POST | Draw polygon |
| `/solidworks/sketch/ellipse` | POST | Draw ellipse |
| `/solidworks/sketch/close` | POST | Exit sketch editing |

### Feature Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks/feature/extrude` | POST | Boss extrusion |
| `/solidworks/feature/cut-extrude` | POST | Cut extrusion |
| `/solidworks/feature/revolve` | POST | Revolve feature |
| `/solidworks/feature/sweep` | POST | Sweep feature |
| `/solidworks/feature/loft` | POST | Loft feature |
| `/solidworks/feature/fillet` | POST | Fillet edges |
| `/solidworks/feature/chamfer` | POST | Chamfer edges |
| `/solidworks/feature/shell` | POST | Shell feature |
| `/solidworks/feature/mirror` | POST | Mirror feature |
| `/solidworks/feature/linear-pattern` | POST | Linear pattern |
| `/solidworks/feature/circular-pattern` | POST | Circular pattern |
| `/solidworks/feature/rib` | POST | Rib feature |
| `/solidworks/feature/draft` | POST | Draft feature |
| `/solidworks/feature/hole-wizard` | POST | Hole wizard |

### Document Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks/document/new` | POST | New document |
| `/solidworks/document/open` | POST | Open file |
| `/solidworks/document/save` | POST | Save document |
| `/solidworks/document/export` | POST | Export (STEP, STL, PDF) |
| `/solidworks/document/close` | POST | Close document |
| `/solidworks/document/rebuild` | POST | Rebuild model |

### Properties

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks/properties` | GET | Get custom properties |
| `/solidworks/properties` | POST | Set custom property |
| `/solidworks/mass-properties` | GET | Get mass, volume, etc. |
| `/solidworks/material` | POST | Set material |

---

## 2. Assembly Operations (`/solidworks-assembly/*`)

### Component Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks-assembly/insert-component` | POST | Insert component |
| `/solidworks-assembly/replace-component` | POST | Replace component |
| `/solidworks-assembly/suppress` | POST | Suppress component |
| `/solidworks-assembly/unsuppress` | POST | Unsuppress component |
| `/solidworks-assembly/hide` | POST | Hide component |
| `/solidworks-assembly/show` | POST | Show component |
| `/solidworks-assembly/component-pattern` | POST | Pattern components |

### Mates

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks-assembly/mate/coincident` | POST | Coincident mate |
| `/solidworks-assembly/mate/concentric` | POST | Concentric mate |
| `/solidworks-assembly/mate/parallel` | POST | Parallel mate |
| `/solidworks-assembly/mate/perpendicular` | POST | Perpendicular mate |
| `/solidworks-assembly/mate/distance` | POST | Distance mate |
| `/solidworks-assembly/mate/angle` | POST | Angle mate |
| `/solidworks-assembly/mate/tangent` | POST | Tangent mate |
| `/solidworks-assembly/mate/gear` | POST | Gear mate |
| `/solidworks-assembly/mate/cam` | POST | Cam follower |
| `/solidworks-assembly/mate/path` | POST | Path mate |
| `/solidworks-assembly/mate/slot` | POST | Slot mate |
| `/solidworks-assembly/mate/width` | POST | Width mate |

### Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks-assembly/bom` | GET | Get BOM |
| `/solidworks-assembly/interference` | GET | Interference check |
| `/solidworks-assembly/components` | GET | List components |

---

## 3. Drawing Operations (`/solidworks-drawings/*`)

### Views

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks-drawings/view/standard` | POST | Standard view |
| `/solidworks-drawings/view/projected` | POST | Projected view |
| `/solidworks-drawings/view/section` | POST | Section view |
| `/solidworks-drawings/view/detail` | POST | Detail view |
| `/solidworks-drawings/view/isometric` | POST | Isometric view |

### Annotations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks-drawings/dimension/insert` | POST | Insert dimension |
| `/solidworks-drawings/note/add` | POST | Add note |
| `/solidworks-drawings/balloon/add` | POST | Add balloon |
| `/solidworks-drawings/centerline` | POST | Add centerline |
| `/solidworks-drawings/centermark` | POST | Add center mark |

### Tables

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solidworks-drawings/table/bom` | POST | BOM table |
| `/solidworks-drawings/table/revision` | POST | Revision table |
| `/solidworks-drawings/table/general` | POST | General table |

---

## 4. Sheet Metal (`/solidworks-advanced/sheet-metal/*`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sheet-metal/base-flange` | POST | Base flange from sketch |
| `/sheet-metal/edge-flange` | POST | Edge flange |
| `/sheet-metal/miter-flange` | POST | Miter flange |
| `/sheet-metal/hem` | POST | Hem (closed, open, tear drop) |
| `/sheet-metal/jog` | POST | Jog offset |
| `/sheet-metal/lofted-bend` | POST | Lofted bend |
| `/sheet-metal/flat-pattern` | POST | Create flat pattern |
| `/sheet-metal/parameters` | GET | Get SM parameters |

---

## 5. Weldments (`/solidworks-advanced/weldments/*`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/weldments/structural-member` | POST | Structural member |
| `/weldments/gusset` | POST | Gusset plate |
| `/weldments/end-cap` | POST | End cap |
| `/weldments/trim-extend` | POST | Trim/extend member |
| `/weldments/cut-list` | GET | Get cut list |
| `/weldments/profiles` | GET | List available profiles |

---

## 6. Routing (`/solidworks-advanced/routing/*`)

**Requires**: SOLIDWORKS Routing Add-in

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/routing/status` | GET | Check routing availability |
| `/routing/start-route` | POST | Start new route |
| `/routing/add-segment` | POST | Add route segment |
| `/routing/insert-fitting` | POST | Insert fitting |

Supported routing types:
- Piping
- Tubing
- Electrical
- Cable Tray

---

## 7. Simulation (`/solidworks-simulation/*`)

**Requires**: SOLIDWORKS Simulation Add-in

### Study Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulation/status` | GET | Check availability |
| `/simulation/study/create` | POST | Create study |
| `/simulation/study/list` | GET | List studies |
| `/simulation/study/{name}` | DELETE | Delete study |

### Setup

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulation/material/assign` | POST | Assign material |
| `/simulation/material/library` | GET | Get materials |
| `/simulation/fixture/add` | POST | Add fixture |
| `/simulation/load/force` | POST | Add force |
| `/simulation/load/pressure` | POST | Add pressure |
| `/simulation/load/gravity` | POST | Add gravity |

### Mesh & Run

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulation/mesh/create` | POST | Create mesh |
| `/simulation/mesh/info` | GET | Mesh statistics |
| `/simulation/run` | POST | Run analysis |

### Results

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulation/results/summary` | GET | Results summary |
| `/simulation/results/plot` | POST | Create plot |
| `/simulation/results/probe` | GET | Probe value |

---

## 8. PDM Integration (`/solidworks-pdm/*`)

**Requires**: SOLIDWORKS PDM Professional Client

### Connection

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pdm/status` | GET | Check PDM status |
| `/pdm/login` | POST | Login to vault |
| `/pdm/logout` | POST | Logout |
| `/pdm/vaults` | GET | List available vaults |

### File Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pdm/checkout` | POST | Check out files |
| `/pdm/checkin` | POST | Check in files |
| `/pdm/get-latest` | POST | Get latest version |
| `/pdm/file-info` | GET | Get file info |

### Version Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pdm/history` | GET | Version history |
| `/pdm/get-version` | POST | Get specific version |

### Search & Browse

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pdm/search` | POST | Search vault |
| `/pdm/folder/contents` | GET | Browse folder |

### Workflow

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pdm/workflow/state` | GET | Get current state |
| `/pdm/workflow/transition` | POST | Execute transition |

### Data Cards

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pdm/variables` | POST | Get/set variables |
| `/pdm/bom` | POST | Get PDM BOM |

---

## Type Stubs

Type stubs are available for IDE autocomplete:

```python
from desktop_server.com.solidworks_types import (
    ISldWorks,
    IModelDoc2,
    IAssemblyDoc,
    IDrawingDoc,
    IFeatureManager,
    ISketchManager,
    # ... 50+ interfaces
)
```

---

## Thread-Safe Usage

```python
from desktop_server.com.solidworks_bridge import get_bridge, com_operation

# Context manager approach
bridge = get_bridge()
with bridge.connect() as sw:
    model = sw.ActiveDoc
    title = model.GetTitle()

# Decorator approach
@com_operation
def my_function(sw_app, param):
    return sw_app.ActiveDoc.GetTitle()

result = my_function("param")
```

---

## Version Compatibility

| SolidWorks Version | API Version | Status |
|--------------------|-------------|--------|
| 2020 | 28 | Supported |
| 2021 | 29 | Supported |
| 2022 | 30 | Supported |
| 2023 | 31 | Supported |
| 2024 | 32 | Supported |
| 2025 | 33 | Supported |

---

## Error Handling

All endpoints return standard error format:

```json
{
  "success": false,
  "error": "Error description",
  "error_code": 500
}
```

Common error codes:
- `400`: Bad request / invalid parameters
- `404`: Entity not found
- `500`: COM/SolidWorks error
- `501`: Feature/add-in not available

---

## Performance Tips

1. **Use batch operations** for multiple changes
2. **Disable graphics** during heavy operations
3. **Defer rebuilds** until all changes complete
4. **Use early-binding** with type stubs for faster dispatch
5. **Pool connections** for concurrent requests

---

## Links

- [SolidWorks API Help](https://help.solidworks.com/2024/english/api/sldworksapi/Welcome.htm)
- [Project Vulcan GitHub](https://github.com/...)
