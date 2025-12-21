
---

## 🔧 Phase 15: CAD Module Redesign - PLANNED

### 📋 Overview
Complete redesign of `/cad` page based on 2024 PLM/PDM UI research. Integrates with existing SolidWrap, Flatter Files, and Performance Manager features.

**Current Components**: Projects, PartsLibrary, ECNTracker, ExportDrive
**Design Inspiration**: Teamcenter, SOLIDWORKS PDM 2025, Onshape, OpenBOM, Zel X

---

### 🏗️ Step 1: Create New Route Structure

**Location**: `apps/web/src/app/cad/`

```bash
# Create directories
mkdir -p apps/web/src/app/cad/{dashboard,projects/{new,[id]},drawings/{search,[id]},assemblies/{[id],bom},parts/{library,search,[id]},ecn/{new,[id]},jobs/{queue,history,[id]},exports/{drive,flatter-files},performance,settings/{sw-settings,preferences}}
```

**New Routes:**
| Route | Purpose |
|-------|---------|
| `/cad` | Redirect to `/cad/dashboard` |
| `/cad/dashboard` | Main workspace (status, queue, performance) |
| `/cad/projects` | Project list |
| `/cad/projects/new` | New project |
| `/cad/projects/[id]` | Project detail |
| `/cad/drawings` | Drawing management |
| `/cad/drawings/search` | Search drawings (Flatter Files) |
| `/cad/drawings/[id]` | Drawing detail + revisions |
| `/cad/assemblies` | Assembly browser |
| `/cad/assemblies/[id]` | Assembly detail |
| `/cad/assemblies/bom` | BOM management |
| `/cad/parts` | Parts overview |
| `/cad/parts/library` | Parts library browser |
| `/cad/parts/search` | Part search |
| `/cad/parts/[id]` | Part detail |
| `/cad/ecn` | ECN list |
| `/cad/ecn/new` | New ECN |
| `/cad/ecn/[id]` | ECN detail + approval workflow |
| `/cad/jobs` | Job overview |
| `/cad/jobs/queue` | Active job queue |
| `/cad/jobs/history` | Completed jobs |
| `/cad/jobs/[id]` | Job detail |
| `/cad/exports` | Export overview |
| `/cad/exports/drive` | Google Drive export |
| `/cad/exports/flatter-files` | Flatter Files upload |
| `/cad/performance` | System performance monitor |
| `/cad/settings` | Settings overview |
| `/cad/settings/sw-settings` | SolidWorks graphics tiers |
| `/cad/settings/preferences` | UI preferences |

---

### 🏗️ Step 2: Create Component Structure

**Location**: `apps/web/src/components/cad/`

```bash
# Create component directories
mkdir -p apps/web/src/components/cad/{layout,dashboard,projects,drawings,assemblies,parts,ecn,jobs,exports,performance,common}
```

**Components to Create:**

#### Layout Components
| File | Description | Lines |
|------|-------------|-------|
| `layout/CADHeader.tsx` | Header with SW status, quick actions | ~150 |
| `layout/CADNav.tsx` | Side navigation | ~120 |
| `layout/LeftPanel.tsx` | Collapsible file tree | ~150 |
| `layout/StatusBar.tsx` | SW connection, RAM, GPU status | ~100 |

#### Dashboard Components
| File | Description | Lines |
|------|-------------|-------|
| `dashboard/SystemStatus.tsx` | SolidWorks connection + health | ~150 |
| `dashboard/JobQueueWidget.tsx` | Active jobs mini view | ~120 |
| `dashboard/PerformanceWidget.tsx` | RAM/GPU gauges | ~150 |
| `dashboard/RecentFiles.tsx` | Recently opened files | ~100 |
| `dashboard/QuickActions.tsx` | Common actions (New Part, Import PDF) | ~80 |

#### Projects Components
| File | Description | Lines |
|------|-------------|-------|
| `projects/ProjectList.tsx` | Project grid/list view | ~200 |
| `projects/ProjectCard.tsx` | Project card with stats | ~100 |
| `projects/ProjectDetail.tsx` | Full project view | ~250 |
| `projects/ProjectForm.tsx` | New/edit project form | ~200 |

