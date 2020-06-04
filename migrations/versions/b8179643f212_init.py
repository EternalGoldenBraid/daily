"""init

Revision ID: 5b64ace08c6e
 OLD Revision ID: b8179643f212
Revises: 
Create Date: 2020-05-31 08:51:06.176982

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b64ace08c6e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('buffer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('event_tag', sa.String(length=16), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_buffer_event_tag'), 'buffer', ['event_tag'], unique=False)
    op.create_index(op.f('ix_buffer_user_id'), 'buffer', ['user_id'], unique=False)
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('rating_date', sa.DateTime(), nullable=False),
    sa.Column('story', sa.String(length=500), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_rating_date'), 'event', ['rating_date'], unique=False)
    op.create_index(op.f('ix_event_story'), 'event', ['story'], unique=False)
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag_name', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tag_tag_name'), 'tag', ['tag_name'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('event_tags',
    sa.Column('event.id', sa.Integer(), nullable=True),
    sa.Column('tag.id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event.id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['tag.id'], ['event.id'], )
    )
    op.create_table('rating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('rating_sleep', sa.Integer(), nullable=False),
    sa.Column('meditation', sa.Integer(), nullable=False),
    sa.Column('cw', sa.Integer(), nullable=False),
    sa.Column('screen', sa.Integer(), nullable=False),
    sa.Column('rating_day', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_index(op.f('ix_rating_rating_sleep'), 'rating', ['rating_sleep'], unique=False)
    op.create_index(op.f('ix_rating_user_id'), 'rating', ['user_id'], unique=False)
    op.create_table('rating_events',
    sa.Column('rating_id', sa.Integer(), nullable=True),
    sa.Column('event.id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event.id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['rating_id'], ['rating.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rating_events')
    op.drop_index(op.f('ix_rating_user_id'), table_name='rating')
    op.drop_index(op.f('ix_rating_rating_sleep'), table_name='rating')
    op.drop_table('rating')
    op.drop_table('event_tags')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_tag_tag_name'), table_name='tag')
    op.drop_table('tag')
    op.drop_index(op.f('ix_event_story'), table_name='event')
    op.drop_index(op.f('ix_event_rating_date'), table_name='event')
    op.drop_table('event')
    op.drop_index(op.f('ix_buffer_user_id'), table_name='buffer')
    op.drop_index(op.f('ix_buffer_event_tag'), table_name='buffer')
    op.drop_table('buffer')
    # ### end Alembic commands ###
