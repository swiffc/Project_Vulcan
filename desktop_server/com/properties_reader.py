"""
Custom Properties Reader - COM Adapter
Read and list custom properties from CAD files.

Priority 1 API - Custom Properties (14% coverage - can SET but not GET/LIST)
Enables:
- "List all custom properties"
- "Get the material property"
- "Show me all BOM data"
"""

import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("com.properties_reader")

router = APIRouter(prefix="/com/properties", tags=["Custom Properties"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CustomProperty(BaseModel):
    """Custom property information."""
    name: str
    value: str
    type: str  # "Text", "Number", "Date", "Yes or No"
    expression: Optional[str] = None  # Formula if any


class PropertyListResponse(BaseModel):
    """Response with list of properties."""
    properties: List[CustomProperty]
    count: int
    configuration: Optional[str] = None


# ============================================================================
# SOLIDWORKS PROPERTIES READER
# ============================================================================

class SolidWorksPropertiesReader:
    """Read custom properties from SolidWorks files."""
    
    def __init__(self, sw_app=None):
        self.app = sw_app
    
    def list_custom_properties(self, configuration: Optional[str] = None) -> List[CustomProperty]:
        """
        List all custom properties.
        
        Args:
            configuration: Configuration name (None for file-level properties)
        
        Returns:
            List of custom properties
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Get custom property manager
        if configuration:
            # Configuration-specific properties
            config = model.GetConfigurationByName(configuration)
            if not config:
                raise ValueError(f"Configuration not found: {configuration}")
            cust_prop_mgr = config.CustomPropertyManager
        else:
            # File-level properties
            ext = model.Extension
            cust_prop_mgr = ext.CustomPropertyManager("")
        
        if not cust_prop_mgr:
            return []
        
        # Get all property names
        prop_names = cust_prop_mgr.GetNames()
        if not prop_names:
            return []
        
        properties = []
        
        for name in prop_names:
            # Get property value and type
            val_out = [""]
            resolved_val = [""]
            was_resolved = [False]
            link_to_prop = [False]
            
            prop_type = cust_prop_mgr.Get5(
                name,
                False,  # UseCached
                val_out,  # Value
                resolved_val,  # ResolvedValue
                was_resolved,  # WasResolved
                link_to_prop  # LinkToProperty
            )
            
            # Convert type code to string
            type_map = {
                0: "Text",
                1: "Number",
                2: "Date",
                3: "Yes or No"
            }
            type_str = type_map.get(prop_type, "Unknown")
            
            # Get value (use resolved value if available)
            value = resolved_val[0] if resolved_val[0] else val_out[0]
            expression = val_out[0] if val_out[0] != resolved_val[0] else None
            
            properties.append(CustomProperty(
                name=name,
                value=value or "",
                type=type_str,
                expression=expression
            ))
        
        return properties
    
    def get_custom_property(self, name: str, configuration: Optional[str] = None) -> Optional[CustomProperty]:
        """
        Get a specific custom property.
        
        Args:
            name: Property name
            configuration: Configuration name (None for file-level)
        
        Returns:
            CustomProperty or None if not found
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Get custom property manager
        if configuration:
            config = model.GetConfigurationByName(configuration)
            if not config:
                raise ValueError(f"Configuration not found: {configuration}")
            cust_prop_mgr = config.CustomPropertyManager
        else:
            ext = model.Extension
            cust_prop_mgr = ext.CustomPropertyManager("")
        
        if not cust_prop_mgr:
            return None
        
        # Get property
        val_out = [""]
        resolved_val = [""]
        was_resolved = [False]
        link_to_prop = [False]
        
        prop_type = cust_prop_mgr.Get5(
            name,
            False,
            val_out,
            resolved_val,
            was_resolved,
            link_to_prop
        )
        
        # If property doesn't exist, Get5 returns 0 and empty values
        if not val_out[0] and not resolved_val[0]:
            return None
        
        type_map = {
            0: "Text",
            1: "Number",
            2: "Date",
            3: "Yes or No"
        }
        type_str = type_map.get(prop_type, "Unknown")
        
        value = resolved_val[0] if resolved_val[0] else val_out[0]
        expression = val_out[0] if val_out[0] != resolved_val[0] else None
        
        return CustomProperty(
            name=name,
            value=value or "",
            type=type_str,
            expression=expression
        )
    
    def get_summary_information(self) -> Dict[str, str]:
        """
        Get summary information (author, title, subject, etc.).
        These are the built-in document properties.
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Get summary info
        summary = {}
        
        try:
            # Get model doc extension
            ext = model.Extension
            
            # Summary info property IDs
            # These are standard Windows file properties
            summary_props = {
                "Author": 4,  # swSummInfoAuthor
                "Title": 2,   # swSummInfoTitle
                "Subject": 3,  # swSummInfoSubject
                "Keywords": 5,  # swSummInfoKeywords
                "Comments": 6,  # swSummInfoComment
                "SavedBy": 7,  # swSummInfoSavedBy
                "CreatedDate": 11,  # swSummInfoCreateDate
                "SavedDate": 12,  # swSummInfoSaveDate
            }
            
            for prop_name, prop_id in summary_props.items():
                try:
                    value = ext.GetSummaryInformation(prop_id)
                    if value:
                        summary[prop_name] = str(value)
                except:
                    pass
        except Exception as e:
            logger.warning(f"Failed to get summary info: {e}")
        
        return summary


# ============================================================================
# INVENTOR PROPERTIES READER
# ============================================================================

class InventorPropertiesReader:
    """Read custom properties from Inventor files."""
    
    def __init__(self, inv_app=None):
        self.app = inv_app
    
    def list_custom_properties(self, configuration: Optional[str] = None) -> List[CustomProperty]:
        """List all iProperties."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        properties = []
        
        try:
            # Get property sets
            prop_sets = doc.PropertySets
            
            # Common property sets to check
            set_names = [
                "Inventor Summary Information",
                "Inventor User Defined Properties",
                "Design Tracking Properties",
                "Inventor Document Summary Information"
            ]
            
            for set_name in set_names:
                try:
                    prop_set = prop_sets.Item(set_name)
                    
                    # Iterate through properties in this set
                    for i in range(1, prop_set.Count + 1):
                        prop = prop_set.Item(i)
                        
                        # Get property info
                        name = prop.Name
                        value = str(prop.Value) if prop.Value is not None else ""
                        
                        # Type detection (simplified)
                        prop_type = "Text"
                        if isinstance(prop.Value, (int, float)):
                            prop_type = "Number"
                        elif isinstance(prop.Value, bool):
                            prop_type = "Yes or No"
                        
                        properties.append(CustomProperty(
                            name=f"{set_name}/{name}",
                            value=value,
                            type=prop_type
                        ))
                except:
                    # Property set might not exist
                    continue
        
        except Exception as e:
            logger.error(f"Failed to list Inventor properties: {e}")
        
        return properties
    
    def get_custom_property(self, name: str, configuration: Optional[str] = None) -> Optional[CustomProperty]:
        """Get a specific iProperty."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        try:
            # Try to find property in user-defined properties first
            prop_sets = doc.PropertySets
            prop_set = prop_sets.Item("Inventor User Defined Properties")
            
            try:
                prop = prop_set.Item(name)
                value = str(prop.Value) if prop.Value is not None else ""
                
                prop_type = "Text"
                if isinstance(prop.Value, (int, float)):
                    prop_type = "Number"
                elif isinstance(prop.Value, bool):
                    prop_type = "Yes or No"
                
                return CustomProperty(
                    name=name,
                    value=value,
                    type=prop_type
                )
            except:
                # Try other property sets
                for set_name in ["Inventor Summary Information", "Design Tracking Properties"]:
                    try:
                        prop_set = prop_sets.Item(set_name)
                        prop = prop_set.Item(name)
                        value = str(prop.Value) if prop.Value is not None else ""
                        
                        return CustomProperty(
                            name=name,
                            value=value,
                            type="Text"
                        )
                    except:
                        continue
        
        except Exception as e:
            logger.error(f"Failed to get Inventor property: {e}")
        
        return None
    
    def get_summary_information(self) -> Dict[str, str]:
        """Get summary information from Inventor document."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        summary = {}
        
        try:
            prop_sets = doc.PropertySets
            sum_info = prop_sets.Item("Inventor Summary Information")
            
            common_props = ["Title", "Subject", "Author", "Keywords", "Comments"]
            
            for prop_name in common_props:
                try:
                    prop = sum_info.Item(prop_name)
                    value = str(prop.Value) if prop.Value is not None else ""
                    if value:
                        summary[prop_name] = value
                except:
                    pass
        
        except Exception as e:
            logger.warning(f"Failed to get Inventor summary info: {e}")
        
        return summary


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

_sw_props: Optional[SolidWorksPropertiesReader] = None
_inv_props: Optional[InventorPropertiesReader] = None


def set_solidworks_app(sw_app):
    """Set SolidWorks application instance."""
    global _sw_props
    _sw_props = SolidWorksPropertiesReader(sw_app)


def set_inventor_app(inv_app):
    """Set Inventor application instance."""
    global _inv_props
    _inv_props = InventorPropertiesReader(inv_app)


@router.get("/list")
async def list_custom_properties(
    cad_system: str = "solidworks",
    configuration: Optional[str] = None
):
    """
    List all custom properties.
    
    Args:
        cad_system: "solidworks" or "inventor"
        configuration: Configuration name (SolidWorks only, None for file-level)
    
    Returns:
        List of all custom properties
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_props:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            properties = _sw_props.list_custom_properties(configuration)
        else:
            if not _inv_props:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            properties = _inv_props.list_custom_properties(configuration)
        
        return {
            "success": True,
            "properties": [p.dict() for p in properties],
            "count": len(properties),
            "configuration": configuration
        }
    except Exception as e:
        logger.error(f"List properties failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{property_name}")
async def get_custom_property(
    property_name: str,
    cad_system: str = "solidworks",
    configuration: Optional[str] = None
):
    """
    Get a specific custom property.
    
    Args:
        property_name: Name of the property
        cad_system: "solidworks" or "inventor"
        configuration: Configuration name (SolidWorks only)
    
    Returns:
        Property value or 404 if not found
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_props:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            prop = _sw_props.get_custom_property(property_name, configuration)
        else:
            if not _inv_props:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            prop = _inv_props.get_custom_property(property_name, configuration)
        
        if not prop:
            raise HTTPException(
                status_code=404,
                detail=f"Property not found: {property_name}"
            )
        
        return {
            "success": True,
            "property": prop.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get property failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_summary_information(cad_system: str = "solidworks"):
    """
    Get document summary information (author, title, etc.).
    
    Args:
        cad_system: "solidworks" or "inventor"
    
    Returns:
        Dictionary of summary properties
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_props:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            summary = _sw_props.get_summary_information()
        else:
            if not _inv_props:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            summary = _inv_props.get_summary_information()
        
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Get summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
