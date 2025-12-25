"""
Configuration Manager - COM Adapter
Manages configurations for SolidWorks and Inventor parts/assemblies.

Priority 1 API - Configuration Management (0% coverage)
Enables:
- "List all configurations"
- "Switch to the steel configuration"
- "Create configs for 2-inch, 4-inch, 6-inch sizes"
"""

import logging
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("com.configuration")

router = APIRouter(prefix="/com/configuration", tags=["Configuration"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ConfigurationInfo(BaseModel):
    """Configuration information."""
    name: str
    is_active: bool
    description: Optional[str] = None
    properties: Dict[str, Any] = {}


class CreateConfigRequest(BaseModel):
    """Request to create a new configuration."""
    name: str
    description: Optional[str] = None
    base_config: Optional[str] = None  # Copy from this config
    properties: Dict[str, Any] = {}


class ActivateConfigRequest(BaseModel):
    """Request to activate a configuration."""
    name: str


class RenameConfigRequest(BaseModel):
    """Request to rename a configuration."""
    old_name: str
    new_name: str


class DeleteConfigRequest(BaseModel):
    """Request to delete a configuration."""
    name: str


# ============================================================================
# SOLIDWORKS CONFIGURATION MANAGER
# ============================================================================

class SolidWorksConfigManager:
    """Manage SolidWorks configurations."""
    
    def __init__(self, sw_app=None):
        self.app = sw_app
        
    def list_configurations(self) -> List[ConfigurationInfo]:
        """List all configurations in active document."""
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        configs = []
        config_mgr = model.ConfigurationManager
        active_config_name = config_mgr.ActiveConfiguration.Name
        
        config_names = model.GetConfigurationNames()
        if not config_names:
            return []
        
        for name in config_names:
            config = model.GetConfigurationByName(name)
            if config:
                configs.append(ConfigurationInfo(
                    name=name,
                    is_active=(name == active_config_name),
                    description=config.Description or "",
                    properties={}
                ))
        
        return configs
    
    def activate_configuration(self, name: str) -> bool:
        """Activate a configuration."""
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Show the configuration
        success = model.ShowConfiguration2(name)
        if not success:
            raise ValueError(f"Failed to activate configuration: {name}")
        
        logger.info(f"Activated configuration: {name}")
        return True
    
    def create_configuration(
        self, 
        name: str, 
        description: str = "", 
        base_config: Optional[str] = None
    ) -> bool:
        """Create a new configuration."""
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # If base config specified, use it as parent
        if base_config:
            # First show the base config
            model.ShowConfiguration2(base_config)
        
        # Create new configuration
        config_mgr = model.ConfigurationManager
        new_config = config_mgr.AddConfiguration(
            name,  # Name
            description,  # Description/Comment
            "",  # Alternate name
            0  # Options (0 = default)
        )
        
        if not new_config:
            raise ValueError(f"Failed to create configuration: {name}")
        
        logger.info(f"Created configuration: {name}")
        return True
    
    def delete_configuration(self, name: str) -> bool:
        """Delete a configuration."""
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Cannot delete the last configuration
        config_names = model.GetConfigurationNames()
        if len(config_names) <= 1:
            raise ValueError("Cannot delete the last configuration")
        
        # Cannot delete active configuration - switch first
        config_mgr = model.ConfigurationManager
        if config_mgr.ActiveConfiguration.Name == name:
            # Switch to first different config
            for config_name in config_names:
                if config_name != name:
                    model.ShowConfiguration2(config_name)
                    break
        
        # Delete
        success = model.DeleteConfiguration2(name)
        if not success:
            raise ValueError(f"Failed to delete configuration: {name}")
        
        logger.info(f"Deleted configuration: {name}")
        return True
    
    def rename_configuration(self, old_name: str, new_name: str) -> bool:
        """Rename a configuration."""
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        config = model.GetConfigurationByName(old_name)
        if not config:
            raise ValueError(f"Configuration not found: {old_name}")
        
        config.Name = new_name
        logger.info(f"Renamed configuration: {old_name} -> {new_name}")
        return True


# ============================================================================
# INVENTOR CONFIGURATION MANAGER (iLogic/iProperties)
# ============================================================================

class InventorConfigManager:
    """
    Manage Inventor configurations.
    
    Note: Inventor doesn't have native "configurations" like SolidWorks.
    This uses iLogic or iPart factories for similar functionality.
    """
    
    def __init__(self, inv_app=None):
        self.app = inv_app
    
    def list_configurations(self) -> List[ConfigurationInfo]:
        """
        List configurations (iPart members if iPart factory).
        """
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        configs = []
        
        # Check if this is an iPart factory
        if hasattr(doc, 'ComponentDefinition'):
            comp_def = doc.ComponentDefinition
            if hasattr(comp_def, 'iPartFactory'):
                factory = comp_def.iPartFactory
                if factory:
                    # List iPart members
                    for i in range(1, factory.TableRows.Count + 1):
                        row = factory.TableRows.Item(i)
                        member_name = row.Item(1).Value  # First column is usually name
                        configs.append(ConfigurationInfo(
                            name=member_name,
                            is_active=(i == factory.DefaultRow),
                            description=f"iPart member {i}",
                            properties={}
                        ))
                    return configs
        
        # If not iPart, return current state as single "config"
        configs.append(ConfigurationInfo(
            name="Default",
            is_active=True,
            description="Default configuration",
            properties={}
        ))
        
        return configs
    
    def activate_configuration(self, name: str) -> bool:
        """
        Activate configuration (change iPart member if iPart).
        """
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        # For iPart, change the active member
        if hasattr(doc, 'ComponentDefinition'):
            comp_def = doc.ComponentDefinition
            if hasattr(comp_def, 'iPartFactory'):
                factory = comp_def.iPartFactory
                if factory:
                    # Find member by name
                    for i in range(1, factory.TableRows.Count + 1):
                        row = factory.TableRows.Item(i)
                        member_name = row.Item(1).Value
                        if member_name == name:
                            factory.DefaultRow = i
                            logger.info(f"Activated iPart member: {name}")
                            return True
                    raise ValueError(f"iPart member not found: {name}")
        
        logger.warning("Not an iPart - cannot change configuration")
        return False
    
    def create_configuration(
        self, 
        name: str, 
        description: str = "", 
        base_config: Optional[str] = None
    ) -> bool:
        """
        Create configuration (add iPart member if iPart factory).
        """
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        logger.warning("Creating configurations in Inventor requires iPart factory - not implemented")
        raise NotImplementedError("Configuration creation not supported for Inventor (use iPart factory)")
    
    def delete_configuration(self, name: str) -> bool:
        """Delete configuration (remove iPart member)."""
        logger.warning("Deleting configurations in Inventor requires iPart factory - not implemented")
        raise NotImplementedError("Configuration deletion not supported for Inventor")
    
    def rename_configuration(self, old_name: str, new_name: str) -> bool:
        """Rename configuration."""
        logger.warning("Renaming configurations in Inventor requires iPart factory - not implemented")
        raise NotImplementedError("Configuration rename not supported for Inventor")


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

# Global instances (set by server)
_sw_manager: Optional[SolidWorksConfigManager] = None
_inv_manager: Optional[InventorConfigManager] = None


def set_solidworks_app(sw_app):
    """Set SolidWorks application instance."""
    global _sw_manager
    _sw_manager = SolidWorksConfigManager(sw_app)


def set_inventor_app(inv_app):
    """Set Inventor application instance."""
    global _inv_manager
    _inv_manager = InventorConfigManager(inv_app)


@router.get("/list")
async def list_configurations(cad_system: str = "solidworks"):
    """
    List all configurations in active document.
    
    Args:
        cad_system: "solidworks" or "inventor"
    
    Returns:
        List of configuration info
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_manager:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            configs = _sw_manager.list_configurations()
        else:
            if not _inv_manager:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            configs = _inv_manager.list_configurations()
        
        return {
            "success": True,
            "configurations": [c.dict() for c in configs],
            "count": len(configs)
        }
    except Exception as e:
        logger.error(f"List configurations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/activate")
async def activate_configuration(request: ActivateConfigRequest, cad_system: str = "solidworks"):
    """
    Activate a configuration.
    
    Args:
        request: Configuration name to activate
        cad_system: "solidworks" or "inventor"
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_manager:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            success = _sw_manager.activate_configuration(request.name)
        else:
            if not _inv_manager:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            success = _inv_manager.activate_configuration(request.name)
        
        return {
            "success": success,
            "message": f"Activated configuration: {request.name}"
        }
    except Exception as e:
        logger.error(f"Activate configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_configuration(request: CreateConfigRequest, cad_system: str = "solidworks"):
    """
    Create a new configuration.
    
    Args:
        request: Configuration creation details
        cad_system: "solidworks" or "inventor"
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_manager:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            success = _sw_manager.create_configuration(
                request.name,
                request.description or "",
                request.base_config
            )
        else:
            if not _inv_manager:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            success = _inv_manager.create_configuration(
                request.name,
                request.description or "",
                request.base_config
            )
        
        return {
            "success": success,
            "message": f"Created configuration: {request.name}"
        }
    except Exception as e:
        logger.error(f"Create configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_configuration(request: DeleteConfigRequest, cad_system: str = "solidworks"):
    """Delete a configuration."""
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_manager:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            success = _sw_manager.delete_configuration(request.name)
        else:
            if not _inv_manager:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            success = _inv_manager.delete_configuration(request.name)
        
        return {
            "success": success,
            "message": f"Deleted configuration: {request.name}"
        }
    except Exception as e:
        logger.error(f"Delete configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rename")
async def rename_configuration(request: RenameConfigRequest, cad_system: str = "solidworks"):
    """Rename a configuration."""
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_manager:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            success = _sw_manager.rename_configuration(request.old_name, request.new_name)
        else:
            if not _inv_manager:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            success = _inv_manager.rename_configuration(request.old_name, request.new_name)
        
        return {
            "success": success,
            "message": f"Renamed configuration: {request.old_name} -> {request.new_name}"
        }
    except Exception as e:
        logger.error(f"Rename configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