#### Drawings Components
| File | Description | Lines |
|------|-------------|-------|
| `drawings/DrawingSearch.tsx` | Flatter Files search UI | ~200 |
| `drawings/DrawingList.tsx` | Drawing results list | ~150 |
| `drawings/DrawingCard.tsx` | Drawing preview card | ~120 |
| `drawings/DrawingDetail.tsx` | Full drawing view + revisions | ~250 |
| `drawings/RevisionHistory.tsx` | Revision timeline | ~150 |
| `drawings/PDFViewer.tsx` | Embedded PDF viewer | ~100 |

#### Assemblies Components
| File | Description | Lines |
|------|-------------|-------|
| `assemblies/AssemblyTree.tsx` | Hierarchical assembly view | ~250 |
| `assemblies/AssemblyNode.tsx` | Tree node component | ~80 |
| `assemblies/BOMTable.tsx` | Bill of Materials table | ~300 |
| `assemblies/BOMExport.tsx` | Export BOM to Excel/CSV | ~100 |
| `assemblies/AssemblyViewer.tsx` | 3D preview (if available) | ~150 |

#### Parts Components
| File | Description | Lines |
|------|-------------|-------|
| `parts/PartLibrary.tsx` | Parts library browser | ~250 |
| `parts/PartSearch.tsx` | Part search with filters | ~200 |
| `parts/PartCard.tsx` | Part preview card | ~100 |
| `parts/PartDetail.tsx` | Full part view + properties | ~200 |
| `parts/PartProperties.tsx` | Custom properties editor | ~150 |
| `parts/WhereUsed.tsx` | Where-used analysis | ~150 |

#### ECN Components
| File | Description | Lines |
|------|-------------|-------|
| `ecn/ECNList.tsx` | ECN list with status filters | ~200 |
| `ecn/ECNCard.tsx` | ECN summary card | ~100 |
| `ecn/ECNDetail.tsx` | Full ECN view | ~250 |
| `ecn/ECNForm.tsx` | New/edit ECN form | ~300 |
| `ecn/ECNWorkflow.tsx` | Approval workflow visualization | ~200 |
| `ecn/AffectedItems.tsx` | List of affected parts/drawings | ~150 |

#### Jobs Components
| File | Description | Lines |
|------|-------------|-------|
| `jobs/JobQueue.tsx` | Active job queue | ~250 |
| `jobs/JobCard.tsx` | Job status card | ~120 |
| `jobs/JobDetail.tsx` | Full job detail | ~200 |
| `jobs/JobHistory.tsx` | Completed jobs list | ~200 |
| `jobs/JobProgress.tsx` | Progress bar with steps | ~100 |
| `jobs/BatchUpload.tsx` | Batch file upload UI | ~200 |

#### Exports Components
| File | Description | Lines |
|------|-------------|-------|
| `exports/ExportQueue.tsx` | Pending exports | ~150 |
| `exports/DriveExport.tsx` | Google Drive export UI | ~200 |
| `exports/FlatterFilesUpload.tsx` | Flatter Files upload UI | ~200 |
| `exports/ExportHistory.tsx` | Export history log | ~150 |

#### Performance Components
| File | Description | Lines |
|------|-------------|-------|
| `performance/PerformanceDashboard.tsx` | Full performance view | ~300 |
| `performance/RAMGauge.tsx` | RAM usage gauge | ~100 |
| `performance/GPUGauge.tsx` | GPU usage gauge | ~100 |
| `performance/TierIndicator.tsx` | Current tier display | ~80 |
| `performance/TierHistory.tsx` | Tier changes over time | ~150 |
| `performance/SWRestartLog.tsx` | SW restart history | ~100 |

