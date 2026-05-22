"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('profile_picture', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('role', sa.String(20), nullable=False, default='student'),
        sa.Column('google_id', sa.String(255), nullable=True),
        sa.Column('oauth_provider', sa.String(50), nullable=True),
        sa.Column('exam_target', sa.String(20), nullable=False, default='upsc'),
        sa.Column('daily_study_hours', sa.Integer(), nullable=False, default=8),
        sa.Column('exam_year', sa.Integer(), nullable=True),
        sa.Column('current_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('longest_streak', sa.Integer(), nullable=False, default=0),
        sa.Column('total_study_hours', sa.Integer(), nullable=False, default=0),
        sa.Column('reset_token', sa.String(255), nullable=True),
        sa.Column('reset_token_expires', sa.String(255), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)

    # Subjects table
    op.create_table(
        'subjects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('color', sa.String(7), nullable=False, default='#6366f1'),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('total_topics', sa.Integer(), nullable=False, default=0),
        sa.Column('completed_topics', sa.Integer(), nullable=False, default=0),
        sa.Column('completion_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_subjects_user_id', 'subjects', ['user_id'])

    # Topics table
    op.create_table(
        'topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, default='not_started'),
        sa.Column('importance_score', sa.Integer(), nullable=False, default=5),
        sa.Column('priority', sa.String(20), nullable=False, default='medium'),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False, default=[]),
        sa.Column('study_time_minutes', sa.Integer(), nullable=False, default=0),
        sa.Column('revision_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_studied_at', sa.String(50), nullable=True),
        sa.Column('confidence_level', sa.Integer(), nullable=False, default=0),
        sa.Column('pyq_frequency', sa.Integer(), nullable=False, default=0),
        sa.Column('last_asked_year', sa.Integer(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('key_concepts', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('embedding_id', sa.String(255), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['topics.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_topics_subject_id', 'topics', ['subject_id'])


def downgrade() -> None:
    op.drop_table('topics')
    op.drop_table('subjects')
    op.drop_table('users')
