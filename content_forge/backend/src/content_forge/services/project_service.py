"""Project management service."""

import logging
from typing import Dict, List, Optional

from ..models.project import Project, ProjectInput, ProjectUpdate
from ..models.common import PaginatedResponse
from ..utils.dynamodb import DynamoDBClient, model_to_dynamodb_item, dynamodb_item_to_model

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for managing projects."""
    
    def __init__(self, dynamodb_client: DynamoDBClient):
        """Initialize project service."""
        self.db = dynamodb_client
    
    def create_project(self, user_id: str, project_input: ProjectInput) -> Optional[Project]:
        """Create a new project."""
        try:
            project = Project(
                user_id=user_id,
                name=project_input.name,
                niche=project_input.niche,
                target_audience=project_input.target_audience
            )
            
            # Set DynamoDB keys
            project.pk = f"USER#{user_id}"
            project.sk = f"PROJECT#{project.id}"
            project.gsi1pk = f"PROJECT#{project.id}"
            project.gsi1sk = "METADATA"
            
            # Convert to DynamoDB item and save
            item = model_to_dynamodb_item(project)
            success = self.db.put_item(item)
            
            if success:
                logger.info(f"Created project {project.id} for user {user_id}")
                return project
            else:
                logger.error(f"Failed to create project for user {user_id}")
                return None
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
    
    def get_project(self, user_id: str, project_id: str) -> Optional[Project]:
        """Get a specific project."""
        try:
            item = self.db.get_item(f"USER#{user_id}", f"PROJECT#{project_id}")
            if item:
                return dynamodb_item_to_model(item, Project)
            return None
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            return None
    
    def list_projects(
        self, 
        user_id: str, 
        limit: int = 20,
        next_token: Optional[str] = None
    ) -> PaginatedResponse:
        """List projects for a user."""
        try:
            result = self.db.query_items(
                pk=f"USER#{user_id}",
                sk_prefix="PROJECT#",
                limit=limit,
                next_token=next_token
            )
            
            projects = []
            for item in result['items']:
                project = dynamodb_item_to_model(item, Project)
                if project and project.status != "deleted":
                    projects.append(project)
            
            return PaginatedResponse(
                items=projects,
                next_token=result['next_token']
            )
        except Exception as e:
            logger.error(f"Error listing projects for user {user_id}: {e}")
            return PaginatedResponse(items=[], next_token=None)
    
    def update_project(
        self, 
        user_id: str, 
        project_id: str, 
        project_update: ProjectUpdate
    ) -> Optional[Project]:
        """Update a project."""
        try:
            # Get existing project
            project = self.get_project(user_id, project_id)
            if not project:
                return None
            
            # Update fields
            update_data = project_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(project, field, value)
            
            # Update timestamp
            project.updated_at = datetime.utcnow()
            
            # Build update expression
            update_expression = "SET "
            expression_values = {}
            expression_names = {}
            
            for i, (field, value) in enumerate(update_data.items()):
                if i > 0:
                    update_expression += ", "
                update_expression += f"#field{i} = :value{i}"
                expression_names[f"#field{i}"] = field
                expression_values[f":value{i}"] = value
            
            update_expression += ", #updated_at = :updated_at"
            expression_names["#updated_at"] = "updated_at"
            expression_values[":updated_at"] = project.updated_at.isoformat()
            
            # Update in DynamoDB
            success = self.db.update_item(
                pk=f"USER#{user_id}",
                sk=f"PROJECT#{project_id}",
                update_expression=update_expression,
                expression_values=expression_values,
                expression_names=expression_names
            )
            
            if success:
                logger.info(f"Updated project {project_id} for user {user_id}")
                return project
            else:
                logger.error(f"Failed to update project {project_id}")
                return None
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            return None
    
    def delete_project(self, user_id: str, project_id: str) -> bool:
        """Delete a project (soft delete)."""
        try:
            # Soft delete by updating status
            success = self.db.update_item(
                pk=f"USER#{user_id}",
                sk=f"PROJECT#{project_id}",
                update_expression="SET #status = :status, #updated_at = :updated_at",
                expression_values={
                    ":status": "deleted",
                    ":updated_at": datetime.utcnow().isoformat()
                },
                expression_names={
                    "#status": "status",
                    "#updated_at": "updated_at"
                }
            )
            
            if success:
                logger.info(f"Deleted project {project_id} for user {user_id}")
                return True
            else:
                logger.error(f"Failed to delete project {project_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False