#### Common Components
| File | Description | Lines |
|------|-------------|-------|
| `common/FileTree.tsx` | File/folder tree view | ~200 |
| `common/PartNumberInput.tsx` | Part number with validation | ~80 |
| `common/RevisionBadge.tsx` | Revision display badge | ~50 |
| `common/StatusBadge.tsx` | Status display (Draft, Released, etc) | ~50 |
| `common/SWConnectionStatus.tsx` | SolidWorks connection indicator | ~80 |
| `common/ThumbnailPreview.tsx` | Part/drawing thumbnail | ~100 |

---

### 🏗️ Step 3: Create Types & Constants

**Location**: `apps/web/src/lib/cad/`

```bash
mkdir -p apps/web/src/lib/cad/hooks
```

#### `types.ts` - CAD Type Definitions
```typescript
// File Types
export type CADFileType = 'part' | 'assembly' | 'drawing';

// File Status
export type FileStatus = 'draft' | 'in_review' | 'approved' | 'released' | 'obsolete';

// ECN Status
export type ECNStatus = 'draft' | 'pending_review' | 'approved' | 'rejected' | 'implemented';

// Job Status
export type JobStatus = 'queued' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';

// Performance Tier
export type PerformanceTier = 'FULL' | 'REDUCED' | 'MINIMAL' | 'SURVIVAL';

// Part
export interface Part {
  id: string;
  partNumber: string;
  description: string;
  revision: string;
  status: FileStatus;
  material?: string;
  weight?: number;
  filePath: string;
  thumbnail?: string;
  customProperties: Record<string, string>;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

// Assembly
export interface Assembly {
  id: string;
  partNumber: string;
  description: string;
  revision: string;
  status: FileStatus;
  filePath: string;
  thumbnail?: string;
  componentCount: number;
  components: AssemblyComponent[];
  createdAt: string;
  updatedAt: string;
}

// Assembly Component
export interface AssemblyComponent {
  id: string;
  partNumber: string;
  description: string;
  quantity: number;
  level: number;
  parentId?: string;
  type: CADFileType;
}

// Drawing
export interface Drawing {
  id: string;
  drawingNumber: string;
  title: string;
  revision: string;
  status: FileStatus;
  sheetCount: number;
  filePath: string;
  pdfPath?: string;
  relatedParts: string[];
  createdAt: string;
  updatedAt: string;
}

// ECN (Engineering Change Notice)
export interface ECN {
  id: string;
  ecnNumber: string;
  title: string;
  description: string;
  reason: string;
  status: ECNStatus;
  priority: 'low' | 'medium' | 'high' | 'critical';
  affectedItems: AffectedItem[];
  requestedBy: string;
  assignedTo: string;
  createdAt: string;
  dueDate?: string;
  completedAt?: string;
  approvals: Approval[];
}

// Affected Item
export interface AffectedItem {
  partNumber: string;
  description: string;
  type: CADFileType;
  currentRevision: string;
  newRevision: string;
  changeType: 'add' | 'modify' | 'delete';
}

// Approval
export interface Approval {
  role: string;
  approver: string;
  status: 'pending' | 'approved' | 'rejected';
  date?: string;
  comments?: string;
}

// Job
export interface Job {
  id: string;
  name: string;
  type: 'pdf_to_part' | 'batch_export' | 'bom_extract' | 'drawing_update';
  status: JobStatus;
  progress: number;
  filesTotal: number;
  filesProcessed: number;
  currentFile?: string;
  startedAt: string;
  completedAt?: string;
  error?: string;
}

// Project
export interface Project {
  id: string;
  name: string;
  description: string;
  customer?: string;
  dueDate?: string;
  status: 'active' | 'on_hold' | 'completed' | 'archived';
  partsCount: number;
  assembliesCount: number;
  drawingsCount: number;
  createdAt: string;
  updatedAt: string;
}

// System Performance
export interface SystemPerformance {
  ramUsagePercent: number;
  ramUsedGB: number;
  ramTotalGB: number;
  gpuUsagePercent: number;
  gpuMemoryUsedGB: number;
  gpuMemoryTotalGB: number;
  currentTier: PerformanceTier;
  swConnected: boolean;
  swVersion?: string;
  lastRestart?: string;
  restartCount: number;
}
```

