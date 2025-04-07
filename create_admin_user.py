"""create admin user

Revision ID: abcdef123456
Revises: previous_revision_id
Create Date: 2023-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean, Enum
import enum

# revision identifiers, used by Alembic.
revision = 'abcdef123456'
down_revision = None
branch_labels = None
depends_on = None

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    DELIVERY_AGENT = "delivery_agent"

def upgrade():
    # Define table for direct operations
    users = table(
        'users',
        column('id', Integer),
        column('mobile', String),
        column('name', String),
        column('email', String),
        column('role', Enum(UserRole)),
        column('is_active', Boolean),
        column('is_verified', Boolean)
        column('is_profile_complete', Boolean),
    )
    
    # Upsert admin user
    op.execute(
        """
        INSERT INTO users (mobile, name, email, role, is_active, is_verified)
        VALUES ('1234567890', 'Admin User', 'admin@example.com', 'admin', TRUE, TRUE, TRUE)
        ON CONFLICT (mobile) 
        DO UPDATE SET 
            name = EXCLUDED.name,
            email = EXCLUDED.email,
            role = EXCLUDED.role,
            is_active = EXCLUDED.is_active,
            is_verified = EXCLUDED.is_verified
            is_profile_complete = EXCLUDED.is_profile_complete
        """
    )

def downgrade():
    # If needed, remove the admin user
    op.execute("DELETE FROM users WHERE mobile = '1234567890'")
