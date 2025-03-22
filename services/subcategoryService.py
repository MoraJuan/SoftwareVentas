import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from models.Category import Category
from models.Subcategory import Subcategory

logger = logging.getLogger(__name__)

class SubcategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_subcategories(self) -> List[Subcategory]:
        """Obtiene todas las subcategorías."""
        try:
            return self.db.query(Subcategory).order_by(Subcategory.name).all()
        except Exception as e:
            logger.error(f"Error al obtener subcategorías: {str(e)}")
            return []
    
    def get_active_subcategories(self,category_id: int = None) -> List[Subcategory]:
        """Obtiene las subcategorías activas"""
        try:
            if category_id:
                return self.db.query(Subcategory).filter(Subcategory.active == True, Subcategory.category_id == category_id).order_by(Subcategory.name).all()
            else:
                return self.db.query(Subcategory).filter(Subcategory.active == True).order_by(Subcategory.name).all()
        except Exception as e:
            logger.error(f"Error al obtener subcategorías activas: {str(e)}")
            return []

    def get_subcategories_by_category(self, category_id: int) -> List[Subcategory]:
        """Obtiene todas las subcategorías de una categoría específica."""
        try:
            return self.db.query(Subcategory).filter(Subcategory.category_id == category_id).all()
        except Exception as e:
            logger.error(f"Error al obtener subcategorías de la categoría {category_id}: {str(e)}")
            return []

    def get_subcategory_by_id(self, subcategory_id: int) -> Optional[Subcategory]:
        """Obtiene una subcategoría por su ID."""
        try:
            return self.db.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
        except Exception as e:
            logger.error(f"Error al obtener subcategoría por ID: {str(e)}")
            return None

    def create_subcategory(self, category_id: int, subcategory_data: dict) -> Optional[Subcategory]:
        """Crea una nueva subcategoría dentro de una categoría existente."""
        try:
            category = self.db.query(Category).filter(Category.id == category_id).first()
            if not category:
                logger.warning(f"No se encontró la categoría con ID {category_id}")
                return None
            
            # Verificar si ya existe una subcategoría con el mismo nombre en la categoría
            existing_subcategory = self.db.query(Subcategory).filter(
                Subcategory.name == subcategory_data["name"],
                Subcategory.category_id == category_id
            ).first()
            
            if existing_subcategory:
                logger.warning(f"Ya existe una subcategoría con el nombre '{subcategory_data['name']}' en la categoría {category_id}")
                return None
            
            subcategory = Subcategory(
                name=subcategory_data["name"],
                description=subcategory_data.get("description", ""),
                active=subcategory_data.get("active", True),
                category_id=category_id
            )
            
            self.db.add(subcategory)
            self.db.commit()
            self.db.refresh(subcategory)
            
            logger.info(f"Subcategoría creada: {subcategory.name} (ID: {subcategory.id}, Categoría: {category_id})")
            return subcategory
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear subcategoría: {str(e)}")
            return None

    def update_subcategory(self, subcategory_id: int, subcategory_data: dict) -> Optional[Subcategory]:
        """Actualiza una subcategoría existente."""
        try:
            subcategory = self.get_subcategory_by_id(subcategory_id)
            if not subcategory:
                logger.warning(f"No se encontró la subcategoría con ID {subcategory_id}")
                return None

            if "name" in subcategory_data:
                subcategory.name = subcategory_data["name"]
                
            if "description" in subcategory_data:
                subcategory.description = subcategory_data["description"]
                
            if "active" in subcategory_data:
                subcategory.active = subcategory_data["active"]

            self.db.commit()
            self.db.refresh(subcategory)
            
            logger.info(f"Subcategoría actualizada: {subcategory.name} (ID: {subcategory.id})")
            return subcategory
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar subcategoría: {str(e)}")
            return None

    def delete_subcategory(self, subcategory_id: int) -> bool:
        """Elimina una subcategoría."""
        try:
            subcategory = self.get_subcategory_by_id(subcategory_id)
            if not subcategory:
                logger.warning(f"No se encontró la subcategoría con ID {subcategory_id}")
                return False

            self.db.delete(subcategory)
            self.db.commit()
            
            logger.info(f"Subcategoría eliminada: {subcategory.name} (ID: {subcategory.id})")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar subcategoría: {str(e)}")
            return False