#### `constants.ts` - CAD Constants
```typescript
// Performance Tier Thresholds
export const TIER_THRESHOLDS = {
  REDUCED: 60,   // RAM % to switch to REDUCED
  MINIMAL: 75,   // RAM % to switch to MINIMAL
  SURVIVAL: 85,  // RAM % to switch to SURVIVAL
  RESTART: 90,   // RAM % to force restart
};

// Tier Colors
export const TIER_COLORS = {
  FULL: '#3fb950',
  REDUCED: '#d29922',
  MINIMAL: '#f85149',
  SURVIVAL: '#ff0000',
};

// File Status Colors
export const STATUS_COLORS = {
  draft: '#6e7681',
  in_review: '#d29922',
  approved: '#58a6ff',
  released: '#3fb950',
  obsolete: '#f85149',
};

// ECN Status Colors
export const ECN_STATUS_COLORS = {
  draft: '#6e7681',
  pending_review: '#d29922',
  approved: '#3fb950',
  rejected: '#f85149',
  implemented: '#58a6ff',
};

// Job Status Colors
export const JOB_STATUS_COLORS = {
  queued: '#6e7681',
  running: '#58a6ff',
  paused: '#d29922',
  completed: '#3fb950',
  failed: '#f85149',
  cancelled: '#6e7681',
};

// Export Formats
export const EXPORT_FORMATS = {
  parts: ['STEP', 'IGES', 'Parasolid', 'STL', 'DXF'],
  assemblies: ['STEP', 'IGES', 'Parasolid'],
  drawings: ['PDF', 'DXF', 'DWG'],
};

// Default Properties
export const DEFAULT_CUSTOM_PROPERTIES = [
  'Description',
  'Material',
  'Finish',
  'Weight',
  'Vendor',
  'Cost',
];

// SolidWorks File Extensions
export const SW_EXTENSIONS = {
  part: '.sldprt',
  assembly: '.sldasm',
  drawing: '.slddrw',
};
```

---

### 🏗️ Step 4: Integration Points

#### Backend Adapters (Already Exist)
| Adapter | Location | Integration |
|---------|----------|-------------|
| `cad_orchestrator.py` | `agents/cad_agent/` | Main coordinator |
| `performance_manager.py` | `agents/cad_agent/adapters/` | RAM/GPU monitoring |
| `solidworks_settings.py` | `agents/cad_agent/adapters/` | Graphics tiers |
| `job_queue.py` | `agents/cad_agent/adapters/` | Batch processing |
| `flatter_files_adapter.py` | `agents/cad_agent/adapters/` | Drawing search |
| `notification_store.py` | `agents/cad_agent/adapters/` | UI notifications |

#### API Routes to Create
| Route | Method | Purpose |
|-------|--------|---------|
| `/api/cad/status` | GET | SolidWorks connection status |
| `/api/cad/performance` | GET | RAM/GPU/tier status |
| `/api/cad/jobs` | GET/POST | Job queue management |
| `/api/cad/jobs/[id]` | GET/PUT/DELETE | Single job operations |
| `/api/cad/projects` | GET/POST | Project CRUD |
| `/api/cad/parts/search` | GET | Part search |
| `/api/cad/drawings/search` | GET | Flatter Files search proxy |
| `/api/cad/ecn` | GET/POST | ECN management |
| `/api/cad/bom/[assemblyId]` | GET | BOM extraction |

---

### 🏗️ Step 5: Design System Updates

**Location**: `apps/web/src/app/globals.css`

Add CAD-specific CSS variables:
```css
:root {
  /* CAD-specific colors */
  --cad-bg-primary: #0d1117;
  --cad-bg-secondary: #161b22;
  --cad-bg-tertiary: #21262d;
  --cad-bg-elevated: #30363d;
  
  --cad-accent-blue: #58a6ff;
  --cad-accent-green: #3fb950;
  --cad-accent-red: #f85149;
  --cad-accent-yellow: #d29922;
  --cad-accent-purple: #a371f7;
  
  /* Tier colors */
  --tier-full: #3fb950;
  --tier-reduced: #d29922;
  --tier-minimal: #f85149;
  --tier-survival: #ff0000;
  
  /* Status colors */
  --status-draft: #6e7681;
  --status-review: #d29922;
  --status-approved: #58a6ff;
  --status-released: #3fb950;
  --status-obsolete: #f85149;
}
```

