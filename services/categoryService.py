import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from models.Category import Category

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_categories(self) -> List[Category]:
        """Obtiene todas las categorías"""
        try:
            return self.db.query(Category).order_by(Category.name).all()
        except Exception as e:
            logger.error(f"Error al obtener categorías: {str(e)}")
            return []

    def get_active_categories(self) -> List[Category]:
        """Obtiene las categorías activas"""
        try:
            return self.db.query(Category).filter(Category.active == True).order_by(Category.name).all()
        except Exception as e:
            logger.error(f"Error al obtener categorías activas: {str(e)}")
            return []

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Obtiene una categoría por su ID"""
        try:
            return self.db.query(Category).filter(Category.id == category_id).first()
        except Exception as e:
            logger.error(f"Error al obtener categoría por ID: {str(e)}")
            return None

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Obtiene una categoría por su nombre"""
        try:
            return self.db.query(Category).filter(Category.name == name).first()
        except Exception as e:
            logger.error(f"Error al obtener categoría por nombre: {str(e)}")
            return None

    def create_category(self, category_data: dict) -> Optional[Category]:
        """Crea una nueva categoría"""
        try:
            # Verificar si ya existe una categoría con el mismo nombre
            existing_category = self.get_category_by_name(category_data["name"])
            if existing_category:
                logger.warning(f"Ya existe una categoría con el nombre '{category_data['name']}'")
                return None

            # Crear la nueva categoría
            category = Category(
                name=category_data["name"],
                description=category_data.get("description", ""),
                active=category_data.get("active", True)
            )
            
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            
            logger.info(f"Categoría creada: {category.name} (ID: {category.id})")
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear categoría: {str(e)}")
            return None

    def update_category(self, category_id: int, category_data: dict) -> Optional[Category]:
        """Actualiza una categoría existente"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                logger.warning(f"No se encontró la categoría con ID {category_id}")
                return None

            # Verificar si el nuevo nombre ya está en uso por otra categoría
            if "name" in category_data and category_data["name"] != category.name:
                existing_category = self.get_category_by_name(category_data["name"])
                if existing_category and existing_category.id != category_id:
                    logger.warning(f"Ya existe una categoría con el nombre '{category_data['name']}'")
                    return None

            # Actualizar los campos
            if "name" in category_data:
                category.name = category_data["name"]
            if "description" in category_data:
                category.description = category_data["description"]
            if "active" in category_data:
                category.active = category_data["active"]

            self.db.commit()
            self.db.refresh(category)
            
            logger.info(f"Categoría actualizada: {category.name} (ID: {category.id})")
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar categoría: {str(e)}")
            return None

    def delete_category(self, category_id: int) -> bool:
        """Elimina una categoría"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                logger.warning(f"No se encontró la categoría con ID {category_id}")
                return False

            self.db.delete(category)
            self.db.commit()
            
            logger.info(f"Categoría eliminada: {category.name} (ID: {category.id})")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar categoría: {str(e)}")
            return False

    def toggle_category_status(self, category_id: int) -> Optional[Category]:
        """Activa o desactiva una categoría"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                logger.warning(f"No se encontró la categoría con ID {category_id}")
                return None

            # Cambiar el estado
            category.active = not category.active
            
            self.db.commit()
            self.db.refresh(category)
            
            status = "activada" if category.active else "desactivada"
            logger.info(f"Categoría {status}: {category.name} (ID: {category.id})")
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al cambiar estado de categoría: {str(e)}")
            return None 