---

### 📋 Implementation Checklist

#### Week 1: Foundation
- [ ] Create all route directories (Step 1)
- [ ] Create all component directories (Step 2)
- [ ] Create `types.ts` with CAD types (Step 3)
- [ ] Create `constants.ts` with CAD constants (Step 3)
- [ ] Build `CADHeader.tsx`
- [ ] Build `CADNav.tsx`
- [ ] Build `StatusBar.tsx`
- [ ] Update `globals.css` with CAD variables

#### Week 2: Dashboard
- [ ] Update `/cad/page.tsx` to redirect to `/dashboard`
- [ ] Create `/cad/dashboard/page.tsx`
- [ ] Build `SystemStatus.tsx`
- [ ] Build `JobQueueWidget.tsx`
- [ ] Build `PerformanceWidget.tsx`
- [ ] Build `RecentFiles.tsx`
- [ ] Build `QuickActions.tsx`

#### Week 3: Projects & Parts
- [ ] Create `/cad/projects/` pages
- [ ] Build `ProjectList.tsx`
- [ ] Build `ProjectCard.tsx`
- [ ] Build `ProjectDetail.tsx`
- [ ] Build `ProjectForm.tsx`
- [ ] Create `/cad/parts/` pages
- [ ] Build `PartLibrary.tsx`
- [ ] Build `PartSearch.tsx`
- [ ] Build `PartCard.tsx`
- [ ] Build `PartDetail.tsx`

#### Week 4: Drawings & Assemblies
- [ ] Create `/cad/drawings/` pages
- [ ] Build `DrawingSearch.tsx` (Flatter Files integration)
- [ ] Build `DrawingList.tsx`
- [ ] Build `DrawingDetail.tsx`
- [ ] Build `RevisionHistory.tsx`
- [ ] Create `/cad/assemblies/` pages
- [ ] Build `AssemblyTree.tsx`
- [ ] Build `BOMTable.tsx`
- [ ] Build `BOMExport.tsx`

#### Week 5: ECN & Jobs
- [ ] Create `/cad/ecn/` pages
- [ ] Build `ECNList.tsx`
- [ ] Build `ECNDetail.tsx`
- [ ] Build `ECNForm.tsx`
- [ ] Build `ECNWorkflow.tsx`
- [ ] Create `/cad/jobs/` pages
- [ ] Build `JobQueue.tsx`
- [ ] Build `JobDetail.tsx`
- [ ] Build `JobHistory.tsx`
- [ ] Build `BatchUpload.tsx`

#### Week 6: Performance & Exports
- [ ] Create `/cad/performance/page.tsx`
- [ ] Build `PerformanceDashboard.tsx`
- [ ] Build `RAMGauge.tsx`
- [ ] Build `GPUGauge.tsx`
- [ ] Build `TierIndicator.tsx`
- [ ] Create `/cad/exports/` pages
- [ ] Build `DriveExport.tsx`
- [ ] Build `FlatterFilesUpload.tsx`

#### Week 7: API & Integration
- [ ] Create all API routes
- [ ] Connect to Desktop Server
- [ ] Integrate with existing adapters
- [ ] Real-time status updates (WebSocket)
- [ ] Testing & polish

---

### 📚 Reference Software for CAD UI

| Software | Use For |
|----------|---------|
| SOLIDWORKS PDM 2025 | Workflow states, BOM visualization |
| Teamcenter | PLM-style data management |
| Onshape | Modern cloud CAD UI patterns |
| OpenBOM | BOM/catalog management |
| Zel X (Siemens) | Lightweight PLM dashboard |
